"""
Rate-Limited API Client with Circuit Breaker and Exponential Backoff

A production-ready async API client with comprehensive rate limiting,
error handling, and resilience patterns.
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
from enum import Enum
import aiohttp
from functools import wraps
import json


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class RequestMetrics:
    """Metrics for tracking request performance"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limited_requests: int = 0
    circuit_breaker_trips: int = 0
    total_latency: float = 0.0
    request_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    def add_request(self, success: bool, latency: float, rate_limited: bool = False):
        """Record a request in metrics"""
        self.total_requests += 1
        self.total_latency += latency
        self.request_times.append((time.time(), latency))
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            
        if rate_limited:
            self.rate_limited_requests += 1
    
    def get_average_latency(self) -> float:
        """Calculate average latency"""
        if self.total_requests == 0:
            return 0.0
        return self.total_latency / self.total_requests
    
    def get_success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    requests_per_minute: int = 100
    burst_size: int = 10
    queue_size: int = 1000


@dataclass
class RetryConfig:
    """Configuration for retry logic"""
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    half_open_max_calls: int = 3


class RateLimitedAPIClient:
    """
    Asynchronous API client with rate limiting, circuit breaker, and retry logic.
    
    Features:
    - Token bucket rate limiting with burst support
    - Exponential backoff retry with jitter
    - Circuit breaker pattern for fault tolerance
    - Request queuing with overflow handling
    - Comprehensive metrics and logging
    - Support for GET and POST methods
    - Proper error handling and timeout management
    """
    
    def __init__(
        self,
        base_url: str,
        rate_limit_config: Optional[RateLimitConfig] = None,
        retry_config: Optional[RetryConfig] = None,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
        timeout: float = 30.0,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for API requests
            rate_limit_config: Rate limiting configuration
            retry_config: Retry logic configuration
            circuit_breaker_config: Circuit breaker configuration
            timeout: Request timeout in seconds
            logger: Logger instance (creates default if not provided)
        """
        self.base_url = base_url.rstrip('/')
        self.rate_limit_config = rate_limit_config or RateLimitConfig()
        self.retry_config = retry_config or RetryConfig()
        self.circuit_breaker_config = circuit_breaker_config or CircuitBreakerConfig()
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.logger = logger or logging.getLogger(__name__)
        
        # Rate limiting state
        self.tokens = float(self.rate_limit_config.burst_size)
        self.last_refill = time.time()
        self.request_queue: asyncio.Queue = asyncio.Queue(maxsize=self.rate_limit_config.queue_size)
        
        # Circuit breaker state
        self.circuit_state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.circuit_opened_at: Optional[float] = None
        self.half_open_calls = 0
        
        # Metrics
        self.metrics = RequestMetrics()
        
        # Session management
        self._session: Optional[aiohttp.ClientSession] = None
        self._rate_limiter_task: Optional[asyncio.Task] = None
        
        # Locks for thread safety
        self._token_lock = asyncio.Lock()
        self._circuit_lock = asyncio.Lock()
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def start(self):
        """Start the client and background tasks"""
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
            self._rate_limiter_task = asyncio.create_task(self._rate_limiter_loop())
            self.logger.info("API client started")
    
    async def close(self):
        """Close the client and cleanup resources"""
        if self._rate_limiter_task:
            self._rate_limiter_task.cancel()
            try:
                await self._rate_limiter_task
            except asyncio.CancelledError:
                pass
        
        if self._session:
            await self._session.close()
            self._session = None
            
        self.logger.info("API client closed")
    
    async def _rate_limiter_loop(self):
        """Background task to refill rate limit tokens"""
        while True:
            try:
                await asyncio.sleep(1.0)  # Check every second
                async with self._token_lock:
                    now = time.time()
                    elapsed = now - self.last_refill
                    
                    # Calculate tokens to add based on configured rate
                    tokens_to_add = elapsed * (self.rate_limit_config.requests_per_minute / 60.0)
                    self.tokens = min(
                        self.tokens + tokens_to_add,
                        self.rate_limit_config.burst_size
                    )
                    self.last_refill = now
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in rate limiter loop: {e}")
    
    async def _acquire_token(self) -> bool:
        """Try to acquire a rate limit token"""
        async with self._token_lock:
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return True
            return False
    
    async def _check_circuit_breaker(self) -> bool:
        """Check if circuit breaker allows the request"""
        async with self._circuit_lock:
            if self.circuit_state == CircuitState.CLOSED:
                return True
            
            if self.circuit_state == CircuitState.OPEN:
                # Check if recovery timeout has passed
                if self.circuit_opened_at and \
                   time.time() - self.circuit_opened_at >= self.circuit_breaker_config.recovery_timeout:
                    self.circuit_state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                    self.logger.info("Circuit breaker moved to HALF_OPEN state")
                else:
                    return False
            
            if self.circuit_state == CircuitState.HALF_OPEN:
                if self.half_open_calls < self.circuit_breaker_config.half_open_max_calls:
                    self.half_open_calls += 1
                    return True
                return False
            
            return False
    
    async def _record_success(self):
        """Record a successful request for circuit breaker"""
        async with self._circuit_lock:
            self.consecutive_failures = 0
            
            if self.circuit_state == CircuitState.HALF_OPEN:
                # If all half-open calls succeed, close the circuit
                if self.half_open_calls >= self.circuit_breaker_config.half_open_max_calls:
                    self.circuit_state = CircuitState.CLOSED
                    self.logger.info("Circuit breaker closed after successful recovery")
    
    async def _record_failure(self):
        """Record a failed request for circuit breaker"""
        async with self._circuit_lock:
            self.consecutive_failures += 1
            
            if self.consecutive_failures >= self.circuit_breaker_config.failure_threshold:
                if self.circuit_state != CircuitState.OPEN:
                    self.circuit_state = CircuitState.OPEN
                    self.circuit_opened_at = time.time()
                    self.metrics.circuit_breaker_trips += 1
                    self.logger.warning(
                        f"Circuit breaker opened after {self.consecutive_failures} consecutive failures"
                    )
            
            if self.circuit_state == CircuitState.HALF_OPEN:
                # Failed during half-open, reopen the circuit
                self.circuit_state = CircuitState.OPEN
                self.circuit_opened_at = time.time()
                self.logger.warning("Circuit breaker reopened after failure in HALF_OPEN state")
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate delay for exponential backoff with optional jitter"""
        delay = min(
            self.retry_config.initial_delay * (self.retry_config.exponential_base ** attempt),
            self.retry_config.max_delay
        )
        
        if self.retry_config.jitter:
            # Add random jitter (±25% of delay)
            import random
            jitter = delay * 0.25 * (2 * random.random() - 1)
            delay += jitter
            
        return max(0, delay)
    
    async def _execute_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Union[Dict[str, Any], bytes]:
        """Execute a single HTTP request with error handling"""
        if not self._session:
            raise RuntimeError("Client not started. Use 'async with' or call start() first.")
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = time.time()
        
        try:
            async with self._session.request(method, url, **kwargs) as response:
                latency = time.time() - start_time
                
                if response.status >= 500:
                    # Server error, should retry
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status
                    )
                
                response.raise_for_status()
                
                # Try to parse JSON, fallback to bytes
                try:
                    data = await response.json()
                except (json.JSONDecodeError, aiohttp.ContentTypeError):
                    data = await response.read()
                
                self.metrics.add_request(success=True, latency=latency)
                await self._record_success()
                
                return data
                
        except asyncio.TimeoutError:
            latency = time.time() - start_time
            self.metrics.add_request(success=False, latency=latency)
            await self._record_failure()
            self.logger.error(f"Request timeout for {method} {url}")
            raise
            
        except aiohttp.ClientError as e:
            latency = time.time() - start_time
            self.metrics.add_request(success=False, latency=latency)
            await self._record_failure()
            self.logger.error(f"Client error for {method} {url}: {e}")
            raise
            
        except Exception as e:
            latency = time.time() - start_time
            self.metrics.add_request(success=False, latency=latency)
            await self._record_failure()
            self.logger.error(f"Unexpected error for {method} {url}: {e}")
            raise
    
    async def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Union[Dict[str, Any], bytes]:
        """Execute request with retry logic"""
        last_exception = None
        
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                # Check circuit breaker
                if not await self._check_circuit_breaker():
                    raise Exception("Circuit breaker is open")
                
                # Execute request
                return await self._execute_request(method, endpoint, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                # Don't retry for client errors (4xx)
                if isinstance(e, aiohttp.ClientResponseError) and 400 <= e.status < 500:
                    raise
                
                # Don't retry if circuit is open
                if self.circuit_state == CircuitState.OPEN:
                    raise
                
                # Last attempt, don't retry
                if attempt >= self.retry_config.max_retries:
                    raise
                
                # Calculate retry delay
                delay = self._calculate_retry_delay(attempt)
                self.logger.warning(
                    f"Request failed (attempt {attempt + 1}/{self.retry_config.max_retries + 1}), "
                    f"retrying in {delay:.2f}s: {e}"
                )
                await asyncio.sleep(delay)
        
        raise last_exception
    
    async def request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Union[Dict[str, Any], bytes]:
        """
        Execute an API request with rate limiting, retry, and circuit breaker.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (relative to base_url)
            **kwargs: Additional arguments for aiohttp request
            
        Returns:
            Response data (dict if JSON, bytes otherwise)
            
        Raises:
            asyncio.QueueFull: If request queue is full
            aiohttp.ClientError: For network errors
            Exception: For other errors
        """
        # Queue the request
        request_data = {
            'method': method,
            'endpoint': endpoint,
            'kwargs': kwargs,
            'future': asyncio.Future()
        }
        
        try:
            self.request_queue.put_nowait(request_data)
        except asyncio.QueueFull:
            self.logger.error("Request queue is full")
            raise
        
        # Wait for rate limiter to process the request
        while not await self._acquire_token():
            await asyncio.sleep(0.1)
            self.metrics.rate_limited_requests += 1
        
        # Execute the request
        try:
            result = await self._request_with_retry(method, endpoint, **kwargs)
            request_data['future'].set_result(result)
            return result
        except Exception as e:
            request_data['future'].set_exception(e)
            raise
    
    async def get(self, endpoint: str, **kwargs) -> Union[Dict[str, Any], bytes]:
        """
        Execute a GET request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments (params, headers, etc.)
            
        Returns:
            Response data
        """
        return await self.request('GET', endpoint, **kwargs)
    
    async def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        **kwargs
    ) -> Union[Dict[str, Any], bytes]:
        """
        Execute a POST request.
        
        Args:
            endpoint: API endpoint
            json: JSON data to send
            data: Form data to send
            **kwargs: Additional arguments
            
        Returns:
            Response data
        """
        if json is not None:
            kwargs['json'] = json
        if data is not None:
            kwargs['data'] = data
            
        return await self.request('POST', endpoint, **kwargs)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            'total_requests': self.metrics.total_requests,
            'successful_requests': self.metrics.successful_requests,
            'failed_requests': self.metrics.failed_requests,
            'rate_limited_requests': self.metrics.rate_limited_requests,
            'circuit_breaker_trips': self.metrics.circuit_breaker_trips,
            'average_latency': self.metrics.get_average_latency(),
            'success_rate': self.metrics.get_success_rate(),
            'circuit_state': self.circuit_state.value,
            'available_tokens': self.tokens,
            'queue_size': self.request_queue.qsize()
        }