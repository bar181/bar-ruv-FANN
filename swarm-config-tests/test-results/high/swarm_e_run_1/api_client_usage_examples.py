"""
Usage Examples for RateLimitedAPIClient

Demonstrates various use cases and patterns for the production-ready API client.
"""

import asyncio
import logging
from rate_limited_api_client import (
    RateLimitedAPIClient, RateLimitConfig, RetryConfig, CircuitBreakerConfig
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def basic_usage_example():
    """Basic usage with default configuration"""
    print("\n=== Basic Usage Example ===")
    
    async with RateLimitedAPIClient('https://jsonplaceholder.typicode.com') as client:
        # Simple GET request
        users = await client.get('/users')
        print(f"Fetched {len(users)} users")
        
        # POST request with data
        new_post = await client.post('/posts', json={
            'title': 'Test Post',
            'body': 'This is a test post',
            'userId': 1
        })
        print(f"Created post with ID: {new_post.get('id')}")
        
        # Check metrics
        metrics = client.get_metrics()
        print(f"Total requests: {metrics['total_requests']}")
        print(f"Success rate: {metrics['success_rate']:.2%}")


async def custom_configuration_example():
    """Example with custom rate limiting and retry configuration"""
    print("\n=== Custom Configuration Example ===")
    
    # Configure aggressive rate limiting
    rate_config = RateLimitConfig(
        requests_per_minute=30,  # Only 30 requests per minute
        burst_size=5,           # Allow 5 requests in burst
        queue_size=100          # Queue up to 100 requests
    )
    
    # Configure retry behavior
    retry_config = RetryConfig(
        max_retries=5,          # Retry up to 5 times
        initial_delay=0.5,      # Start with 0.5s delay
        max_delay=30.0,         # Cap at 30s delay
        exponential_base=2.0,   # Double delay each time
        jitter=True             # Add randomization
    )
    
    # Configure circuit breaker
    circuit_config = CircuitBreakerConfig(
        failure_threshold=3,     # Open after 3 failures
        recovery_timeout=30.0,   # Try recovery after 30s
        half_open_max_calls=2    # Test with 2 calls
    )
    
    client = RateLimitedAPIClient(
        'https://api.github.com',
        rate_limit_config=rate_config,
        retry_config=retry_config,
        circuit_breaker_config=circuit_config,
        timeout=10.0
    )
    
    async with client:
        try:
            # This might be rate limited by GitHub
            repos = await client.get('/users/python/repos')
            print(f"Python has {len(repos)} public repositories")
        except Exception as e:
            print(f"Error fetching repos: {e}")


async def bulk_requests_example():
    """Example of handling bulk requests with rate limiting"""
    print("\n=== Bulk Requests Example ===")
    
    # Strict rate limit for demonstration
    rate_config = RateLimitConfig(
        requests_per_minute=60,
        burst_size=5
    )
    
    async with RateLimitedAPIClient(
        'https://jsonplaceholder.typicode.com',
        rate_limit_config=rate_config
    ) as client:
        
        # Fetch multiple posts concurrently
        post_ids = range(1, 21)  # Fetch 20 posts
        
        async def fetch_post(post_id):
            return await client.get(f'/posts/{post_id}')
        
        print("Fetching 20 posts with rate limiting...")
        start_time = asyncio.get_event_loop().time()
        
        # Create tasks for all posts
        tasks = [fetch_post(pid) for pid in post_ids]
        posts = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = asyncio.get_event_loop().time() - start_time
        successful_posts = [p for p in posts if not isinstance(p, Exception)]
        
        print(f"Fetched {len(successful_posts)} posts in {elapsed:.2f} seconds")
        print(f"Rate limited requests: {client.metrics.rate_limited_requests}")


async def error_handling_example():
    """Example of error handling and circuit breaker behavior"""
    print("\n=== Error Handling Example ===")
    
    # Quick circuit breaker for demonstration
    circuit_config = CircuitBreakerConfig(
        failure_threshold=2,
        recovery_timeout=5.0
    )
    
    async with RateLimitedAPIClient(
        'https://httpstat.us',  # Service that can simulate errors
        circuit_breaker_config=circuit_config
    ) as client:
        
        # Successful request
        try:
            response = await client.get('/200')
            print("✓ Successful request completed")
        except Exception as e:
            print(f"✗ Request failed: {e}")
        
        # Simulate server errors to trigger circuit breaker
        print("\nSimulating server errors...")
        for i in range(3):
            try:
                # This endpoint returns 500 error
                await client.get('/500')
            except Exception as e:
                print(f"✗ Request {i+1} failed: {type(e).__name__}")
                print(f"  Circuit state: {client.circuit_state.value}")
        
        # Circuit should be open now
        print(f"\nCircuit breaker trips: {client.metrics.circuit_breaker_trips}")
        
        # Wait for recovery
        print("\nWaiting for circuit recovery...")
        await asyncio.sleep(6)
        
        # Try again - should enter half-open state
        try:
            response = await client.get('/200')
            print("✓ Recovery successful - circuit closed")
        except Exception as e:
            print(f"✗ Recovery failed: {e}")


async def real_world_example():
    """Real-world example: Fetching cryptocurrency prices"""
    print("\n=== Real-World Example: Crypto Price Monitor ===")
    
    # Configure for a free API with rate limits
    rate_config = RateLimitConfig(
        requests_per_minute=30,  # Typical free tier limit
        burst_size=5
    )
    
    async with RateLimitedAPIClient(
        'https://api.coinbase.com',
        rate_limit_config=rate_config
    ) as client:
        
        currencies = ['BTC-USD', 'ETH-USD', 'DOGE-USD']
        
        print("Fetching cryptocurrency prices...")
        for currency in currencies:
            try:
                response = await client.get(f'/v2/exchange-rates?currency={currency.split("-")[0]}')
                
                if isinstance(response, dict) and 'data' in response:
                    rates = response['data']['rates']
                    usd_rate = rates.get('USD', 'N/A')
                    print(f"{currency}: ${usd_rate}")
                    
            except Exception as e:
                print(f"Failed to fetch {currency}: {e}")
        
        # Show final metrics
        metrics = client.get_metrics()
        print(f"\nAPI Client Metrics:")
        print(f"  Total requests: {metrics['total_requests']}")
        print(f"  Success rate: {metrics['success_rate']:.2%}")
        print(f"  Avg latency: {metrics['average_latency']:.3f}s")


async def monitoring_example():
    """Example of monitoring and metrics collection"""
    print("\n=== Monitoring Example ===")
    
    async with RateLimitedAPIClient('https://api.github.com') as client:
        # Set up periodic metrics reporting
        async def monitor_metrics():
            while True:
                await asyncio.sleep(5)
                metrics = client.get_metrics()
                if metrics['total_requests'] > 0:
                    print(f"\n[Monitor] Requests: {metrics['total_requests']}, "
                          f"Success: {metrics['success_rate']:.1%}, "
                          f"Avg latency: {metrics['average_latency']:.3f}s, "
                          f"Circuit: {metrics['circuit_state']}")
        
        # Start monitoring task
        monitor_task = asyncio.create_task(monitor_metrics())
        
        try:
            # Make various requests
            endpoints = [
                '/users/python',
                '/users/golang', 
                '/users/rust',
                '/users/javascript'
            ]
            
            for endpoint in endpoints:
                try:
                    data = await client.get(endpoint)
                    print(f"✓ Fetched {endpoint}")
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"✗ Failed {endpoint}: {e}")
            
        finally:
            monitor_task.cancel()


async def advanced_patterns_example():
    """Advanced usage patterns"""
    print("\n=== Advanced Patterns Example ===")
    
    # Pattern 1: Custom headers and authentication
    async with RateLimitedAPIClient('https://api.example.com') as client:
        # Add authentication header
        headers = {'Authorization': 'Bearer YOUR_TOKEN_HERE'}
        
        try:
            # Headers are passed through to the request
            data = await client.get('/protected-endpoint', headers=headers)
        except Exception as e:
            print(f"Auth example (expected to fail): {e}")
    
    # Pattern 2: Request with timeout override
    async with RateLimitedAPIClient('https://httpstat.us', timeout=5.0) as client:
        try:
            # This endpoint delays for 3 seconds
            print("Making slow request (3s delay)...")
            response = await client.get('/200?sleep=3000')
            print("✓ Slow request completed")
        except asyncio.TimeoutError:
            print("✗ Request timed out")
    
    # Pattern 3: Handling different content types
    async with RateLimitedAPIClient('https://httpbin.org') as client:
        # JSON response
        json_data = await client.get('/json')
        print(f"JSON response type: {type(json_data)}")
        
        # Binary response (image)
        image_data = await client.get('/image/png')
        print(f"Binary response size: {len(image_data)} bytes")


async def main():
    """Run all examples"""
    examples = [
        basic_usage_example,
        custom_configuration_example,
        bulk_requests_example,
        error_handling_example,
        real_world_example,
        monitoring_example,
        advanced_patterns_example
    ]
    
    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"\nExample failed: {e}")
        
        # Small delay between examples
        await asyncio.sleep(2)
    
    print("\n=== All examples completed ===")


if __name__ == '__main__':
    asyncio.run(main())