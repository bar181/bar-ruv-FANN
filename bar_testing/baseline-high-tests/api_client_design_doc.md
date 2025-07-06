# Rate-Limited API Client Design Document

## Architecture Decisions

### 1. Token Bucket Algorithm for Rate Limiting
- **Decision**: Implemented token bucket algorithm instead of sliding window
- **Rationale**: 
  - More flexible for burst traffic
  - Simpler implementation with good performance
  - Allows accumulated tokens for idle periods
- **Trade-offs**: 
  - Less precise than sliding window for strict rate enforcement
  - May allow temporary bursts exceeding average rate

### 2. Async/Await with asyncio
- **Decision**: Full async implementation using aiohttp
- **Rationale**:
  - Better concurrency handling for I/O-bound operations
  - Natural fit for rate limiting and queuing
  - Modern Python best practice for network operations
- **Trade-offs**:
  - Requires async context throughout application
  - More complex testing setup

### 3. Circuit Breaker State Machine
- **Decision**: Three-state circuit breaker (CLOSED, OPEN, HALF_OPEN)
- **Rationale**:
  - Industry standard pattern
  - Prevents cascading failures
  - Automatic recovery testing
- **Trade-offs**:
  - Additional complexity
  - May reject valid requests during recovery

### 4. Priority Queue for Request Management
- **Decision**: asyncio.Queue with priority ordering
- **Rationale**:
  - Allows important requests to be processed first
  - Built-in backpressure with max queue size
  - Simple integration with async workflow
- **Trade-offs**:
  - Not persistent across restarts
  - Memory usage scales with queue size

### 5. Exponential Backoff with Jitter
- **Decision**: Exponential backoff with configurable base and max delay
- **Rationale**:
  - Reduces thundering herd problem
  - Gives failing services time to recover
  - Widely accepted retry pattern
- **Trade-offs**:
  - Can increase latency for transient failures
  - May delay recovery detection

## Implementation Details

### Rate Limiting
```python
# Token refill calculation
tokens_to_add = int(elapsed / time_window * max_requests)
```
- Tokens are refilled based on elapsed time
- Partial tokens are truncated (conservative approach)
- Token check is atomic with asyncio.Lock

### Circuit Breaker Logic
- Failure threshold: Configurable consecutive failures
- Recovery timeout: Time before attempting HALF_OPEN
- Success in HALF_OPEN immediately closes circuit
- Any failure in HALF_OPEN reopens circuit

### Metrics Collection
- Per-request timing
- Categorized failure counts
- Circuit breaker state tracking
- Queue depth monitoring

### Error Handling Hierarchy
1. Circuit breaker check (fail fast)
2. Rate limit acquisition (wait/retry)
3. HTTP request execution
4. Retry logic on failure
5. Metric updates

## Usage Patterns

### Basic Usage
```python
async with RateLimitedAPIClient(
    base_url="https://api.example.com",
    rate_limit_config=RateLimitConfig(100, 60)  # 100 req/min
) as client:
    response = await client.get("/endpoint")
```

### Advanced Configuration
```python
client = RateLimitedAPIClient(
    base_url="https://api.example.com",
    rate_limit_config=RateLimitConfig(1000, 60),
    retry_config=RetryConfig(
        max_retries=5,
        base_delay=0.5,
        max_delay=30.0
    ),
    circuit_breaker_threshold=10,
    circuit_breaker_timeout=120.0,
    max_queue_size=5000
)
```

### Priority Requests
```python
# High priority request
urgent_data = await client.request(
    'POST', 
    '/critical-endpoint',
    priority=100,
    json={'data': 'urgent'}
)

# Normal priority
normal_data = await client.request(
    'GET',
    '/regular-endpoint', 
    priority=1
)
```

## Performance Considerations

1. **Memory Usage**: O(n) where n is queue size
2. **CPU Usage**: Minimal, mostly I/O waiting
3. **Network Efficiency**: Batching possible with queue
4. **Latency**: Added by rate limiting and retries

## Security Considerations

1. **Timeout Protection**: Configurable request timeout
2. **Queue Size Limits**: Prevents memory exhaustion
3. **Circuit Breaker**: Prevents cascade failures
4. **No Credential Storage**: Pass through auth headers

## Future Enhancements

1. **Persistent Queue**: Redis/disk backing for reliability
2. **Distributed Rate Limiting**: Coordinate across instances
3. **Adaptive Rate Limiting**: Adjust based on server responses
4. **Request Deduplication**: Prevent duplicate in-flight requests
5. **Response Caching**: Reduce redundant API calls
6. **WebSocket Support**: Long-lived connections
7. **GraphQL Support**: Specialized query handling