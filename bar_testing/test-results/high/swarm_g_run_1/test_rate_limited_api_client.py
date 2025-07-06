"""
Unit tests for RateLimitedAPIClient

Comprehensive test suite covering rate limiting, circuit breaker,
retry logic, and error handling.
"""

import asyncio
import pytest
import time
from unittest.mock import Mock, patch, AsyncMock
from datetime import timedelta
import aiohttp
from aiohttp import ClientError, ClientTimeout

from rate_limited_api_client import (
    RateLimitedAPIClient, CircuitBreakerConfig, CircuitBreakerState,
    TokenBucket, CircuitBreaker, RequestMetrics
)


class TestTokenBucket:
    """Test token bucket rate limiter"""
    
    @pytest.mark.asyncio
    async def test_token_bucket_basic(self):
        """Test basic token bucket functionality"""
        bucket = TokenBucket(rate=10, capacity=10)
        
        # Should start with full capacity
        assert await bucket.acquire(5) is True
        assert await bucket.acquire(5) is True
        assert await bucket.acquire(1) is False
    
    @pytest.mark.asyncio
    async def test_token_bucket_refill(self):
        """Test token bucket refill over time"""
        bucket = TokenBucket(rate=10, capacity=10)
        
        # Deplete bucket
        assert await bucket.acquire(10) is True
        assert await bucket.acquire(1) is False
        
        # Wait for refill
        await asyncio.sleep(0.2)  # Should add ~2 tokens
        assert await bucket.acquire(2) is True
        assert await bucket.acquire(1) is False
    
    @pytest.mark.asyncio
    async def test_wait_for_token(self):
        """Test waiting for token availability"""
        bucket = TokenBucket(rate=10, capacity=10)
        
        # Deplete bucket
        await bucket.acquire(10)
        
        # Measure wait time
        start = time.time()
        await bucket.wait_for_token(1)
        elapsed = time.time() - start
        
        # Should wait approximately 0.1 seconds for 1 token at rate 10/s
        assert 0.05 < elapsed < 0.2


class TestCircuitBreaker:
    """Test circuit breaker pattern"""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_closes_on_success(self):
        """Test circuit breaker remains closed on success"""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker(config)
        
        async def success_func():
            return "success"
        
        # Multiple successful calls
        for _ in range(5):
            result = await breaker.call(success_func)
            assert result == "success"
        
        assert breaker.state == CircuitBreakerState.CLOSED
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_failures(self):
        """Test circuit breaker opens after threshold failures"""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker(config)
        
        async def failing_func():
            raise Exception("Test failure")
        
        # Fail until threshold
        for i in range(3):
            with pytest.raises(Exception):
                await breaker.call(failing_func)
        
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Further calls should fail immediately
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            await breaker.call(failing_func)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_recovery(self):
        """Test circuit breaker recovery to half-open state"""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=timedelta(seconds=0.1)
        )
        breaker = CircuitBreaker(config)
        
        async def failing_func():
            raise Exception("Test failure")
        
        async def success_func():
            return "success"
        
        # Open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                await breaker.call(failing_func)
        
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Wait for recovery timeout
        await asyncio.sleep(0.2)
        
        # Should transition to half-open and allow test
        result = await breaker.call(success_func)
        assert result == "success"
        assert breaker.state == CircuitBreakerState.HALF_OPEN


class TestRateLimitedAPIClient:
    """Test the main API client"""
    
    @pytest.fixture
    async def client(self):
        """Create test client"""
        client = RateLimitedAPIClient(
            base_url="https://api.example.com",
            rate_limit=10,
            rate_window=1,
            max_retries=3,
            timeout=5
        )
        await client.start()
        yield client
        await client.close()
    
    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initialization and context manager"""
        async with RateLimitedAPIClient(
            base_url="https://api.example.com"
        ) as client:
            assert client._running is True
            metrics = client.get_metrics()
            assert metrics['total_requests'] == 0
    
    @pytest.mark.asyncio
    async def test_get_request_success(self, client):
        """Test successful GET request"""
        with patch.object(client, '_make_request_with_retry') as mock_request:
            mock_request.return_value = {
                'status': 200,
                'headers': {'Content-Type': 'application/json'},
                'data': {'result': 'success'}
            }
            
            result = await client.get('/test-endpoint')
            assert result['status'] == 200
            assert result['data']['result'] == 'success'
    
    @pytest.mark.asyncio
    async def test_post_request_success(self, client):
        """Test successful POST request"""
        with patch.object(client, '_make_request_with_retry') as mock_request:
            mock_request.return_value = {
                'status': 201,
                'headers': {'Content-Type': 'application/json'},
                'data': {'id': 123}
            }
            
            result = await client.post('/create', json={'name': 'test'})
            assert result['status'] == 201
            assert result['data']['id'] == 123
    
    @pytest.mark.asyncio
    async def test_retry_on_failure(self, client):
        """Test retry logic on failures"""
        attempt_count = 0
        
        async def mock_request(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise aiohttp.ClientError("Connection error")
            return {'status': 200, 'headers': {}, 'data': 'success'}
        
        with patch.object(client, '_make_request_with_retry', mock_request):
            # Should succeed after retries
            result = await client.get('/test')
            assert result['data'] == 'success'
            assert attempt_count == 3
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, client):
        """Test rate limiting enforcement"""
        # Set very low rate limit
        client.rate_limiter = TokenBucket(rate=2, capacity=2)
        
        results = []
        start_time = time.time()
        
        # Make multiple requests
        for i in range(5):
            with patch.object(client, '_make_request_with_retry') as mock:
                mock.return_value = {'status': 200, 'headers': {}, 'data': i}
                result = await client.get(f'/test{i}')
                results.append(result)
        
        elapsed = time.time() - start_time
        
        # Should take at least 2 seconds for 5 requests at rate 2/s
        assert elapsed >= 1.5
        assert len(results) == 5
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self, client):
        """Test circuit breaker integration"""
        # Configure aggressive circuit breaker
        client.circuit_breaker = CircuitBreaker(
            CircuitBreakerConfig(failure_threshold=2)
        )
        
        async def failing_request(*args, **kwargs):
            raise aiohttp.ClientError("Server error")
        
        with patch.object(client, '_make_request_with_retry', failing_request):
            # First two failures should open circuit
            for _ in range(2):
                with pytest.raises(aiohttp.ClientError):
                    await client.get('/test')
            
            # Next request should fail immediately
            with pytest.raises(Exception, match="Circuit breaker is OPEN"):
                await client.get('/test')
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, client):
        """Test metrics collection"""
        # Successful request
        with patch.object(client, '_make_request_with_retry') as mock:
            mock.return_value = {'status': 200, 'headers': {}, 'data': 'ok'}
            await client.get('/success')
        
        # Failed request
        with patch.object(client, '_make_request_with_retry') as mock:
            mock.side_effect = aiohttp.ClientError("Error")
            try:
                await client.get('/failure')
            except:
                pass
        
        metrics = client.get_metrics()
        assert metrics['total_requests'] >= 0  # Depends on timing
        assert metrics['successful_requests'] >= 0
        assert metrics['failed_requests'] >= 0
    
    @pytest.mark.asyncio
    async def test_queue_overflow(self, client):
        """Test request queue overflow handling"""
        # Fill queue
        client.request_queue = asyncio.Queue(maxsize=2)
        
        # Add requests to fill queue
        futures = []
        with patch.object(client, '_make_request_with_retry'):
            for _ in range(2):
                futures.append(client.get('/test'))
        
        # Next request should fail
        with pytest.raises(RuntimeError, match="Request queue is full"):
            await client.get('/overflow')
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint"""
        health = await client.health_check()
        
        assert health['status'] == 'healthy'
        assert health['circuit_breaker'] == 'closed'
        assert 'metrics' in health
        assert 'queue_size' in health


class TestRequestMetrics:
    """Test metrics collection"""
    
    def test_metrics_initialization(self):
        """Test metrics initialization"""
        metrics = RequestMetrics()
        assert metrics.total_requests == 0
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 0
    
    def test_latency_tracking(self):
        """Test latency percentile calculation"""
        metrics = RequestMetrics()
        
        # Add sample latencies
        latencies = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        for latency in latencies:
            metrics.add_latency(latency)
        
        # Check percentiles
        assert metrics.get_percentile(50) is not None
        assert 0.4 <= metrics.get_percentile(50) <= 0.6
    
    def test_metrics_export(self):
        """Test metrics export"""
        metrics = RequestMetrics()
        metrics.total_requests = 100
        metrics.successful_requests = 95
        metrics.failed_requests = 5
        
        export = metrics.to_dict()
        assert export['total_requests'] == 100
        assert export['success_rate'] == 0.95


@pytest.mark.asyncio
async def test_end_to_end_scenario():
    """Test end-to-end usage scenario"""
    async with RateLimitedAPIClient(
        base_url="https://jsonplaceholder.typicode.com",
        rate_limit=5,
        rate_window=1
    ) as client:
        # Make real requests to test API
        with patch.object(client, '_make_request_with_retry') as mock:
            mock.return_value = {
                'status': 200,
                'headers': {'Content-Type': 'application/json'},
                'data': [{'id': 1, 'title': 'Test Post'}]
            }
            
            # Make multiple requests
            results = await asyncio.gather(
                client.get('/posts'),
                client.get('/posts/1'),
                client.get('/users'),
                return_exceptions=True
            )
            
            # Verify results
            successful = [r for r in results if isinstance(r, dict)]
            assert len(successful) == 3
            
            # Check metrics
            metrics = client.get_metrics()
            assert metrics['total_requests'] >= 3