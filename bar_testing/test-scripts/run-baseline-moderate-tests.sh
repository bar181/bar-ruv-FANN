#!/bin/bash
# Run Baseline MODERATE Tests (No Swarm)

echo "🎯 Running Baseline MODERATE Tests (Claude Native - No Swarm)"
echo "============================================================="
echo ""
echo "📊 These tests are more complex than simple tests"
echo "⏱️  Expected: 5-8 minutes per test"
echo ""

# Create timestamp for this test run
timestamp=$(date +%Y%m%d_%H%M%S)
results_dir="bar_testing/test-results/moderate/baseline_run_$timestamp"
mkdir -p "$results_dir"

echo "📁 Results will be saved to: $results_dir"
echo ""

# Function to calculate duration
calculate_duration() {
    local start=$1
    local end=$2
    local duration=$((end - start))
    echo "$duration"
}

# Test 1b: Code Generation - TaskQueue Class
echo "▶️  Test 1b: Code Generation - TaskQueue Class (MODERATE)"
echo "--------------------------------------------------------"
cat > "$results_dir/test_1b_prompt.txt" << 'EOF'
Create a Python class called 'TaskQueue' that implements:

1. A simple priority queue for tasks
2. Methods: add_task(task, priority), get_next_task(), peek(), is_empty()
3. Priority levels: HIGH (1), MEDIUM (2), LOW (3)
4. Tasks with same priority should be FIFO
5. Thread-safe implementation using threading.Lock
6. Basic error handling for invalid inputs
7. Include usage example and 5-7 unit tests

Requirements:
- Use heapq for efficiency
- Include type hints and docstrings
- Handle edge cases gracefully
EOF

echo "📝 Prompt saved to: $results_dir/test_1b_prompt.txt"
echo "⏱️  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
start_1b=$(date +%s)
echo ""
echo "COPY AND PASTE THIS PROMPT TO CLAUDE:"
echo "======================================"
cat "$results_dir/test_1b_prompt.txt"
echo "======================================"
echo ""
echo "💾 Save response to: $results_dir/test_1b_response.txt"
read -p "Press Enter when complete..."
end_1b=$(date +%s)
duration_1b=$(calculate_duration $start_1b $end_1b)
echo "⏱️  Duration: $duration_1b seconds"
echo "$duration_1b" > "$results_dir/test_1b_duration.txt"
echo ""

# Test 2b: Debugging - API Authentication Issue
echo "▶️  Test 2b: Debugging - API Authentication (MODERATE)"
echo "----------------------------------------------------"
cat > "$results_dir/test_2b_prompt.txt" << 'EOF'
Debug this Python API authentication code:

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

The authentication is failing on the server. The server expects:
1. Consistent tokens for same requests within 5-minute window
2. Timestamp in signature must match X-Timestamp header
3. SHA256 signature format: sha256(api_key + endpoint + sorted_params + timestamp + secret)

Find and fix ALL bugs. Explain what was wrong and provide corrected code.
EOF

echo "📝 Prompt saved to: $results_dir/test_2b_prompt.txt"
echo "⏱️  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
start_2b=$(date +%s)
echo ""
echo "COPY AND PASTE THIS PROMPT TO CLAUDE:"
echo "======================================"
cat "$results_dir/test_2b_prompt.txt"
echo "======================================"
echo ""
echo "💾 Save response to: $results_dir/test_2b_response.txt"
read -p "Press Enter when complete..."
end_2b=$(date +%s)
duration_2b=$(calculate_duration $start_2b $end_2b)
echo "⏱️  Duration: $duration_2b seconds"
echo "$duration_2b" > "$results_dir/test_2b_duration.txt"
echo ""

# Test 3b: Math - Matrix Operations
echo "▶️  Test 3b: Math/Algorithm - Matrix Operations (MODERATE)"
echo "--------------------------------------------------------"
cat > "$results_dir/test_3b_prompt.txt" << 'EOF'
Implement a Python class for 2D matrix operations without using NumPy:

```python
class Matrix:
    """2D Matrix with basic operations"""
    
    def __init__(self, data):
        # Initialize from 2D list
        pass
    
    def transpose(self):
        # Return transposed matrix
        pass
    
    def multiply(self, other):
        # Matrix multiplication (self @ other)
        pass
    
    def determinant(self):
        # Calculate determinant (for square matrices)
        pass
    
    def is_invertible(self):
        # Check if matrix can be inverted
        pass
```

Requirements:
1. Implement ALL methods with proper error handling
2. Support matrix multiplication with dimension checking
3. Calculate determinant using recursive cofactor expansion
4. Include comprehensive tests covering edge cases
5. Add clear docstrings with examples

Provide complete implementation with usage examples.
EOF

echo "📝 Prompt saved to: $results_dir/test_3b_prompt.txt"
echo "⏱️  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
start_3b=$(date +%s)
echo ""
echo "COPY AND PASTE THIS PROMPT TO CLAUDE:"
echo "======================================"
cat "$results_dir/test_3b_prompt.txt"
echo "======================================"
echo ""
echo "💾 Save response to: $results_dir/test_3b_response.txt"
read -p "Press Enter when complete..."
end_3b=$(date +%s)
duration_3b=$(calculate_duration $start_3b $end_3b)
echo "⏱️  Duration: $duration_3b seconds"
echo "$duration_3b" > "$results_dir/test_3b_duration.txt"
echo ""

# Test 4b: Research - Database Technologies
echo "▶️  Test 4b: Research - Database Technologies (MODERATE)"
echo "------------------------------------------------------"
cat > "$results_dir/test_4b_prompt.txt" << 'EOF'
Research and compare these database technologies for a high-traffic e-commerce platform:

1. PostgreSQL with read replicas
2. MongoDB with sharding
3. DynamoDB
4. CockroachDB

Analyze each for:
- Performance characteristics (read/write throughput)
- Scalability patterns and limitations
- Consistency guarantees and CAP theorem tradeoffs
- Operational complexity and costs
- Best use cases within e-commerce (catalog, orders, inventory, user data)

Provide:
1. Detailed comparison table
2. Architecture recommendations for different e-commerce components
3. Migration considerations from traditional RDBMS
4. Sample configuration snippets for optimal performance

Make a specific recommendation with justification.
EOF

echo "📝 Prompt saved to: $results_dir/test_4b_prompt.txt"
echo "⏱️  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
start_4b=$(date +%s)
echo ""
echo "COPY AND PASTE THIS PROMPT TO CLAUDE:"
echo "======================================"
cat "$results_dir/test_4b_prompt.txt"
echo "======================================"
echo ""
echo "💾 Save response to: $results_dir/test_4b_response.txt"
read -p "Press Enter when complete..."
end_4b=$(date +%s)
duration_4b=$(calculate_duration $start_4b $end_4b)
echo "⏱️  Duration: $duration_4b seconds"
echo "$duration_4b" > "$results_dir/test_4b_duration.txt"

# Calculate totals
total_start=$start_1b
total_end=$end_4b
total_duration=$(calculate_duration $total_start $total_end)

# Create summary report
cat > "$results_dir/baseline_moderate_summary.md" << EOF
# Baseline MODERATE Test Results
Date: $(date '+%Y-%m-%d %H:%M:%S')
Configuration: Claude Native (No Swarm)
Test Level: MODERATE (5-8 minute tests)

## Test Durations
- Test 1b (TaskQueue Class): $duration_1b seconds
- Test 2b (API Debugging): $duration_2b seconds
- Test 3b (Matrix Operations): $duration_3b seconds
- Test 4b (Database Research): $duration_4b seconds
- **Total Time**: $total_duration seconds

## Average Performance
- Average per test: $((total_duration / 4)) seconds
- Expected range: 300-480 seconds (5-8 minutes)

## Quality Assessment (0-10)
Rate each response on these criteria:

### Test 1b - TaskQueue Class:
- [ ] Correct implementation (priority ordering, FIFO within priority)
- [ ] Thread-safety properly implemented
- [ ] Comprehensive error handling
- [ ] Good test coverage (5-7 tests)
- [ ] Clean code with type hints
- Quality Score: ___/10

### Test 2b - API Debugging:
- [ ] Found timestamp mismatch bug
- [ ] Found signature format issue
- [ ] Found caching logic problems
- [ ] Provided complete fix
- [ ] Clear explanation of issues
- Quality Score: ___/10

### Test 3b - Matrix Operations:
- [ ] All methods correctly implemented
- [ ] Proper dimension checking
- [ ] Determinant calculation works
- [ ] Good error handling
- [ ] Comprehensive tests
- Quality Score: ___/10

### Test 4b - Database Research:
- [ ] Thorough comparison of all 4 databases
- [ ] Specific e-commerce considerations
- [ ] Clear architecture recommendations
- [ ] Practical configuration examples
- [ ] Well-justified recommendation
- Quality Score: ___/10

## Overall Assessment
- **Average Quality Score**: ___/10
- **Total Tokens Used**: ___ (check Claude interface)
- **Key Strengths**: 
- **Areas for Improvement**: 

## Notes for Swarm Comparison
These MODERATE tests are more complex than SIMPLE tests:
- More interdependent components
- Require deeper analysis
- Better suited for multi-agent collaboration
- Thread-safety and debugging benefit from multiple perspectives
EOF

echo ""
echo "✅ Baseline MODERATE tests complete!"
echo "📊 Total test time: $total_duration seconds"
echo "📊 Average per test: $((total_duration / 4)) seconds"
echo "📁 Results saved to: $results_dir"
echo ""
echo "📋 Next Steps:"
echo "1. Save all Claude responses to the results directory"
echo "2. Complete quality assessment in the summary file"
echo "3. Note token usage for comparison"
echo "4. Run swarm configurations to compare performance"