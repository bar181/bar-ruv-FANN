"""
Comprehensive unit tests for RateLimitedAPIClient
"""

import asyncio
import pytest
import aiohttp
from aiohttp import web
import time
from unittest.mock import Mock, patch, AsyncMock
import json

from rate_limited_api_client import (
    RateLimitedAPIClient, RateLimitConfig, RetryConfig, 
    CircuitBreakerConfig, CircuitState
)


class MockAPIServer:
    """Mock API server for testing"""
    
    def __init__(self):
        self.request_count = 0
        self.fail_count = 0
        self.should_fail = False
        self.failure_status = 500
        self.delay = 0
        
    async def handle_request(self, request):
        """Handle mock API request"""
        self.request_count += 1
        
        if self.delay > 0:
            await asyncio.sleep(self.delay)
        
        if self.should_fail and self.fail_count > 0:
            self.fail_count -= 1
            return web.Response(
                text="Server error",
                status=self.failure_status
            )
        
        data = {
            'request_count': self.request_count,
            'method': request.method,
            'path': request.path,
            'timestamp': time.time()
        }
        
        return web.json_response(data)


@pytest.fixture
async def mock_server():
    """Create and run mock API server"""
    mock = MockAPIServer()
    app = web.Application()
    app.router.add_route('*', '/{path:.*}', mock.handle_request)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 0)
    await site.start()
    
    port = site._server.sockets[0].getsockname()[1]
    url = f'http://localhost:{port}'
    
    yield url, mock
    
    await runner.cleanup()


@pytest.mark.asyncio
class TestRateLimitedAPIClient:
    """Test suite for RateLimitedAPIClient"""
    
    async def test_basic_get_request(self, mock_server):
        """Test basic GET request functionality"""
        url, server = mock_server
        
        async with RateLimitedAPIClient(url) as client:
            response = await client.get('/test')
            
            assert response['method'] == 'GET'
            assert response['path'] == '/test'
            assert server.request_count == 1
    
    async def test_basic_post_request(self, mock_server):
        """Test basic POST request functionality"""
        url, server = mock_server
        
        async with RateLimitedAPIClient(url) as client:
            response = await client.post('/test', json={'key': 'value'})
            
            assert response['method'] == 'POST'
            assert response['path'] == '/test'
            assert server.request_count == 1
    
    async def test_rate_limiting(self, mock_server):
        """Test rate limiting functionality"""
        url, server = mock_server
        
        # Configure very strict rate limit
        rate_config = RateLimitConfig(
            requests_per_minute=6,  # 0.1 per second
            burst_size=2,
            queue_size=10
        )
        
        async with RateLimitedAPIClient(url, rate_limit_config=rate_config) as client:
            start_time = time.time()
            
            # First 2 requests should be immediate (burst)
            await client.get('/test1')
            await client.get('/test2')
            
            # Third request should be delayed
            await client.get('/test3')
            
            elapsed = time.time() - start_time
            
            # Should take at least some time due to rate limiting
            assert elapsed > 0.5
            assert server.request_count == 3
            assert client.metrics.rate_limited_requests > 0
    
    async def test_retry_on_failure(self, mock_server):
        """Test retry logic on server errors"""
        url, server = mock_server
        
        # Configure retry
        retry_config = RetryConfig(
            max_retries=3,
            initial_delay=0.1,
            exponential_base=2.0,
            jitter=False
        )
        
        async with RateLimitedAPIClient(url, retry_config=retry_config) as client:
            # Set server to fail twice then succeed
            server.should_fail = True
            server.fail_count = 2
            server.failure_status = 500
            
            start_time = time.time()
            response = await client.get('/test')
            elapsed = time.time() - start_time
            
            # Should succeed after retries
            assert response['method'] == 'GET'
            assert server.request_count == 3  # 2 failures + 1 success
            
            # Should have taken time for retries (0.1 + 0.2 seconds minimum)
            assert elapsed >= 0.3
    
    async def test_no_retry_on_client_error(self, mock_server):
        """Test that client errors (4xx) are not retried"""
        url, server = mock_server
        
        retry_config = RetryConfig(max_retries=3)
        
        async with RateLimitedAPIClient(url, retry_config=retry_config) as client:
            server.should_fail = True
            server.fail_count = 10
            server.failure_status = 404
            
            with pytest.raises(aiohttp.ClientResponseError) as exc_info:
                await client.get('/test')
            
            assert exc_info.value.status == 404
            assert server.request_count == 1  # No retries
    
    async def test_circuit_breaker_opens(self, mock_server):
        """Test circuit breaker opens after consecutive failures"""
        url, server = mock_server
        
        cb_config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=1.0,
            half_open_max_calls=2
        )
        
        async with RateLimitedAPIClient(url, circuit_breaker_config=cb_config) as client:
            server.should_fail = True
            server.fail_count = 10
            
            # Make requests until circuit opens
            for i in range(3):
                with pytest.raises(Exception):
                    await client.get(f'/test{i}')
            
            # Circuit should be open now
            assert client.circuit_state == CircuitState.OPEN
            assert client.metrics.circuit_breaker_trips == 1
            
            # Further requests should fail immediately
            server.request_count_before = server.request_count
            with pytest.raises(Exception):
                await client.get('/test_blocked')
            
            # No new request should have been made
            assert server.request_count == server.request_count_before
    
    async def test_circuit_breaker_recovery(self, mock_server):
        """Test circuit breaker recovery process"""
        url, server = mock_server
        
        cb_config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=0.5,
            half_open_max_calls=2
        )
        
        async with RateLimitedAPIClient(url, circuit_breaker_config=cb_config) as client:
            # Open the circuit
            server.should_fail = True
            server.fail_count = 5
            
            for i in range(2):
                with pytest.raises(Exception):
                    await client.get(f'/test{i}')
            
            assert client.circuit_state == CircuitState.OPEN
            
            # Wait for recovery timeout
            await asyncio.sleep(0.6)
            
            # Server should work now
            server.should_fail = False
            
            # First request should work (half-open state)
            response = await client.get('/test_recovery')
            assert response['method'] == 'GET'
            
            # After successful requests, circuit should close
            await client.get('/test_recovery2')
            assert client.circuit_state == CircuitState.CLOSED
    
    async def test_metrics_collection(self, mock_server):
        """Test metrics collection functionality"""
        url, server = mock_server
        
        async with RateLimitedAPIClient(url) as client:
            # Make some successful requests
            for i in range(5):
                await client.get(f'/test{i}')
            
            # Make some failed requests
            server.should_fail = True
            server.fail_count = 2
            
            for i in range(2):
                with pytest.raises(Exception):
                    await client.get(f'/fail{i}')
            
            metrics = client.get_metrics()
            
            assert metrics['total_requests'] == 7
            assert metrics['successful_requests'] == 5
            assert metrics['failed_requests'] == 2
            assert metrics['success_rate'] == 5/7
            assert metrics['average_latency'] > 0
    
    async def test_concurrent_requests(self, mock_server):
        """Test handling of concurrent requests"""
        url, server = mock_server
        
        async with RateLimitedAPIClient(url) as client:
            # Launch multiple concurrent requests
            tasks = []
            for i in range(10):
                task = asyncio.create_task(client.get(f'/concurrent{i}'))
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            
            assert len(responses) == 10
            assert all(r['method'] == 'GET' for r in responses)
            assert server.request_count == 10
    
    async def test_timeout_handling(self, mock_server):
        """Test request timeout handling"""
        url, server = mock_server
        
        # Set server to delay responses
        server.delay = 2.0
        
        # Client with short timeout
        async with RateLimitedAPIClient(url, timeout=0.5) as client:
            with pytest.raises(asyncio.TimeoutError):
                await client.get('/timeout_test')
            
            assert client.metrics.failed_requests == 1
    
    async def test_queue_overflow(self, mock_server):
        """Test behavior when request queue is full"""
        url, server = mock_server
        
        rate_config = RateLimitConfig(
            requests_per_minute=1,
            burst_size=1,
            queue_size=2
        )
        
        async with RateLimitedAPIClient(url, rate_limit_config=rate_config) as client:
            # Fill up the queue
            tasks = []
            
            # This should fill the burst and queue
            for i in range(4):
                task = asyncio.create_task(client.get(f'/queue{i}'))
                tasks.append(task)
            
            # This should fail due to full queue
            with pytest.raises(asyncio.QueueFull):
                client.request_queue.put_nowait({
                    'method': 'GET',
                    'endpoint': '/overflow',
                    'kwargs': {},
                    'future': asyncio.Future()
                })
    
    async def test_context_manager(self, mock_server):
        """Test proper context manager behavior"""
        url, server = mock_server
        
        client = RateLimitedAPIClient(url)
        
        # Should not work before entering context
        with pytest.raises(RuntimeError):
            await client.get('/test')
        
        # Should work within context
        async with client:
            response = await client.get('/test')
            assert response['method'] == 'GET'
        
        # Should not work after exiting context
        with pytest.raises(RuntimeError):
            await client.get('/test')
    
    async def test_exponential_backoff_calculation(self):
        """Test exponential backoff delay calculation"""
        retry_config = RetryConfig(
            initial_delay=1.0,
            exponential_base=2.0,
            max_delay=10.0,
            jitter=False
        )
        
        client = RateLimitedAPIClient('http://test', retry_config=retry_config)
        
        # Test delay progression
        assert client._calculate_retry_delay(0) == 1.0
        assert client._calculate_retry_delay(1) == 2.0
        assert client._calculate_retry_delay(2) == 4.0
        assert client._calculate_retry_delay(3) == 8.0
        assert client._calculate_retry_delay(4) == 10.0  # Max delay
        assert client._calculate_retry_delay(5) == 10.0  # Still max delay
    
    async def test_jitter_in_retry_delay(self):
        """Test jitter in retry delay calculation"""
        retry_config = RetryConfig(
            initial_delay=1.0,
            jitter=True
        )
        
        client = RateLimitedAPIClient('http://test', retry_config=retry_config)
        
        # Collect multiple delay calculations
        delays = [client._calculate_retry_delay(1) for _ in range(100)]
        
        # With jitter, delays should vary
        assert len(set(delays)) > 1
        assert all(0.75 * 2.0 <= d <= 1.25 * 2.0 for d in delays)


# Example usage and integration test
async def example_usage():
    """Example of how to use the RateLimitedAPIClient"""
    
    # Configure the client
    rate_config = RateLimitConfig(
        requests_per_minute=100,
        burst_size=10
    )
    
    retry_config = RetryConfig(
        max_retries=3,
        initial_delay=1.0
    )
    
    circuit_config = CircuitBreakerConfig(
        failure_threshold=5,
        recovery_timeout=60.0
    )
    
    # Use the client
    async with RateLimitedAPIClient(
        'https://api.example.com',
        rate_limit_config=rate_config,
        retry_config=retry_config,
        circuit_breaker_config=circuit_config
    ) as client:
        
        # Make requests
        try:
            # GET request
            data = await client.get('/users/123')
            print(f"User data: {data}")
            
            # POST request
            new_user = await client.post('/users', json={
                'name': 'John Doe',
                'email': 'john@example.com'
            })
            print(f"Created user: {new_user}")
            
            # Check metrics
            metrics = client.get_metrics()
            print(f"Client metrics: {metrics}")
            
        except aiohttp.ClientError as e:
            print(f"API error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == '__main__':
    # Run the example
    asyncio.run(example_usage())