import pytest
import pytest_asyncio
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch
import aiohttp
from aiohttp import ClientResponseError
from rate_limited_api_client import (
    RateLimitedAPIClient, RateLimitConfig, RetryConfig, 
    CircuitState, RequestMetrics
)


@pytest.fixture
def rate_limit_config():
    return RateLimitConfig(max_requests=10, time_window=1.0)


@pytest.fixture
def retry_config():
    return RetryConfig(max_retries=3, base_delay=0.1, max_delay=1.0)


@pytest_asyncio.fixture
async def mock_session():
    session = AsyncMock(spec=aiohttp.ClientSession)
    return session


@pytest_asyncio.fixture
async def client(rate_limit_config, retry_config):
    client = RateLimitedAPIClient(
        base_url="https://api.test.com",
        rate_limit_config=rate_limit_config,
        retry_config=retry_config,
        circuit_breaker_threshold=3,
        circuit_breaker_timeout=1.0
    )
    yield client
    await client.close()


class TestRateLimiting:
    @pytest.mark.asyncio
    async def test_rate_limit_enforcement(self, client, mock_session):
        """Test that rate limiting is properly enforced."""
        client._session = mock_session
        
        # Mock successful responses
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content_type = 'application/json'
        mock_response.headers = {}
        mock_response.json = AsyncMock(return_value={'success': True})
        mock_response.raise_for_status = Mock()
        
        mock_session.request.return_value.__aenter__.return_value = mock_response
        
        await client.start()
        
        # Make requests up to the limit
        start_time = time.time()
        tasks = []
        for i in range(15):  # More than rate limit
            tasks.append(client.get(f"/test/{i}"))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - start_time
        
        # Should take at least 0.5 seconds due to rate limiting
        assert elapsed > 0.4
        
        # All requests should eventually succeed
        assert all(not isinstance(r, Exception) for r in results)
        
        # Check metrics
        metrics = client.get_metrics()
        assert metrics['total_requests'] == 15
        assert metrics['rate_limited_requests'] > 0
        
    @pytest.mark.asyncio
    async def test_token_refill(self, client):
        """Test that tokens are refilled over time."""
        client.tokens = 0
        client.last_refill = time.time() - 2.0  # 2 seconds ago
        
        await client._refill_tokens()
        
        # Should have refilled tokens
        assert client.tokens == 10  # max_requests


class TestRetryLogic:
    @pytest.mark.asyncio
    async def test_exponential_backoff(self, client, mock_session):
        """Test exponential backoff on failures."""
        client._session = mock_session
        
        # Mock failures then success
        mock_session.request.side_effect = [
            self._create_error_context(aiohttp.ClientError("Connection error")),
            self._create_error_context(aiohttp.ClientError("Connection error")),
            self._create_success_context({'data': 'success'})
        ]
        
        await client.start()
        
        start_time = time.time()
        result = await client.get("/test")
        elapsed = time.time() - start_time
        
        # Should have retried with backoff
        assert result['data']['data'] == 'success'
        assert elapsed > 0.2  # At least 0.1 + 0.2 seconds of backoff
        assert client.metrics.failed_requests == 2
        assert client.metrics.successful_requests == 1
        
    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, client, mock_session):
        """Test that max retries is respected."""
        client._session = mock_session
        
        # Always fail
        mock_session.request.side_effect = lambda *args, **kwargs: self._create_error_context(
            aiohttp.ClientError("Persistent error")
        )
        
        await client.start()
        
        with pytest.raises(aiohttp.ClientError):
            await client.get("/test")
            
        assert client.metrics.failed_requests == 4  # 1 initial + 3 retries
        
    @pytest.mark.asyncio
    async def test_rate_limit_429_response(self, client, mock_session):
        """Test handling of 429 rate limit responses."""
        client._session = mock_session
        
        # Mock 429 then success
        mock_429 = AsyncMock()
        mock_429.status = 429
        mock_429.headers = {'Retry-After': '1'}
        mock_429.raise_for_status.side_effect = ClientResponseError(
            None, None, status=429
        )
        
        mock_success = AsyncMock()
        mock_success.status = 200
        mock_success.content_type = 'application/json'
        mock_success.headers = {}
        mock_success.json = AsyncMock(return_value={'success': True})
        mock_success.raise_for_status = Mock()
        
        mock_session.request.side_effect = [
            self._create_response_context(mock_429),
            self._create_response_context(mock_success)
        ]
        
        await client.start()
        
        start_time = time.time()
        result = await client.get("/test")
        elapsed = time.time() - start_time
        
        assert result['data']['success'] is True
        assert elapsed >= 1.0  # Should wait for Retry-After
        
    def _create_error_context(self, error):
        """Helper to create error context manager."""
        
        class ErrorContext:
            async def __aenter__(self):
                raise error
                
            async def __aexit__(self, *args):
                pass
                
        return ErrorContext()
        
    def _create_response_context(self, response):
        """Helper to create response context manager."""
        
        class ResponseContext:
            async def __aenter__(self):
                return response
                
            async def __aexit__(self, *args):
                pass
                
        return ResponseContext()
        
    def _create_success_context(self, data):
        """Helper to create successful response context."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content_type = 'application/json'
        mock_response.headers = {}
        mock_response.json = AsyncMock(return_value=data)
        mock_response.raise_for_status = Mock()
        
        return self._create_response_context(mock_response)


class TestCircuitBreaker:
    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold(self, client, mock_session):
        """Test circuit breaker opens after consecutive failures."""
        client._session = mock_session
        
        # Always fail
        mock_session.request.side_effect = lambda *args, **kwargs: self._create_error_context(
            aiohttp.ClientError("Service unavailable")
        )
        
        await client.start()
        
        # Make requests until circuit opens
        for i in range(3):
            with pytest.raises(aiohttp.ClientError):
                await client.get(f"/test/{i}")
                
        assert client.circuit_state == CircuitState.OPEN
        assert client.metrics.failed_requests == 3
        
        # Next request should fail immediately
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            await client.get("/test/blocked")
            
        assert client.metrics.circuit_breaker_rejections == 1
        
    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_recovery(self, client, mock_session):
        """Test circuit breaker recovery through half-open state."""
        client._session = mock_session
        await client.start()
        
        # Force circuit open
        client.circuit_state = CircuitState.OPEN
        client.circuit_opened_at = time.time() - 2.0  # 2 seconds ago
        
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content_type = 'application/json'
        mock_response.headers = {}
        mock_response.json = AsyncMock(return_value={'success': True})
        mock_response.raise_for_status = Mock()
        
        mock_session.request.return_value.__aenter__.return_value = mock_response
        
        # Should enter half-open and succeed
        result = await client.get("/test")
        
        assert result['data']['success'] is True
        assert client.circuit_state == CircuitState.CLOSED
        
    def _create_error_context(self, error):
        """Helper to create error context manager."""
        
        class ErrorContext:
            async def __aenter__(self):
                raise error
                
            async def __aexit__(self, *args):
                pass
                
        return ErrorContext()


class TestRequestQueue:
    @pytest.mark.asyncio
    async def test_request_queue_priority(self, client, mock_session):
        """Test that higher priority requests are processed first."""
        client._session = mock_session
        
        processed_order = []
        
        async def mock_request(method, url, **kwargs):
            # Extract ID from URL
            request_id = int(url.split('/')[-1])
            processed_order.append(request_id)
            
            # Simulate some processing time
            await asyncio.sleep(0.01)
            
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.content_type = 'application/json'
            mock_response.headers = {}
            mock_response.json = AsyncMock(return_value={'id': request_id})
            mock_response.raise_for_status = Mock()
            
            class ResponseContext:
                async def __aenter__(self):
                    return mock_response
                    
                async def __aexit__(self, *args):
                    pass
                    
            return ResponseContext()
            
        mock_session.request.side_effect = mock_request
        
        await client.start()
        
        # Queue requests with different priorities
        tasks = []
        # Low priority
        for i in range(5):
            tasks.append(client.request('GET', f'/test/{i}', priority=1))
            
        # High priority (should be processed first)
        for i in range(5, 10):
            tasks.append(client.request('GET', f'/test/{i}', priority=10))
            
        # Wait a bit to ensure all are queued
        await asyncio.sleep(0.1)
        
        results = await asyncio.gather(*tasks)
        
        # High priority requests (5-9) should be processed before low priority (0-4)
        high_priority_indices = [i for i, x in enumerate(processed_order) if x >= 5]
        low_priority_indices = [i for i, x in enumerate(processed_order) if x < 5]
        
        if high_priority_indices and low_priority_indices:
            assert max(high_priority_indices) < min(low_priority_indices)


class TestMetrics:
    @pytest.mark.asyncio
    async def test_metrics_collection(self, client, mock_session):
        """Test that metrics are properly collected."""
        client._session = mock_session
        
        # Mock mixed responses
        success_response = self._create_success_response({'data': 'success'})
        error_context = self._create_error_context(aiohttp.ClientError("Error"))
        
        mock_session.request.side_effect = [
            self._create_response_context(success_response),
            error_context,
            self._create_response_context(success_response),
        ]
        
        await client.start()
        
        # Make requests
        results = await asyncio.gather(
            client.get("/test/1"),
            client.get("/test/2"),
            client.get("/test/3"),
            return_exceptions=True
        )
        
        metrics = client.get_metrics()
        
        assert metrics['total_requests'] >= 3
        assert metrics['successful_requests'] == 2
        assert metrics['failed_requests'] >= 1
        assert metrics['average_response_time'] > 0
        
    def _create_success_response(self, data):
        """Helper to create successful response."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content_type = 'application/json'
        mock_response.headers = {}
        mock_response.json = AsyncMock(return_value=data)
        mock_response.raise_for_status = Mock()
        return mock_response
        
    def _create_response_context(self, response):
        """Helper to create response context manager."""
        
        class ResponseContext:
            async def __aenter__(self):
                return response
                
            async def __aexit__(self, *args):
                pass
                
        return ResponseContext()
        
    def _create_error_context(self, error):
        """Helper to create error context manager."""
        
        class ErrorContext:
            async def __aenter__(self):
                raise error
                
            async def __aexit__(self, *args):
                pass
                
        return ErrorContext()


class TestClientLifecycle:
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test client works as context manager."""
        rate_limit = RateLimitConfig(max_requests=10, time_window=1.0)
        
        async with RateLimitedAPIClient(
            base_url="https://api.test.com",
            rate_limit_config=rate_limit
        ) as client:
            assert client._session is not None
            assert client.queue_processor_task is not None
            
        # After exiting, should be cleaned up
        assert client._session is None
        
    @pytest.mark.asyncio
    async def test_manual_lifecycle(self):
        """Test manual start/close lifecycle."""
        rate_limit = RateLimitConfig(max_requests=10, time_window=1.0)
        client = RateLimitedAPIClient(
            base_url="https://api.test.com",
            rate_limit_config=rate_limit
        )
        
        # Initially not started
        assert client._session is None
        
        await client.start()
        assert client._session is not None
        assert client.queue_processor_task is not None
        
        await client.close()
        assert client._session is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])