"""
Production-ready Rate-Limited API Client with Circuit Breaker Pattern
Research Division - 20-Agent Maximum Stress Test Implementation

This implementation demonstrates advanced async patterns, comprehensive error handling,
and enterprise-grade reliability features.
"""

import asyncio
import aiohttp
import logging
import time
from typing import Optional, Dict, Any, Callable, List, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import json
import hashlib
from contextlib import asynccontextmanager
import weakref


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class RequestMethod(Enum):
    """Supported HTTP methods"""
    GET = "GET"
    POST = "POST"


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    max_requests: int = 100
    window_seconds: int = 60
    burst_limit: int = 10
    queue_timeout: float = 30.0


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    success_threshold: int = 3
    half_open_max_requests: int = 5


@dataclass
class RetryConfig:
    """Retry configuration"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    jitter: bool = True


@dataclass
class RequestMetrics:
    """Request metrics tracking"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limited_requests: int = 0
    circuit_breaker_opens: int = 0
    retry_count: int = 0
    average_response_time: float = 0.0
    response_times: deque = field(default_factory=lambda: deque(maxlen=1000))


@dataclass
class QueuedRequest:
    """Queued request representation"""
    method: RequestMethod
    url: str
    headers: Optional[Dict[str, str]] = None
    json_data: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, Any]] = None
    future: Optional[asyncio.Future] = None
    priority: int = 0
    created_at: float = field(default_factory=time.time)


class RateLimitedAPIClient:
    """
    Production-ready rate-limited API client with circuit breaker pattern.
    
    Features:
    - Configurable rate limiting with token bucket algorithm
    - Exponential backoff retry logic with jitter
    - Circuit breaker pattern for fault tolerance
    - Request queuing with priority support
    - Comprehensive metrics and logging
    - Concurrent request handling with asyncio
    - Memory-efficient request tracking
    """

    def __init__(
        self,
        base_url: str = "",
        rate_limit: RateLimitConfig = None,
        circuit_breaker: CircuitBreakerConfig = None,
        retry_config: RetryConfig = None,
        session: Optional[aiohttp.ClientSession] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the rate-limited API client.
        
        Args:
            base_url: Base URL for all requests
            rate_limit: Rate limiting configuration
            circuit_breaker: Circuit breaker configuration
            retry_config: Retry configuration
            session: Optional aiohttp session
            logger: Optional logger instance
        """
        self.base_url = base_url.rstrip('/')
        self.rate_limit = rate_limit or RateLimitConfig()
        self.circuit_breaker = circuit_breaker or CircuitBreakerConfig()
        self.retry_config = retry_config or RetryConfig()
        
        # Session management
        self._session = session
        self._session_owned = session is None
        
        # Circuit breaker state
        self._circuit_state = CircuitState.CLOSED
        self._circuit_failure_count = 0
        self._circuit_last_failure_time = 0.0
        self._circuit_half_open_requests = 0
        
        # Rate limiting - token bucket algorithm
        self._tokens = float(self.rate_limit.max_requests)
        self._last_token_update = time.time()
        self._rate_limit_lock = asyncio.Lock()
        
        # Request queue
        self._request_queue = asyncio.PriorityQueue()
        self._queue_processors: List[asyncio.Task] = []
        self._processing_active = False
        
        # Metrics
        self.metrics = RequestMetrics()
        
        # Logging
        self.logger = logger or logging.getLogger(__name__)
        
        # Cleanup tracking
        self._cleanup_refs = weakref.WeakSet()
        
        # Start background tasks
        self._start_background_tasks()

    async def __aenter__(self):
        """Async context manager entry"""
        if self._session is None:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=30,
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={'User-Agent': 'RateLimitedAPIClient/1.0'}
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    def _start_background_tasks(self):
        """Start background processing tasks"""
        if not self._processing_active:
            self._processing_active = True
            # Start multiple queue processors for better throughput
            for i in range(3):
                task = asyncio.create_task(self._process_request_queue())
                self._queue_processors.append(task)
                self._cleanup_refs.add(task)

    async def _process_request_queue(self):
        """Background task to process queued requests"""
        while self._processing_active:
            try:
                # Get request from queue with timeout
                priority, request = await asyncio.wait_for(
                    self._request_queue.get(), 
                    timeout=1.0
                )
                
                # Check if request has timed out
                if time.time() - request.created_at > self.rate_limit.queue_timeout:
                    if request.future and not request.future.done():
                        request.future.set_exception(
                            asyncio.TimeoutError("Request timed out in queue")
                        )
                    continue
                
                # Process the request
                try:
                    response = await self._execute_request(request)
                    if request.future and not request.future.done():
                        request.future.set_result(response)
                except Exception as e:
                    if request.future and not request.future.done():
                        request.future.set_exception(e)
                
                # Mark task as done
                self._request_queue.task_done()
                
            except asyncio.TimeoutError:
                # No requests in queue, continue
                continue
            except Exception as e:
                self.logger.error(f"Error processing request queue: {e}")
                await asyncio.sleep(0.1)

    async def _wait_for_rate_limit(self) -> bool:
        """
        Wait for rate limit using token bucket algorithm.
        
        Returns:
            bool: True if token acquired, False if circuit breaker is open
        """
        if self._circuit_state == CircuitState.OPEN:
            return await self._check_circuit_breaker()
        
        async with self._rate_limit_lock:
            now = time.time()
            
            # Refill tokens based on time elapsed
            time_elapsed = now - self._last_token_update
            tokens_to_add = time_elapsed * (self.rate_limit.max_requests / self.rate_limit.window_seconds)
            self._tokens = min(self.rate_limit.max_requests, self._tokens + tokens_to_add)
            self._last_token_update = now
            
            # Check if we have tokens available
            if self._tokens >= 1.0:
                self._tokens -= 1.0
                return True
            
            # No tokens available, calculate wait time
            wait_time = (1.0 - self._tokens) / (self.rate_limit.max_requests / self.rate_limit.window_seconds)
            await asyncio.sleep(min(wait_time, self.rate_limit.queue_timeout))
            
            return False

    async def _check_circuit_breaker(self) -> bool:
        """
        Check and update circuit breaker state.
        
        Returns:
            bool: True if request should proceed, False if circuit is open
        """
        now = time.time()
        
        if self._circuit_state == CircuitState.OPEN:
            if now - self._circuit_last_failure_time >= self.circuit_breaker.recovery_timeout:
                self._circuit_state = CircuitState.HALF_OPEN
                self._circuit_half_open_requests = 0
                self.logger.info("Circuit breaker transitioning to HALF_OPEN")
                return True
            return False
        
        elif self._circuit_state == CircuitState.HALF_OPEN:
            if self._circuit_half_open_requests >= self.circuit_breaker.half_open_max_requests:
                return False
            self._circuit_half_open_requests += 1
            return True
        
        return True  # CLOSED state

    def _record_success(self):
        """Record successful request"""
        self.metrics.successful_requests += 1
        
        if self._circuit_state == CircuitState.HALF_OPEN:
            if self._circuit_half_open_requests >= self.circuit_breaker.success_threshold:
                self._circuit_state = CircuitState.CLOSED
                self._circuit_failure_count = 0
                self.logger.info("Circuit breaker closed after successful recovery")

    def _record_failure(self, exception: Exception):
        """Record failed request"""
        self.metrics.failed_requests += 1
        self._circuit_failure_count += 1
        
        if self._circuit_failure_count >= self.circuit_breaker.failure_threshold:
            self._circuit_state = CircuitState.OPEN
            self._circuit_last_failure_time = time.time()
            self.metrics.circuit_breaker_opens += 1
            self.logger.warning(f"Circuit breaker opened after {self._circuit_failure_count} failures")

    async def _execute_request(self, request: QueuedRequest) -> aiohttp.ClientResponse:
        """
        Execute a single request with retry logic.
        
        Args:
            request: The request to execute
            
        Returns:
            aiohttp.ClientResponse: The response
        """
        last_exception = None
        
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                # Wait for rate limit
                if not await self._wait_for_rate_limit():
                    raise Exception("Rate limit exceeded and circuit breaker is open")
                
                # Record attempt
                self.metrics.total_requests += 1
                start_time = time.time()
                
                # Ensure session is available
                if self._session is None:
                    raise RuntimeError("Session not initialized. Use async context manager.")
                
                # Build URL
                url = f"{self.base_url}/{request.url.lstrip('/')}" if self.base_url else request.url
                
                # Execute request
                async with self._session.request(
                    request.method.value,
                    url,
                    headers=request.headers,
                    json=request.json_data,
                    params=request.params
                ) as response:
                    # Record response time
                    response_time = time.time() - start_time
                    self.metrics.response_times.append(response_time)
                    
                    # Update average response time
                    if self.metrics.response_times:
                        self.metrics.average_response_time = sum(self.metrics.response_times) / len(self.metrics.response_times)
                    
                    # Check for HTTP errors
                    if response.status >= 400:
                        error_text = await response.text()
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=f"HTTP {response.status}: {error_text}"
                        )
                    
                    # Success
                    self._record_success()
                    return response
                    
            except Exception as e:
                last_exception = e
                self.logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                
                # Don't retry on certain errors
                if isinstance(e, (aiohttp.ClientResponseError,)) and e.status < 500:
                    break
                
                # Calculate backoff delay
                if attempt < self.retry_config.max_retries:
                    delay = min(
                        self.retry_config.base_delay * (self.retry_config.backoff_factor ** attempt),
                        self.retry_config.max_delay
                    )
                    
                    # Add jitter
                    if self.retry_config.jitter:
                        import random
                        delay *= (0.5 + random.random() * 0.5)
                    
                    self.metrics.retry_count += 1
                    await asyncio.sleep(delay)
        
        # All retries failed
        self._record_failure(last_exception)
        raise last_exception

    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        priority: int = 0
    ) -> aiohttp.ClientResponse:
        """
        Perform GET request.
        
        Args:
            url: Request URL
            headers: Optional headers
            params: Optional query parameters
            priority: Request priority (higher = more priority)
            
        Returns:
            aiohttp.ClientResponse: The response
        """
        return await self._queue_request(
            RequestMethod.GET,
            url,
            headers=headers,
            params=params,
            priority=priority
        )

    async def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        priority: int = 0
    ) -> aiohttp.ClientResponse:
        """
        Perform POST request.
        
        Args:
            url: Request URL
            headers: Optional headers
            json_data: Optional JSON data
            params: Optional query parameters
            priority: Request priority (higher = more priority)
            
        Returns:
            aiohttp.ClientResponse: The response
        """
        return await self._queue_request(
            RequestMethod.POST,
            url,
            headers=headers,
            json_data=json_data,
            params=params,
            priority=priority
        )

    async def _queue_request(
        self,
        method: RequestMethod,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        priority: int = 0
    ) -> aiohttp.ClientResponse:
        """
        Queue a request for processing.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Optional headers
            json_data: Optional JSON data
            params: Optional query parameters
            priority: Request priority
            
        Returns:
            aiohttp.ClientResponse: The response
        """
        # Create request
        request = QueuedRequest(
            method=method,
            url=url,
            headers=headers,
            json_data=json_data,
            params=params,
            future=asyncio.get_event_loop().create_future(),
            priority=priority
        )
        
        # Queue request (negative priority for min-heap to work as max-heap)
        await self._request_queue.put((-priority, request))
        
        # Wait for result
        return await request.future

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics.
        
        Returns:
            Dict[str, Any]: Current metrics
        """
        return {
            'total_requests': self.metrics.total_requests,
            'successful_requests': self.metrics.successful_requests,
            'failed_requests': self.metrics.failed_requests,
            'rate_limited_requests': self.metrics.rate_limited_requests,
            'circuit_breaker_opens': self.metrics.circuit_breaker_opens,
            'retry_count': self.metrics.retry_count,
            'average_response_time': self.metrics.average_response_time,
            'success_rate': (
                self.metrics.successful_requests / max(1, self.metrics.total_requests) * 100
            ),
            'circuit_breaker_state': self._circuit_state.value,
            'current_tokens': self._tokens,
            'queue_size': self._request_queue.qsize()
        }

    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = RequestMetrics()

    def reset_circuit_breaker(self):
        """Reset circuit breaker to closed state"""
        self._circuit_state = CircuitState.CLOSED
        self._circuit_failure_count = 0
        self._circuit_last_failure_time = 0.0
        self._circuit_half_open_requests = 0

    async def close(self):
        """Clean up resources"""
        self._processing_active = False
        
        # Cancel background tasks
        for task in self._queue_processors:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        if self._queue_processors:
            await asyncio.gather(*self._queue_processors, return_exceptions=True)
        
        # Close session if owned
        if self._session_owned and self._session:
            await self._session.close()
            self._session = None

    def __del__(self):
        """Cleanup on destruction"""
        if hasattr(self, '_session') and self._session_owned and self._session:
            if not self._session.closed:
                self.logger.warning("Session not properly closed. Use async context manager.")


# Usage example and testing utilities
async def example_usage():
    """Example usage of the RateLimitedAPIClient"""
    
    # Configure rate limiting
    rate_limit = RateLimitConfig(
        max_requests=50,  # 50 requests per minute
        window_seconds=60,
        burst_limit=10,
        queue_timeout=30.0
    )
    
    # Configure circuit breaker
    circuit_breaker = CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=30.0,
        success_threshold=2
    )
    
    # Configure retry logic
    retry_config = RetryConfig(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0,
        backoff_factor=2.0,
        jitter=True
    )
    
    # Create client
    async with RateLimitedAPIClient(
        base_url="https://api.example.com",
        rate_limit=rate_limit,
        circuit_breaker=circuit_breaker,
        retry_config=retry_config
    ) as client:
        
        # Make requests
        try:
            response = await client.get("/users/123")
            print(f"GET Response: {response.status}")
            
            response = await client.post(
                "/users",
                json_data={"name": "John", "email": "john@example.com"}
            )
            print(f"POST Response: {response.status}")
            
        except Exception as e:
            print(f"Request failed: {e}")
        
        # Get metrics
        metrics = client.get_metrics()
        print(f"Metrics: {json.dumps(metrics, indent=2)}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())