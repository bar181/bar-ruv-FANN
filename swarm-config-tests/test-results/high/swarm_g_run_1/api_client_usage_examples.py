"""
Usage examples for RateLimitedAPIClient

Demonstrates common usage patterns and best practices.
"""

import asyncio
import json
from rate_limited_api_client import RateLimitedAPIClient, CircuitBreakerConfig
from datetime import timedelta


async def basic_usage_example():
    """Basic usage with context manager"""
    print("\n=== Basic Usage Example ===")
    
    async with RateLimitedAPIClient(
        base_url="https://api.example.com",
        rate_limit=100,  # 100 requests per minute
        rate_window=60,
        max_retries=3
    ) as client:
        # Simple GET request
        response = await client.get("/users/123")
        print(f"User data: {response['data']}")
        
        # POST request with data
        new_user = await client.post("/users", json={
            "name": "John Doe",
            "email": "john@example.com"
        })
        print(f"Created user: {new_user['data']}")
        
        # Check metrics
        metrics = client.get_metrics()
        print(f"Metrics: {json.dumps(metrics, indent=2)}")


async def concurrent_requests_example():
    """Demonstrate concurrent request handling"""
    print("\n=== Concurrent Requests Example ===")
    
    async with RateLimitedAPIClient(
        base_url="https://jsonplaceholder.typicode.com",
        rate_limit=10,  # Low limit to demonstrate queuing
        rate_window=1
    ) as client:
        # Launch multiple concurrent requests
        tasks = []
        for i in range(20):
            task = client.get(f"/posts/{i+1}")
            tasks.append(task)
        
        # Wait for all requests
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = sum(1 for r in results if isinstance(r, dict))
        failed = sum(1 for r in results if isinstance(r, Exception))
        
        print(f"Successful requests: {successful}")
        print(f"Failed requests: {failed}")
        
        # Show rate limiting in action
        metrics = client.get_metrics()
        print(f"Rate limited requests: {metrics['rate_limited_requests']}")


async def circuit_breaker_example():
    """Demonstrate circuit breaker functionality"""
    print("\n=== Circuit Breaker Example ===")
    
    # Configure aggressive circuit breaker for demonstration
    circuit_config = CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=timedelta(seconds=5),
        half_open_requests=2
    )
    
    async with RateLimitedAPIClient(
        base_url="https://unreliable-api.example.com",
        circuit_breaker_config=circuit_config
    ) as client:
        # Simulate failures
        for i in range(5):
            try:
                # This would fail in real scenario
                response = await client.get("/flaky-endpoint")
                print(f"Request {i+1}: Success")
            except Exception as e:
                print(f"Request {i+1}: Failed - {str(e)}")
            
            # Check circuit breaker state
            health = await client.health_check()
            print(f"Circuit breaker state: {health['circuit_breaker']}")
            
            await asyncio.sleep(1)


async def error_handling_example():
    """Demonstrate comprehensive error handling"""
    print("\n=== Error Handling Example ===")
    
    async with RateLimitedAPIClient(
        base_url="https://api.example.com",
        max_retries=3,
        timeout=5
    ) as client:
        # Handle different error scenarios
        
        # 1. Network timeout
        try:
            response = await client.get("/slow-endpoint")
        except asyncio.TimeoutError:
            print("Request timed out")
        
        # 2. HTTP errors
        try:
            response = await client.get("/not-found")
        except Exception as e:
            print(f"HTTP error: {e}")
        
        # 3. Rate limiting
        try:
            # Make many requests quickly
            for _ in range(200):
                await client.get("/endpoint")
        except Exception as e:
            print(f"Rate limit error: {e}")


async def monitoring_example():
    """Demonstrate monitoring and metrics"""
    print("\n=== Monitoring Example ===")
    
    async with RateLimitedAPIClient(
        base_url="https://jsonplaceholder.typicode.com"
    ) as client:
        # Make various requests
        await client.get("/posts/1")
        await client.post("/posts", json={"title": "Test", "body": "Content"})
        
        # Try to trigger some failures
        try:
            await client.get("/invalid-endpoint")
        except:
            pass
        
        # Get comprehensive metrics
        metrics = client.get_metrics()
        print("\nMetrics Report:")
        print(f"Total requests: {metrics['total_requests']}")
        print(f"Success rate: {metrics['success_rate']:.2%}")
        print(f"P50 latency: {metrics['latency_p50']:.3f}s" if metrics['latency_p50'] else "P50 latency: N/A")
        print(f"P95 latency: {metrics['latency_p95']:.3f}s" if metrics['latency_p95'] else "P95 latency: N/A")
        print(f"Circuit breaker trips: {metrics['circuit_breaker_trips']}")
        
        # Health check
        health = await client.health_check()
        print(f"\nHealth Status: {json.dumps(health, indent=2)}")


async def custom_configuration_example():
    """Demonstrate custom configuration options"""
    print("\n=== Custom Configuration Example ===")
    
    # Create client with custom settings
    client = RateLimitedAPIClient(
        base_url="https://api.example.com",
        rate_limit=500,        # 500 requests
        rate_window=300,       # per 5 minutes
        max_retries=5,         # More retries
        timeout=60,            # Longer timeout
        max_queue_size=5000,   # Larger queue
        circuit_breaker_config=CircuitBreakerConfig(
            failure_threshold=10,
            recovery_timeout=timedelta(minutes=2)
        )
    )
    
    await client.start()
    
    try:
        # Use the client
        response = await client.get("/data")
        print(f"Response: {response}")
    finally:
        await client.close()


async def batch_processing_example():
    """Demonstrate batch request processing"""
    print("\n=== Batch Processing Example ===")
    
    async with RateLimitedAPIClient(
        base_url="https://jsonplaceholder.typicode.com",
        rate_limit=30,
        rate_window=10
    ) as client:
        # Process items in batches
        items = list(range(1, 101))  # 100 items to process
        batch_size = 10
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            # Process batch concurrently
            tasks = [client.get(f"/posts/{item}") for item in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful = sum(1 for r in results if isinstance(r, dict))
            print(f"Batch {i//batch_size + 1}: {successful}/{len(batch)} successful")
            
            # Small delay between batches
            await asyncio.sleep(0.5)


def main():
    """Run all examples"""
    examples = [
        basic_usage_example,
        concurrent_requests_example,
        circuit_breaker_example,
        error_handling_example,
        monitoring_example,
        custom_configuration_example,
        batch_processing_example
    ]
    
    for example in examples:
        try:
            asyncio.run(example())
        except Exception as e:
            print(f"Example failed: {e}")
        print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    # Run examples
    print("RateLimitedAPIClient Usage Examples")
    print("===================================")
    
    # Note: Replace URLs with actual API endpoints for real testing
    print("\nNote: Some examples use placeholder URLs.")
    print("Replace with actual API endpoints for real testing.\n")
    
    main()