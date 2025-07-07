"""
Production Usage Examples for RateLimitedAPIClient
Research Division - 20-Agent Maximum Stress Test

This file demonstrates real-world usage patterns and best practices.
"""

import asyncio
import aiohttp
import logging
import json
from typing import List, Dict, Any
from rate_limited_api_client import (
    RateLimitedAPIClient,
    RateLimitConfig,
    CircuitBreakerConfig,
    RetryConfig
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductionAPIClient:
    """Production-ready wrapper for the RateLimitedAPIClient"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.example.com"):
        """Initialize production client with optimal settings"""
        
        # Production-optimized configurations
        self.rate_limit = RateLimitConfig(
            max_requests=1000,      # 1000 requests per minute
            window_seconds=60,
            burst_limit=50,         # Allow burst of 50 requests
            queue_timeout=30.0      # 30 second queue timeout
        )
        
        self.circuit_breaker = CircuitBreakerConfig(
            failure_threshold=5,    # Open after 5 failures
            recovery_timeout=60.0,  # 1 minute recovery
            success_threshold=3,    # 3 successes to close
            half_open_max_requests=10
        )
        
        self.retry_config = RetryConfig(
            max_retries=3,
            base_delay=1.0,
            max_delay=30.0,
            backoff_factor=2.0,
            jitter=True
        )
        
        # Headers for all requests
        self.default_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ProductionAPIClient/1.0",
            "Accept": "application/json"
        }
        
        # Initialize client
        self.client = RateLimitedAPIClient(
            base_url=base_url,
            rate_limit=self.rate_limit,
            circuit_breaker=self.circuit_breaker,
            retry_config=self.retry_config,
            logger=logger
        )
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user by ID"""
        response = await self.client.get(
            f"/users/{user_id}",
            headers=self.default_headers
        )
        return await response.json()
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        response = await self.client.post(
            "/users",
            headers=self.default_headers,
            json_data=user_data
        )
        return await response.json()
    
    async def bulk_create_users(self, users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple users concurrently"""
        tasks = [
            self.create_user(user_data)
            for user_data in users
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def get_user_analytics(self, user_id: int, date_range: str) -> Dict[str, Any]:
        """Get user analytics (high priority request)"""
        response = await self.client.get(
            f"/users/{user_id}/analytics",
            headers=self.default_headers,
            params={"date_range": date_range},
            priority=10  # High priority
        )
        return await response.json()
    
    def get_client_metrics(self) -> Dict[str, Any]:
        """Get client performance metrics"""
        return self.client.get_metrics()


async def example_basic_usage():
    """Basic usage example"""
    print("=== Basic Usage Example ===")
    
    # Simple configuration
    client = RateLimitedAPIClient(base_url="https://httpbin.org")
    
    async with client:
        # Basic GET request
        response = await client.get("/get")
        data = await response.json()
        print(f"GET Response: {data['url']}")
        
        # Basic POST request
        response = await client.post("/post", json_data={"message": "Hello, World!"})
        data = await response.json()
        print(f"POST Response: {data['json']['message']}")
        
        # Show metrics
        metrics = client.get_metrics()
        print(f"Metrics: {json.dumps(metrics, indent=2)}")


async def example_production_usage():
    """Production usage example"""
    print("\n=== Production Usage Example ===")
    
    # Production client with authentication
    async with ProductionAPIClient("your-api-key-here", "https://httpbin.org") as client:
        try:
            # Get user
            user_data = await client.get_user(123)
            print(f"Retrieved user: {user_data.get('url', 'User data')}")
            
            # Create multiple users
            new_users = [
                {"name": "Alice", "email": "alice@example.com"},
                {"name": "Bob", "email": "bob@example.com"},
                {"name": "Charlie", "email": "charlie@example.com"}
            ]
            
            results = await client.bulk_create_users(new_users)
            successful = sum(1 for r in results if not isinstance(r, Exception))
            print(f"Created {successful}/{len(new_users)} users successfully")
            
            # Get analytics (high priority)
            analytics = await client.get_user_analytics(123, "7d")
            print(f"Analytics retrieved: {analytics.get('url', 'Analytics data')}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        # Show performance metrics
        metrics = client.get_client_metrics()
        print(f"Final metrics: {json.dumps(metrics, indent=2)}")


async def example_high_throughput():
    """High throughput example"""
    print("\n=== High Throughput Example ===")
    
    # High throughput configuration
    rate_limit = RateLimitConfig(
        max_requests=500,  # 500 requests per minute
        window_seconds=60,
        burst_limit=100,   # Allow burst of 100
        queue_timeout=10.0
    )
    
    client = RateLimitedAPIClient(
        base_url="https://httpbin.org",
        rate_limit=rate_limit
    )
    
    async with client:
        # Make many concurrent requests
        tasks = [
            client.get(f"/get?id={i}", priority=i % 3)  # Varying priorities
            for i in range(100)
        ]
        
        start_time = asyncio.get_event_loop().time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = asyncio.get_event_loop().time()
        
        successful = sum(1 for r in results if not isinstance(r, Exception))
        print(f"Processed {successful}/100 requests in {end_time - start_time:.2f} seconds")
        
        # Show throughput metrics
        metrics = client.get_metrics()
        print(f"Throughput: {metrics['successful_requests']/(end_time - start_time):.2f} requests/second")


async def example_circuit_breaker_demo():
    """Circuit breaker demonstration"""
    print("\n=== Circuit Breaker Demo ===")
    
    # Circuit breaker with low threshold for demo
    circuit_breaker = CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=5.0,
        success_threshold=2
    )
    
    client = RateLimitedAPIClient(
        base_url="https://httpbin.org",
        circuit_breaker=circuit_breaker
    )
    
    async with client:
        # Simulate failures to trigger circuit breaker
        for i in range(5):
            try:
                # This will fail
                response = await client.get("/status/500")
                print(f"Request {i+1}: Success (unexpected)")
            except Exception as e:
                print(f"Request {i+1}: Failed - {type(e).__name__}")
                
                metrics = client.get_metrics()
                print(f"  Circuit state: {metrics['circuit_breaker_state']}")
                
                if metrics['circuit_breaker_state'] == 'open':
                    print("  Circuit breaker is now OPEN!")
                    break
        
        # Wait for recovery
        print("\nWaiting for circuit recovery...")
        await asyncio.sleep(6)
        
        # Try successful request
        try:
            response = await client.get("/get")
            print("Recovery request: Success!")
            
            metrics = client.get_metrics()
            print(f"Final circuit state: {metrics['circuit_breaker_state']}")
            
        except Exception as e:
            print(f"Recovery request failed: {e}")


async def example_monitoring_and_alerting():
    """Example of monitoring and alerting integration"""
    print("\n=== Monitoring & Alerting Example ===")
    
    client = RateLimitedAPIClient(base_url="https://httpbin.org")
    
    async def check_health():
        """Health check function"""
        metrics = client.get_metrics()
        
        # Check various health indicators
        health_issues = []
        
        if metrics['circuit_breaker_state'] == 'open':
            health_issues.append("Circuit breaker is OPEN")
        
        if metrics['success_rate'] < 95:
            health_issues.append(f"Success rate low: {metrics['success_rate']:.2f}%")
        
        if metrics['average_response_time'] > 5.0:
            health_issues.append(f"High latency: {metrics['average_response_time']:.2f}s")
        
        if metrics['queue_size'] > 50:
            health_issues.append(f"High queue size: {metrics['queue_size']}")
        
        if health_issues:
            print(f"🚨 ALERT: {', '.join(health_issues)}")
        else:
            print("✅ All systems healthy")
        
        return len(health_issues) == 0
    
    async with client:
        # Make some requests
        tasks = [client.get("/get") for _ in range(10)]
        await asyncio.gather(*tasks)
        
        # Check health
        is_healthy = await check_health()
        
        # Detailed metrics report
        metrics = client.get_metrics()
        print(f"\nDetailed Metrics Report:")
        print(f"  Total Requests: {metrics['total_requests']}")
        print(f"  Success Rate: {metrics['success_rate']:.2f}%")
        print(f"  Average Response Time: {metrics['average_response_time']:.3f}s")
        print(f"  Circuit Breaker State: {metrics['circuit_breaker_state']}")
        print(f"  Queue Size: {metrics['queue_size']}")
        print(f"  Available Tokens: {metrics['current_tokens']:.2f}")


async def example_error_handling_patterns():
    """Error handling patterns example"""
    print("\n=== Error Handling Patterns ===")
    
    client = RateLimitedAPIClient(base_url="https://httpbin.org")
    
    async def safe_request(url: str, max_attempts: int = 3) -> Dict[str, Any]:
        """Safe request wrapper with custom error handling"""
        for attempt in range(max_attempts):
            try:
                response = await client.get(url)
                return await response.json()
            
            except aiohttp.ClientResponseError as e:
                if e.status == 404:
                    return {"error": "Not found", "status": 404}
                elif e.status >= 500:
                    if attempt == max_attempts - 1:
                        return {"error": "Server error", "status": e.status}
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return {"error": f"Client error: {e.status}", "status": e.status}
            
            except asyncio.TimeoutError:
                if attempt == max_attempts - 1:
                    return {"error": "Request timeout", "status": 408}
                await asyncio.sleep(1)
            
            except Exception as e:
                return {"error": f"Unexpected error: {str(e)}", "status": 500}
        
        return {"error": "Max attempts exceeded", "status": 500}
    
    async with client:
        # Test different error scenarios
        test_cases = [
            "/get",           # Success
            "/status/404",    # Not found
            "/status/500",    # Server error
            "/delay/10",      # Timeout
        ]
        
        for url in test_cases:
            result = await safe_request(url)
            print(f"Request to {url}: {result}")


async def example_batch_processing():
    """Batch processing example"""
    print("\n=== Batch Processing Example ===")
    
    client = RateLimitedAPIClient(base_url="https://httpbin.org")
    
    async def process_batch(items: List[Any], batch_size: int = 10) -> List[Dict[str, Any]]:
        """Process items in batches"""
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_tasks = [
                client.get(f"/get?item={item}")
                for item in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Process results
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    results.append({"error": str(result), "item": batch[j]})
                else:
                    data = await result.json()
                    results.append({"success": True, "item": batch[j], "data": data})
            
            # Brief pause between batches
            await asyncio.sleep(0.1)
        
        return results
    
    async with client:
        # Process 50 items in batches
        items = list(range(50))
        results = await process_batch(items, batch_size=10)
        
        successful = sum(1 for r in results if r.get("success"))
        print(f"Processed {successful}/{len(items)} items successfully")


async def main():
    """Run all examples"""
    print("🚀 RateLimitedAPIClient Examples - Research Division Maximum Stress Test")
    print("=" * 80)
    
    examples = [
        example_basic_usage,
        example_production_usage,
        example_high_throughput,
        example_circuit_breaker_demo,
        example_monitoring_and_alerting,
        example_error_handling_patterns,
        example_batch_processing
    ]
    
    for example in examples:
        try:
            await example()
            await asyncio.sleep(1)  # Brief pause between examples
        except Exception as e:
            print(f"Error in {example.__name__}: {e}")
    
    print("\n" + "=" * 80)
    print("🎯 All examples completed! Research Division stress test successful.")


if __name__ == "__main__":
    asyncio.run(main())