"""
Production-ready Rate-Limited API Client with Circuit Breaker Pattern

This module provides a robust API client with rate limiting, retry logic,
circuit breaker pattern, and comprehensive error handling.
"""

import asyncio
import time
import logging
import json
from typing import Dict, Any, Optional, Union, List, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque, defaultdict
import aiohttp
from aiohttp import ClientSession, ClientError, ClientTimeout
import random
from functools import wraps
import statistics

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

T = TypeVar('T')


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class RequestMetrics:
    """Container for request metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limited_requests: int = 0
    circuit_breaker_trips: int = 0
    latencies: List[float] = field(default_factory=list)
    
    def add_latency(self, latency: float) -> None:
        """Add a latency measurement"""
        self.latencies.append(latency)
        # Keep only last 1000 measurements to prevent memory growth
        if len(self.latencies) > 1000:
            self.latencies.pop(0)
    
    def get_percentile(self, percentile: float) -> Optional[float]:
        """Get latency percentile"""
        if not self.latencies:
            return None
        return statistics.quantiles(self.latencies, n=100)[int(percentile)]
    
    def to_dict(self) -> Dict[str, Any]:
        """Export metrics as dictionary"""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "rate_limited_requests": self.rate_limited_requests,
            "circuit_breaker_trips": self.circuit_breaker_trips,
            "success_rate": self.successful_requests / max(1, self.total_requests),
            "latency_p50": self.get_percentile(50),
            "latency_p95": self.get_percentile(95),
            "latency_p99": self.get_percentile(99),
        }


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5
    recovery_timeout: timedelta = timedelta(seconds=60)
    half_open_requests: int = 3


class TokenBucket:
    """Token bucket implementation for rate limiting"""
    
    def __init__(self, rate: float, capacity: float):
        """
        Initialize token bucket
        
        Args:
            rate: Tokens added per second
            capacity: Maximum tokens in bucket
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens from bucket
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            True if tokens acquired, False otherwise
        """
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            self.last_update = now
            
            # Add new tokens based on elapsed time
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    async def wait_for_token(self, tokens: int = 1) -> None:
        """Wait until tokens are available"""
        while not await self.acquire(tokens):
            # Calculate wait time for next token
            wait_time = (tokens - self.tokens) / self.rate
            await asyncio.sleep(min(wait_time, 0.1))


class CircuitBreaker:
    """Circuit breaker implementation"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_requests = 0
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection"""
        async with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.half_open_requests = 0
                else:
                    raise Exception("Circuit breaker is OPEN")
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                if self.half_open_requests >= self.config.half_open_requests:
                    raise Exception("Circuit breaker is testing recovery")
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise
    
    async def _on_success(self) -> None:
        """Handle successful request"""
        async with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.half_open_requests += 1
                if self.half_open_requests >= self.config.half_open_requests:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                    logger.info("Circuit breaker closed after recovery")
            else:
                self.failure_count = 0
    
    async def _on_failure(self) -> None:
        """Handle failed request"""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.OPEN
                logger.warning("Circuit breaker reopened during recovery test")
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time >= self.config.recovery_timeout
        )


class RateLimitedAPIClient:
    """
    Production-ready API client with rate limiting, retry logic, and circuit breaker
    
    Features:
    - Configurable rate limiting using token bucket algorithm
    - Exponential backoff retry logic with jitter
    - Circuit breaker pattern for fault tolerance
    - Comprehensive metrics collection
    - Async request handling with queuing
    - Support for GET and POST methods
    """
    
    def __init__(
        self,
        base_url: str,
        rate_limit: int = 100,
        rate_window: int = 60,
        max_retries: int = 3,
        timeout: int = 30,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
        max_queue_size: int = 1000
    ):
        """
        Initialize the API client
        
        Args:
            base_url: Base URL for API endpoints
            rate_limit: Maximum requests per rate window
            rate_window: Time window in seconds for rate limiting
            max_retries: Maximum retry attempts
            timeout: Request timeout in seconds
            circuit_breaker_config: Circuit breaker configuration
            max_queue_size: Maximum size of request queue
        """
        self.base_url = base_url.rstrip('/')
        self.max_retries = max_retries
        self.timeout = ClientTimeout(total=timeout)
        self.max_queue_size = max_queue_size
        
        # Initialize rate limiter
        self.rate_limiter = TokenBucket(
            rate=rate_limit / rate_window,
            capacity=rate_limit
        )
        
        # Initialize circuit breaker
        self.circuit_breaker = CircuitBreaker(
            circuit_breaker_config or CircuitBreakerConfig()
        )
        
        # Request queue
        self.request_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        
        # Metrics
        self.metrics = RequestMetrics()
        
        # Session management
        self._session: Optional[ClientSession] = None
        self._session_lock = asyncio.Lock()
        
        # Start request processor
        self._processor_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def start(self) -> None:
        """Start the client and request processor"""
        self._running = True
        self._processor_task = asyncio.create_task(self._process_requests())
        logger.info("RateLimitedAPIClient started")
    
    async def close(self) -> None:
        """Close the client and cleanup resources"""
        self._running = False
        
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        
        if self._session:
            await self._session.close()
        
        logger.info("RateLimitedAPIClient closed")
    
    async def _get_session(self) -> ClientSession:
        """Get or create aiohttp session"""
        if self._session is None:
            async with self._session_lock:
                if self._session is None:
                    self._session = ClientSession(
                        timeout=self.timeout,
                        connector=aiohttp.TCPConnector(limit=100)
                    )
        return self._session
    
    async def _process_requests(self) -> None:
        """Process requests from queue"""
        while self._running:
            try:
                # Get request from queue with timeout
                request_data = await asyncio.wait_for(
                    self.request_queue.get(),
                    timeout=1.0
                )
                
                # Wait for rate limit token
                await self.rate_limiter.wait_for_token()
                
                # Process request
                asyncio.create_task(self._execute_request(request_data))
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing request: {e}")
    
    async def _execute_request(self, request_data: Dict[str, Any]) -> None:
        """Execute a single request with retries and circuit breaker"""
        method = request_data['method']
        url = request_data['url']
        future = request_data['future']
        kwargs = request_data.get('kwargs', {})
        
        try:
            result = await self.circuit_breaker.call(
                self._make_request_with_retry,
                method, url, **kwargs
            )
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)
    
    async def _make_request_with_retry(
        self, method: str, url: str, **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        session = await self._get_session()
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                start_time = time.monotonic()
                
                async with session.request(method, url, **kwargs) as response:
                    latency = time.monotonic() - start_time
                    self.metrics.add_latency(latency)
                    self.metrics.total_requests += 1
                    
                    # Handle rate limit responses
                    if response.status == 429:
                        self.metrics.rate_limited_requests += 1
                        retry_after = int(response.headers.get('Retry-After', 60))
                        await asyncio.sleep(retry_after)
                        continue
                    
                    # Handle error responses
                    if response.status >= 400:
                        self.metrics.failed_requests += 1
                        response.raise_for_status()
                    
                    # Success
                    self.metrics.successful_requests += 1
                    return {
                        'status': response.status,
                        'headers': dict(response.headers),
                        'data': await response.json() if response.content_type == 'application/json' else await response.text()
                    }
                    
            except (ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                self.metrics.failed_requests += 1
                
                # Calculate backoff with jitter
                backoff = min(2 ** attempt + random.uniform(0, 1), 30)
                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}. "
                    f"Retrying in {backoff:.2f}s"
                )
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(backoff)
                
            except Exception as e:
                self.metrics.failed_requests += 1
                logger.error(f"Unexpected error: {e}")
                raise
        
        # All retries exhausted
        raise last_exception or Exception("All retry attempts failed")
    
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make GET request
        
        Args:
            endpoint: API endpoint (relative to base_url)
            **kwargs: Additional arguments passed to aiohttp
            
        Returns:
            Response data
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return await self._enqueue_request('GET', url, **kwargs)
    
    async def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make POST request
        
        Args:
            endpoint: API endpoint (relative to base_url)
            **kwargs: Additional arguments passed to aiohttp
            
        Returns:
            Response data
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return await self._enqueue_request('POST', url, **kwargs)
    
    async def _enqueue_request(
        self, method: str, url: str, **kwargs
    ) -> Dict[str, Any]:
        """Enqueue request for processing"""
        if not self._running:
            raise RuntimeError("Client is not running. Call start() first.")
        
        future = asyncio.Future()
        request_data = {
            'method': method,
            'url': url,
            'kwargs': kwargs,
            'future': future
        }
        
        try:
            await self.request_queue.put(request_data)
        except asyncio.QueueFull:
            raise RuntimeError(f"Request queue is full (max size: {self.max_queue_size})")
        
        return await future
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        metrics = self.metrics.to_dict()
        metrics['circuit_breaker_state'] = self.circuit_breaker.state.value
        metrics['queue_size'] = self.request_queue.qsize()
        return metrics
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        return {
            'status': 'healthy' if self._running else 'stopped',
            'circuit_breaker': self.circuit_breaker.state.value,
            'queue_size': self.request_queue.qsize(),
            'metrics': self.get_metrics()
        }