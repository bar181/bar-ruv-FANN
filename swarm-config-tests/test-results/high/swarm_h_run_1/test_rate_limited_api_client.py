"""
Comprehensive unit tests for RateLimitedAPIClient
Research Division - Maximum Stress Test Implementation

These tests cover all functionality with edge cases and concurrent scenarios.
"""

import asyncio
import pytest
import aiohttp
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import time
import json
from aioresponses import aioresponses
import logging

from rate_limited_api_client import (
    RateLimitedAPIClient,
    RateLimitConfig,
    CircuitBreakerConfig,
    RetryConfig,
    CircuitState,
    RequestMethod,
    RequestMetrics
)


class TestRateLimitedAPIClient:
    """Comprehensive test suite for RateLimitedAPIClient"""

    @pytest.fixture
    def rate_limit_config(self):
        """Default rate limit configuration for tests"""
        return RateLimitConfig(
            max_requests=10,
            window_seconds=60,
            burst_limit=5,
            queue_timeout=5.0
        )

    @pytest.fixture
    def circuit_breaker_config(self):
        """Default circuit breaker configuration for tests"""
        return CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=5.0,
            success_threshold=2,
            half_open_max_requests=3
        )

    @pytest.fixture
    def retry_config(self):
        """Default retry configuration for tests"""
        return RetryConfig(
            max_retries=2,
            base_delay=0.1,
            max_delay=1.0,
            backoff_factor=2.0,
            jitter=False
        )

    @pytest.fixture
    def client(self, rate_limit_config, circuit_breaker_config, retry_config):
        """Create test client"""
        return RateLimitedAPIClient(
            base_url="https://api.test.com",
            rate_limit=rate_limit_config,
            circuit_breaker=circuit_breaker_config,
            retry_config=retry_config
        )

    @pytest.mark.asyncio
    async def test_client_initialization(self, client):
        """Test client initialization"""
        assert client.base_url == "https://api.test.com"
        assert client.rate_limit.max_requests == 10
        assert client.circuit_breaker.failure_threshold == 3
        assert client.retry_config.max_retries == 2
        assert client._circuit_state == CircuitState.CLOSED
        assert client._tokens == 10.0
        assert client.metrics.total_requests == 0

    @pytest.mark.asyncio
    async def test_context_manager(self, rate_limit_config, circuit_breaker_config, retry_config):
        """Test async context manager"""
        async with RateLimitedAPIClient(
            base_url="https://api.test.com",
            rate_limit=rate_limit_config,
            circuit_breaker=circuit_breaker_config,
            retry_config=retry_config
        ) as client:
            assert client._session is not None
            assert not client._session.closed
        
        # Session should be closed after context exit
        assert client._session.closed

    @pytest.mark.asyncio
    async def test_successful_get_request(self, client):
        """Test successful GET request"""
        with aioresponses() as m:
            m.get("https://api.test.com/users/123", payload={"id": 123, "name": "John"})
            
            async with client:
                response = await client.get("/users/123")
                assert response.status == 200
                
                data = await response.json()
                assert data["id"] == 123
                assert data["name"] == "John"

    @pytest.mark.asyncio
    async def test_successful_post_request(self, client):
        """Test successful POST request"""
        with aioresponses() as m:
            m.post("https://api.test.com/users", payload={"id": 456, "name": "Jane"})
            
            async with client:
                response = await client.post(
                    "/users",
                    json_data={"name": "Jane", "email": "jane@example.com"}
                )
                assert response.status == 200
                
                data = await response.json()
                assert data["id"] == 456
                assert data["name"] == "Jane"

    @pytest.mark.asyncio
    async def test_rate_limiting_token_bucket(self, client):
        """Test rate limiting with token bucket algorithm"""
        async with client:
            # Use up all tokens
            for i in range(10):
                can_proceed = await client._wait_for_rate_limit()
                assert can_proceed
                assert client._tokens == 9 - i
            
            # Next request should be limited
            start_time = time.time()
            can_proceed = await client._wait_for_rate_limit()
            end_time = time.time()
            
            # Should have waited
            assert end_time - start_time > 0.1
            assert client._tokens < 1.0

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_failures(self, client):
        """Test circuit breaker opens after threshold failures"""
        with aioresponses() as m:
            m.get("https://api.test.com/fail", status=500)
            
            async with client:
                # Make requests that will fail
                for i in range(3):
                    try:
                        await client.get("/fail")
                    except Exception:
                        pass
                
                # Circuit should be open
                assert client._circuit_state == CircuitState.OPEN
                assert client._circuit_failure_count == 3
                assert client.metrics.circuit_breaker_opens == 1

    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_recovery(self, client):
        """Test circuit breaker recovery through half-open state"""
        with aioresponses() as m:
            # First, trigger circuit breaker
            m.get("https://api.test.com/fail", status=500)
            
            async with client:
                # Cause failures to open circuit
                for i in range(3):
                    try:
                        await client.get("/fail")
                    except Exception:
                        pass
                
                assert client._circuit_state == CircuitState.OPEN
                
                # Wait for recovery timeout
                await asyncio.sleep(5.1)
                
                # Add successful response
                m.get("https://api.test.com/success", payload={"success": True})
                
                # Next request should transition to half-open
                can_proceed = await client._check_circuit_breaker()
                assert can_proceed
                assert client._circuit_state == CircuitState.HALF_OPEN

    @pytest.mark.asyncio
    async def test_retry_with_exponential_backoff(self, client):
        """Test retry logic with exponential backoff"""
        with aioresponses() as m:
            # First two requests fail, third succeeds
            m.get("https://api.test.com/retry", status=500)
            m.get("https://api.test.com/retry", status=500)
            m.get("https://api.test.com/retry", payload={"success": True})
            
            async with client:
                start_time = time.time()
                response = await client.get("/retry")
                end_time = time.time()
                
                # Should have succeeded after retries
                assert response.status == 200
                
                # Should have taken time for retries (0.1 + 0.2 = 0.3s minimum)
                assert end_time - start_time >= 0.3
                
                # Check metrics
                assert client.metrics.retry_count == 2
                assert client.metrics.successful_requests == 1

    @pytest.mark.asyncio
    async def test_request_queuing_with_priority(self, client):
        """Test request queuing with priority handling"""
        with aioresponses() as m:
            m.get("https://api.test.com/low", payload={"priority": "low"})
            m.get("https://api.test.com/high", payload={"priority": "high"})
            
            async with client:
                # Queue requests with different priorities
                low_priority_task = asyncio.create_task(
                    client.get("/low", priority=1)
                )
                high_priority_task = asyncio.create_task(
                    client.get("/high", priority=10)
                )
                
                # Wait for both to complete
                responses = await asyncio.gather(low_priority_task, high_priority_task)
                
                assert len(responses) == 2
                assert all(r.status == 200 for r in responses)

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client):
        """Test handling of concurrent requests"""
        with aioresponses() as m:
            # Add multiple endpoints
            for i in range(20):
                m.get(f"https://api.test.com/item/{i}", payload={"id": i})
            
            async with client:
                # Make 20 concurrent requests
                tasks = [
                    client.get(f"/item/{i}")
                    for i in range(20)
                ]
                
                responses = await asyncio.gather(*tasks)
                
                # All requests should succeed
                assert len(responses) == 20
                assert all(r.status == 200 for r in responses)
                
                # Check metrics
                assert client.metrics.total_requests >= 20
                assert client.metrics.successful_requests >= 20

    @pytest.mark.asyncio
    async def test_request_timeout_in_queue(self, client):
        """Test request timeout when queued too long"""
        # Create client with very short queue timeout
        client.rate_limit.queue_timeout = 0.1
        
        with aioresponses() as m:
            m.get("https://api.test.com/slow", payload={"data": "slow"})
            
            async with client:
                # Fill up rate limit tokens
                for i in range(10):
                    await client._wait_for_rate_limit()
                
                # This request should timeout in queue
                with pytest.raises(asyncio.TimeoutError):
                    await client.get("/slow")

    @pytest.mark.asyncio
    async def test_metrics_collection(self, client):
        """Test metrics collection and calculation"""
        with aioresponses() as m:
            m.get("https://api.test.com/success", payload={"success": True})
            m.get("https://api.test.com/fail", status=500)
            
            async with client:
                # Successful request
                await client.get("/success")
                
                # Failed request
                try:
                    await client.get("/fail")
                except Exception:
                    pass
                
                metrics = client.get_metrics()
                
                assert metrics["total_requests"] >= 2
                assert metrics["successful_requests"] >= 1
                assert metrics["failed_requests"] >= 1
                assert metrics["success_rate"] > 0
                assert metrics["circuit_breaker_state"] == "closed"
                assert "average_response_time" in metrics
                assert "queue_size" in metrics

    @pytest.mark.asyncio
    async def test_metrics_reset(self, client):
        """Test metrics reset functionality"""
        with aioresponses() as m:
            m.get("https://api.test.com/test", payload={"test": True})
            
            async with client:
                await client.get("/test")
                
                assert client.metrics.total_requests > 0
                assert client.metrics.successful_requests > 0
                
                # Reset metrics
                client.reset_metrics()
                
                assert client.metrics.total_requests == 0
                assert client.metrics.successful_requests == 0
                assert client.metrics.failed_requests == 0

    @pytest.mark.asyncio
    async def test_circuit_breaker_reset(self, client):
        """Test circuit breaker reset functionality"""
        with aioresponses() as m:
            m.get("https://api.test.com/fail", status=500)
            
            async with client:
                # Open circuit breaker
                for i in range(3):
                    try:
                        await client.get("/fail")
                    except Exception:
                        pass
                
                assert client._circuit_state == CircuitState.OPEN
                
                # Reset circuit breaker
                client.reset_circuit_breaker()
                
                assert client._circuit_state == CircuitState.CLOSED
                assert client._circuit_failure_count == 0

    @pytest.mark.asyncio
    async def test_custom_headers_and_params(self, client):
        """Test custom headers and parameters"""
        with aioresponses() as m:
            m.get("https://api.test.com/custom", payload={"custom": True})
            
            async with client:
                response = await client.get(
                    "/custom",
                    headers={"Authorization": "Bearer token123"},
                    params={"filter": "active", "limit": 10}
                )
                
                assert response.status == 200

    @pytest.mark.asyncio
    async def test_error_handling_network_errors(self, client):
        """Test error handling for network errors"""
        with aioresponses() as m:
            m.get("https://api.test.com/network_error", exception=aiohttp.ClientError())
            
            async with client:
                with pytest.raises(aiohttp.ClientError):
                    await client.get("/network_error")

    @pytest.mark.asyncio
    async def test_memory_efficiency(self, client):
        """Test memory efficiency with large number of requests"""
        with aioresponses() as m:
            # Add many endpoints
            for i in range(1000):
                m.get(f"https://api.test.com/item/{i}", payload={"id": i})
            
            async with client:
                # Make many requests
                tasks = [client.get(f"/item/{i}") for i in range(1000)]
                
                # Process in batches to avoid overwhelming
                for i in range(0, 1000, 50):
                    batch = tasks[i:i+50]
                    await asyncio.gather(*batch)
                
                # Check that response times collection is capped
                assert len(client.metrics.response_times) <= 1000

    @pytest.mark.asyncio
    async def test_base_url_handling(self):
        """Test different base URL configurations"""
        configs = [
            ("https://api.test.com", "/users", "https://api.test.com/users"),
            ("https://api.test.com/", "/users", "https://api.test.com/users"),
            ("https://api.test.com/v1", "users", "https://api.test.com/v1/users"),
            ("", "https://api.test.com/users", "https://api.test.com/users"),
        ]
        
        for base_url, endpoint, expected in configs:
            client = RateLimitedAPIClient(base_url=base_url)
            
            with aioresponses() as m:
                m.get(expected, payload={"test": True})
                
                async with client:
                    response = await client.get(endpoint)
                    assert response.status == 200

    @pytest.mark.asyncio
    async def test_cleanup_on_close(self, client):
        """Test proper cleanup when client is closed"""
        async with client:
            # Ensure background tasks are running
            assert len(client._queue_processors) > 0
            assert client._processing_active
            
            # Make a request to start processing
            with aioresponses() as m:
                m.get("https://api.test.com/test", payload={"test": True})
                await client.get("/test")
        
        # After context exit, should be cleaned up
        assert not client._processing_active
        assert all(task.done() for task in client._queue_processors)

    @pytest.mark.asyncio
    async def test_jitter_in_retries(self):
        """Test jitter in retry delays"""
        retry_config = RetryConfig(
            max_retries=2,
            base_delay=1.0,
            backoff_factor=2.0,
            jitter=True
        )
        
        client = RateLimitedAPIClient(retry_config=retry_config)
        
        with aioresponses() as m:
            m.get("https://api.test.com/jitter", status=500)
            m.get("https://api.test.com/jitter", status=500)
            m.get("https://api.test.com/jitter", payload={"success": True})
            
            async with client:
                start_time = time.time()
                response = await client.get("https://api.test.com/jitter")
                end_time = time.time()
                
                # Should have succeeded
                assert response.status == 200
                
                # Should have taken time for retries with jitter
                assert end_time - start_time >= 1.0  # At least base delay
                assert end_time - start_time <= 10.0  # But not too long

    @pytest.mark.asyncio
    async def test_stress_test_high_concurrency(self, client):
        """Stress test with high concurrency"""
        with aioresponses() as m:
            # Add many endpoints
            for i in range(500):
                m.get(f"https://api.test.com/stress/{i}", payload={"id": i})
            
            async with client:
                # Create many concurrent requests
                tasks = [client.get(f"/stress/{i}") for i in range(500)]
                
                # Execute all concurrently
                start_time = time.time()
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                end_time = time.time()
                
                # Check results
                successful = sum(1 for r in responses if isinstance(r, aiohttp.ClientResponse))
                
                print(f"Stress test: {successful}/500 requests succeeded in {end_time - start_time:.2f}s")
                
                # Should handle most requests successfully
                assert successful > 400  # Allow some failures due to rate limiting
                
                # Check metrics
                metrics = client.get_metrics()
                assert metrics["total_requests"] >= 400


@pytest.mark.asyncio
async def test_integration_with_real_endpoints():
    """Integration test with real HTTP endpoints (httpbin.org)"""
    client = RateLimitedAPIClient(
        base_url="https://httpbin.org",
        rate_limit=RateLimitConfig(max_requests=10, window_seconds=60),
        retry_config=RetryConfig(max_retries=2, base_delay=0.5)
    )
    
    async with client:
        # Test GET request
        response = await client.get("/get")
        assert response.status == 200
        
        data = await response.json()
        assert "url" in data
        
        # Test POST request
        response = await client.post("/post", json_data={"test": "data"})
        assert response.status == 200
        
        data = await response.json()
        assert "json" in data
        assert data["json"]["test"] == "data"
        
        # Check metrics
        metrics = client.get_metrics()
        assert metrics["total_requests"] >= 2
        assert metrics["successful_requests"] >= 2
        assert metrics["success_rate"] == 100.0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])