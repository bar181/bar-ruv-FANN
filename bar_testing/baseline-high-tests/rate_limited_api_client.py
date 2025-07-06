import asyncio
import time
import logging
from typing import Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import aiohttp
from datetime import datetime, timedelta
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class RequestMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limited_requests: int = 0
    circuit_breaker_rejections: int = 0
    total_response_time: float = 0.0
    
    @property
    def average_response_time(self) -> float:
        if self.successful_requests == 0:
            return 0.0
        return self.total_response_time / self.successful_requests


@dataclass
class RateLimitConfig:
    max_requests: int
    time_window: float  # in seconds
    
    
@dataclass
class RetryConfig:
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0


class RateLimitedAPIClient:
    """
    A production-ready API client with rate limiting, exponential backoff,
    circuit breaker pattern, and comprehensive error handling.
    
    Features:
    - Configurable rate limiting with token bucket algorithm
    - Exponential backoff retry logic
    - Circuit breaker pattern
    - Request queuing
    - Async/await support
    - Detailed metrics and logging
    """
    
    def __init__(
        self,
        base_url: str,
        rate_limit_config: RateLimitConfig,
        retry_config: Optional[RetryConfig] = None,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: float = 60.0,
        timeout: float = 30.0,
        max_queue_size: int = 1000
    ):
        self.base_url = base_url.rstrip('/')
        self.rate_limit_config = rate_limit_config
        self.retry_config = retry_config or RetryConfig()
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_queue_size = max_queue_size
        
        # Rate limiting state
        self.tokens = rate_limit_config.max_requests
        self.last_refill = time.time()
        self.token_lock = asyncio.Lock()
        
        # Circuit breaker state
        self.circuit_state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.circuit_opened_at: Optional[float] = None
        self.circuit_lock = asyncio.Lock()
        
        # Request queue
        self.request_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.queue_processor_task: Optional[asyncio.Task] = None
        
        # Metrics
        self.metrics = RequestMetrics()
        
        # Session management
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    async def start(self):
        """Initialize the client and start background tasks."""
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        if self.queue_processor_task is None:
            self.queue_processor_task = asyncio.create_task(self._process_queue())
            
    async def close(self):
        """Clean up resources."""
        if self.queue_processor_task:
            self.queue_processor_task.cancel()
            try:
                await self.queue_processor_task
            except asyncio.CancelledError:
                pass
                
        if self._session:
            await self._session.close()
            self._session = None
            
    async def _refill_tokens(self):
        """Refill tokens based on elapsed time."""
        async with self.token_lock:
            now = time.time()
            elapsed = now - self.last_refill
            tokens_to_add = int(elapsed / self.rate_limit_config.time_window * 
                               self.rate_limit_config.max_requests)
            
            if tokens_to_add > 0:
                self.tokens = min(
                    self.rate_limit_config.max_requests,
                    self.tokens + tokens_to_add
                )
                self.last_refill = now
                
    async def _acquire_token(self) -> bool:
        """Try to acquire a token for rate limiting."""
        await self._refill_tokens()
        
        async with self.token_lock:
            if self.tokens > 0:
                self.tokens -= 1
                return True
            return False
            
    async def _check_circuit_breaker(self) -> bool:
        """Check if circuit breaker allows the request."""
        async with self.circuit_lock:
            if self.circuit_state == CircuitState.CLOSED:
                return True
                
            if self.circuit_state == CircuitState.OPEN:
                if (time.time() - self.circuit_opened_at) > self.circuit_breaker_timeout:
                    self.circuit_state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker entering HALF_OPEN state")
                    return True
                else:
                    self.metrics.circuit_breaker_rejections += 1
                    return False
                    
            # HALF_OPEN state
            return True
            
    async def _handle_circuit_breaker_success(self):
        """Handle successful request for circuit breaker."""
        async with self.circuit_lock:
            if self.circuit_state == CircuitState.HALF_OPEN:
                self.circuit_state = CircuitState.CLOSED
                logger.info("Circuit breaker CLOSED")
            self.consecutive_failures = 0
            
    async def _handle_circuit_breaker_failure(self):
        """Handle failed request for circuit breaker."""
        async with self.circuit_lock:
            self.consecutive_failures += 1
            
            if self.consecutive_failures >= self.circuit_breaker_threshold:
                self.circuit_state = CircuitState.OPEN
                self.circuit_opened_at = time.time()
                logger.warning(f"Circuit breaker OPENED after {self.consecutive_failures} failures")
                
    async def _execute_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute a single request with retry logic."""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                # Check circuit breaker
                if not await self._check_circuit_breaker():
                    raise Exception("Circuit breaker is OPEN")
                    
                # Acquire rate limit token
                while not await self._acquire_token():
                    self.metrics.rate_limited_requests += 1
                    await asyncio.sleep(0.1)
                    
                # Execute request
                start_time = time.time()
                async with self._session.request(method, url, **kwargs) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 429:  # Rate limited by server
                        retry_after = int(response.headers.get('Retry-After', '60'))
                        logger.warning(f"Server rate limit hit, waiting {retry_after}s")
                        await asyncio.sleep(retry_after)
                        continue
                        
                    response.raise_for_status()
                    
                    # Success
                    self.metrics.total_requests += 1
                    self.metrics.successful_requests += 1
                    self.metrics.total_response_time += response_time
                    
                    await self._handle_circuit_breaker_success()
                    
                    return {
                        'status': response.status,
                        'headers': dict(response.headers),
                        'data': await response.json() if response.content_type == 'application/json' else await response.text()
                    }
                    
            except Exception as e:
                self.metrics.total_requests += 1
                self.metrics.failed_requests += 1
                
                await self._handle_circuit_breaker_failure()
                
                if attempt == self.retry_config.max_retries:
                    logger.error(f"Request failed after {attempt + 1} attempts: {e}")
                    raise
                    
                # Calculate backoff delay
                delay = min(
                    self.retry_config.base_delay * (self.retry_config.exponential_base ** attempt),
                    self.retry_config.max_delay
                )
                
                logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {delay}s: {e}")
                await asyncio.sleep(delay)
                
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Execute GET request."""
        return await self._execute_request('GET', endpoint, **kwargs)
        
    async def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Execute POST request."""
        return await self._execute_request('POST', endpoint, **kwargs)
        
    async def request(
        self,
        method: str,
        endpoint: str,
        priority: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Queue a request for execution.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            priority: Request priority (higher = more important)
            **kwargs: Additional request parameters
            
        Returns:
            Response data
        """
        future = asyncio.Future()
        
        await self.request_queue.put((
            priority,
            future,
            method,
            endpoint,
            kwargs
        ))
        
        return await future
        
    async def _process_queue(self):
        """Process queued requests."""
        while True:
            try:
                # Get highest priority request
                priority, future, method, endpoint, kwargs = await self.request_queue.get()
                
                try:
                    result = await self._execute_request(method, endpoint, **kwargs)
                    future.set_result(result)
                except Exception as e:
                    future.set_exception(e)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Queue processor error: {e}")
                
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return {
            'total_requests': self.metrics.total_requests,
            'successful_requests': self.metrics.successful_requests,
            'failed_requests': self.metrics.failed_requests,
            'rate_limited_requests': self.metrics.rate_limited_requests,
            'circuit_breaker_rejections': self.metrics.circuit_breaker_rejections,
            'average_response_time': self.metrics.average_response_time,
            'circuit_state': self.circuit_state.value,
            'tokens_available': self.tokens,
            'queue_size': self.request_queue.qsize()
        }


# Usage examples
async def example_usage():
    """Demonstrate common usage patterns."""
    
    # Configure rate limiting: 100 requests per minute
    rate_limit = RateLimitConfig(max_requests=100, time_window=60)
    
    # Configure retry logic
    retry_config = RetryConfig(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0,
        exponential_base=2.0
    )
    
    # Create client
    async with RateLimitedAPIClient(
        base_url="https://api.example.com",
        rate_limit_config=rate_limit,
        retry_config=retry_config,
        circuit_breaker_threshold=5,
        circuit_breaker_timeout=60.0
    ) as client:
        
        # Simple GET request
        response = await client.get("/users/123")
        print(f"User data: {response['data']}")
        
        # POST request with data
        response = await client.post(
            "/users",
            json={"name": "John Doe", "email": "john@example.com"}
        )
        print(f"Created user: {response['data']}")
        
        # Concurrent requests with priority queue
        tasks = []
        for i in range(10):
            # Higher priority for important requests
            priority = 10 if i < 3 else 1
            task = client.request(
                'GET',
                f'/users/{i}',
                priority=priority
            )
            tasks.append(task)
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check metrics
        metrics = client.get_metrics()
        print(f"Metrics: {json.dumps(metrics, indent=2)}")


if __name__ == "__main__":
    asyncio.run(example_usage())