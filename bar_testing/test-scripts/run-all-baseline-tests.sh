#!/bin/bash
# Run ALL Baseline Tests in Claude Terminal

echo "🎯 COMPLETE BASELINE TEST SUITE FOR CLAUDE"
echo "=========================================="
echo ""
echo "This script will run all baseline tests through Claude."
echo "Please follow the prompts and timing instructions."
echo ""

# Function to format time
format_time() {
    local seconds=$1
    local minutes=$((seconds / 60))
    local remaining_seconds=$((seconds % 60))
    echo "${minutes}m ${remaining_seconds}s"
}

# Initialize timing
suite_start=$(date +%s)

echo "📋 Test Suite Overview:"
echo "1. Simple Tests (4 tests, ~1 minute total)"
echo "2. Moderate Tests (4 tests, ~2-3 minutes total)"
echo "3. High Tests [OPTIONAL] (4 tests, ~60-100 minutes total)"
echo ""
read -p "Include HIGH difficulty tests? (y/N): " include_high

# SIMPLE TESTS
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📘 PHASE 1: SIMPLE TESTS"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Expected time: ~1 minute total"
echo "Record actual start time when pasting to Claude."
echo ""

simple_start=$(date +%s)

cat << 'EOF'
Please complete these 4 SIMPLE tests. Work through each one and note the time taken.

=== TEST 1a: Code Generation - Merge Sorted Lists ===
Write a Python function to merge two sorted lists of integers into a single sorted list. 
Include: basic tests (2-3), edge case handling (empty/None lists), docstring with examples, time complexity comment.

=== TEST 2a: Debugging - Fix Factorial Function ===
Debug this factorial function:
```python
def factorial(n):
    if n < 0:
        return "Error: Negative numbers not allowed"
    elif n == 0:
        return 1
    else:
        result = 0  # Bug 1
        for i in range(1, n):  # Bug 2
            result *= i
        return result
```
Find ALL bugs, explain what's wrong, provide corrected code with tests.

=== TEST 3a: Mathematical Problem - Fence Optimization ===
A farmer has 100 meters of fencing for a rectangular enclosure against a wall (only 3 sides need fencing). 
Find dimensions that maximize area. Show mathematical solution, Python verification, answer should be 50m x 25m = 1250 sq meters.

=== TEST 4a: Research & Analysis - Framework Comparison ===
Compare Python async frameworks (FastAPI, Aiohttp, Sanic) for building REST APIs. 
Include performance, ease of use, ecosystem, specific recommendation with justification.

When complete, note the total time taken for all 4 simple tests.
EOF

echo ""
echo "Press Enter after Claude completes ALL 4 simple tests..."
read
simple_end=$(date +%s)
simple_duration=$((simple_end - simple_start))
echo "✅ Simple tests completed in: $(format_time $simple_duration)"

# MODERATE TESTS
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📙 PHASE 2: MODERATE TESTS"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Expected time: ~2-3 minutes total"
echo "Record actual start time when pasting to Claude."
echo ""

moderate_start=$(date +%s)

cat << 'EOF'
Please complete these 4 MODERATE tests. These are more complex and should take longer.

=== TEST 1b: Code Generation - TaskQueue Class ===
Create a Python class called 'TaskQueue' that implements:
1. A simple priority queue for tasks
2. Methods: add_task(task, priority), get_next_task(), peek(), is_empty()
3. Priority levels: HIGH (1), MEDIUM (2), LOW (3)
4. Tasks with same priority should be FIFO
5. Thread-safe implementation using threading.Lock
6. Basic error handling for invalid inputs
7. Include usage example and 5-7 unit tests
Requirements: Use heapq for efficiency, include type hints and docstrings, handle edge cases gracefully

=== TEST 2b: Debugging - API Authentication Issue ===
Debug this Python API authentication code that's failing on the server:
```python
import hashlib
import time
from typing import Optional

class APIAuthenticator:
    def __init__(self, api_key: str, secret: str):
        self.api_key = api_key
        self.secret = secret
        self._token_cache = {}
    
    def generate_token(self, endpoint: str, params: dict) -> str:
        timestamp = int(time.time())
        
        # Build signature string
        signature_string = f"{self.api_key}{endpoint}"
        for key, value in sorted(params.items()):
            signature_string += f"{key}={value}"
        signature_string += str(timestamp)
        
        # Generate hash
        hash_obj = hashlib.sha256(signature_string.encode())
        hash_obj.update(self.secret.encode())
        
        return hash_obj.hexdigest()
    
    def make_authenticated_request(self, endpoint: str, params: dict):
        token = self.generate_token(endpoint, params)
        
        # Cache token for reuse
        cache_key = f"{endpoint}:{str(sorted(params.items()))}"
        self._token_cache[cache_key] = {
            'token': token,
            'timestamp': time.time()
        }
        
        headers = {
            'X-API-Key': self.api_key,
            'X-Auth-Token': token,
            'X-Timestamp': str(int(time.time()))
        }
        
        return headers

# Usage
auth = APIAuthenticator("test_key", "test_secret")
headers1 = auth.make_authenticated_request("/api/users", {"id": 123})
time.sleep(1)
headers2 = auth.make_authenticated_request("/api/users", {"id": 123})

print(f"Token 1: {headers1['X-Auth-Token']}")
print(f"Token 2: {headers2['X-Auth-Token']}")
print(f"Tokens match: {headers1['X-Auth-Token'] == headers2['X-Auth-Token']}")
```
The server expects: consistent tokens for same requests within 5-minute window, timestamp in signature must match X-Timestamp header, SHA256 signature format: sha256(api_key + endpoint + sorted_params + timestamp + secret). Find and fix ALL bugs.

=== TEST 3b: Math/Algorithm - Matrix Operations ===
Implement a Python class for 2D matrix operations without using NumPy with methods for transpose, multiply, determinant, and is_invertible. 
Include proper error handling, dimension checking, recursive cofactor expansion for determinant, comprehensive tests, and clear docstrings.

=== TEST 4b: Research - Database Technologies ===
Research and compare PostgreSQL with read replicas, MongoDB with sharding, DynamoDB, and CockroachDB for a high-traffic e-commerce platform. 
Analyze performance, scalability, consistency, operational complexity, and use cases. 
Provide comparison table, architecture recommendations, migration considerations, and sample configurations.

When complete, note the total time taken for all 4 moderate tests.
EOF

echo ""
echo "Press Enter after Claude completes ALL 4 moderate tests..."
read
moderate_end=$(date +%s)
moderate_duration=$((moderate_end - moderate_start))
echo "✅ Moderate tests completed in: $(format_time $moderate_duration)"

# HIGH TESTS (Optional)
if [[ "$include_high" =~ ^[Yy]$ ]]; then
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "📕 PHASE 3: HIGH DIFFICULTY TESTS (OPTIONAL)"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "⚠️  WARNING: These tests are very complex!"
    echo "Expected time: 60-100 minutes total"
    echo ""
    
    high_start=$(date +%s)
    
    cat << 'EOF'
Please complete these 4 HIGH DIFFICULTY tests. These are advanced challenges requiring deep expertise.

=== TEST 1: Code Generation - Rate-Limited API Client ===
Create a Python class called RateLimitedAPIClient with:
- Configurable rate limiting (e.g., 100 requests per minute)
- Exponential backoff retry logic for failed requests
- Concurrent request handling using asyncio
- Request queuing when rate limit is reached
- Detailed logging and metrics collection
- Error handling for network issues, timeouts, and API errors
- Support for GET and POST methods
- Circuit breaker pattern that opens after 5 consecutive failures
Include comprehensive unit tests, usage examples, and document design decisions.

=== TEST 2: Debugging - Complex Concurrency Bug ===
Debug this distributed task processing system with multiple critical bugs.
[Include the full buggy DistributedTaskProcessor code from the high test prompt]
Fix: race conditions, deadlocks, memory leaks, error propagation, and lost results.
Provide complete corrected implementation with tests.

=== TEST 3: Mathematical Problem - Vehicle Routing Optimization ===
Solve a logistics optimization problem with:
- N=20 delivery locations with coordinates
- M=4 trucks with capacities [50, 40, 45, 55]
- Time windows and demand constraints
- Minimize total distance while meeting all constraints
Provide: mathematical formulation, NP-hardness proof, approximation algorithm, Python implementation, complexity analysis, and visualizations.

=== TEST 4: Research & Analysis - Large-Scale Platform Architecture ===
Compare modern web frameworks for a 100,000+ user real-time collaborative platform:
- Next.js with Vercel
- SvelteKit with Cloudflare Workers
- Remix with fly.io
- Qwik with Deno Deploy
- Astro with SSG/ISR
Analyze: architecture, performance, scalability, security, costs, ecosystem.
Provide: executive summary, comparison matrix, architecture diagrams, TCO analysis, risk assessment, implementation roadmap.

When complete, note the total time taken for all 4 high tests.
EOF
    
    echo ""
    echo "Press Enter after Claude completes ALL 4 high tests..."
    read
    high_end=$(date +%s)
    high_duration=$((high_end - high_start))
    echo "✅ High tests completed in: $(format_time $high_duration)"
fi

# FINAL SUMMARY
suite_end=$(date +%s)
total_duration=$((suite_end - suite_start))

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📊 BASELINE TEST SUITE COMPLETE"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Time Summary:"
echo "- Simple Tests: $(format_time $simple_duration)"
echo "- Moderate Tests: $(format_time $moderate_duration)"
if [[ "$include_high" =~ ^[Yy]$ ]]; then
    echo "- High Tests: $(format_time $high_duration)"
fi
echo "- TOTAL TIME: $(format_time $total_duration)"
echo ""
echo "Expected vs Actual:"
echo "- Simple: Expected ~1 min, Actual: $(format_time $simple_duration)"
echo "- Moderate: Expected ~2-3 min, Actual: $(format_time $moderate_duration)"
if [[ "$include_high" =~ ^[Yy]$ ]]; then
    echo "- High: Expected 60-100 min, Actual: $(format_time $high_duration)"
fi
echo ""
echo "✅ All baseline data collected!"
echo "📁 Remember to save Claude's responses for quality analysis"
echo ""
echo "Next steps:"
echo "1. Review response quality and completeness"
echo "2. Compare with swarm configuration results"
echo "3. Analyze where multi-agent coordination adds value"