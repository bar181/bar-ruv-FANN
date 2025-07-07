#!/bin/bash
# Run baseline (Claude Native) simple tests only

echo "🧪 Running Baseline Simple Tests (Claude Native Only)"
echo "===================================================="

# Create timestamp for this test run
timestamp=$(date +%Y%m%d_%H%M%S)
results_dir="bar_testing/test-results/simple/baseline_run_$timestamp"
mkdir -p "$results_dir"

echo "📁 Results will be saved to: $results_dir"
echo ""

# Test 1a: Simple Function Implementation
echo "▶️  Test 1a: Code Generation - Merge Sorted Lists"
echo "------------------------------------------------"
start_time=$(date +%s.%N)

# Create test prompt file
cat > "$results_dir/test_1a_prompt.txt" << 'EOF'
Create a Python function called 'merge_sorted_lists' that:

1. Takes two sorted lists of integers as input
2. Returns a single sorted list containing all elements from both lists
3. Handles edge cases (empty lists, None values)
4. Includes type hints and a docstring
5. Write 3-5 unit tests for the function

Example:
merge_sorted_lists([1, 3, 5], [2, 4, 6]) → [1, 2, 3, 4, 5, 6]
EOF

echo "⏱️  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "📝 Prompt saved to: $results_dir/test_1a_prompt.txt"
echo ""
echo "INSTRUCTIONS:"
echo "1. Copy the prompt from: $results_dir/test_1a_prompt.txt"
echo "2. Paste it into Claude (in your IDE or web interface)"
echo "3. Save the response to: $results_dir/test_1a_response.txt"
echo "4. Record the time when you receive the complete response"
echo ""
read -p "Press Enter when you've saved the response..."

end_time=$(date +%s.%N)
duration=$(echo "$end_time - $start_time" | bc)
echo "⏱️  Duration: $duration seconds"
echo "$duration" > "$results_dir/test_1a_duration.txt"

# Test 2a: Simple Debugging
echo ""
echo "▶️  Test 2a: Debugging - Fix Factorial Function"
echo "----------------------------------------------"
start_time=$(date +%s.%N)

cat > "$results_dir/test_2a_prompt.txt" << 'EOF'
Debug and fix the following Python function that should calculate the factorial of a number:

```python
def factorial(n):
    """Calculate factorial of n (n!)"""
    if n < 0:
        return "Error: Negative number"
    
    result = 0  # Bug 1: Should be 1
    for i in range(1, n):  # Bug 2: Should be range(1, n+1)
        result *= i
    
    return result

# Test cases that are failing:
assert factorial(0) == 1  # Returns 0
assert factorial(5) == 120  # Returns 0
assert factorial(1) == 1  # Returns 0
```

Requirements:
1. Identify and fix all bugs
2. Explain what was wrong
3. Add 2-3 more test cases
4. Ensure the function handles edge cases properly
EOF

echo "⏱️  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "📝 Prompt saved to: $results_dir/test_2a_prompt.txt"
echo ""
echo "INSTRUCTIONS: Same as before - copy prompt, get response, save it"
echo "Save response to: $results_dir/test_2a_response.txt"
echo ""
read -p "Press Enter when you've saved the response..."

end_time=$(date +%s.%N)
duration=$(echo "$end_time - $start_time" | bc)
echo "⏱️  Duration: $duration seconds"
echo "$duration" > "$results_dir/test_2a_duration.txt"

# Test 3a: Simple Math Optimization
echo ""
echo "▶️  Test 3a: Mathematical Problem - Fence Optimization"
echo "-----------------------------------------------------"
start_time=$(date +%s.%N)

cat > "$results_dir/test_3a_prompt.txt" << 'EOF'
Solve the following optimization problem:

A farmer has 100 meters of fencing and wants to create a rectangular enclosure 
against a straight wall (so only 3 sides need fencing).

1. Find the dimensions that maximize the enclosed area
2. Prove your answer is optimal using calculus
3. Implement a Python function that:
   - Takes fence_length as input
   - Returns optimal dimensions (width, length) and maximum area
   - Validates inputs (positive fence length)
4. Create a simple visualization showing the area vs. width relationship

Example: maximize_enclosure(100) → (width=25, length=50, area=1250)
EOF

echo "⏱️  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "📝 Prompt saved to: $results_dir/test_3a_prompt.txt"
echo ""
echo "INSTRUCTIONS: Same process"
echo "Save response to: $results_dir/test_3a_response.txt"
echo ""
read -p "Press Enter when you've saved the response..."

end_time=$(date +%s.%N)
duration=$(echo "$end_time - $start_time" | bc)
echo "⏱️  Duration: $duration seconds"
echo "$duration" > "$results_dir/test_3a_duration.txt"

# Test 4a: Simple Research
echo ""
echo "▶️  Test 4a: Research & Analysis - Framework Comparison"
echo "------------------------------------------------------"
start_time=$(date +%s.%N)

cat > "$results_dir/test_4a_prompt.txt" << 'EOF'
Compare Python async frameworks for building a simple REST API:

Compare these 3 frameworks:
1. FastAPI
2. Aiohttp
3. Sanic

For each framework, briefly analyze:
- Ease of use for beginners
- Performance characteristics
- Built-in features (validation, docs, etc.)
- Community support

Provide:
1. A comparison table
2. Simple "Hello World" API example for each
3. Recommendation based on these criteria:
   - Team has moderate Python experience
   - Need automatic API documentation
   - Expecting <1000 requests/second
   - Want minimal dependencies

Keep response concise - focus on practical differences.
EOF

echo "⏱️  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "📝 Prompt saved to: $results_dir/test_4a_prompt.txt"
echo ""
echo "INSTRUCTIONS: Same process"
echo "Save response to: $results_dir/test_4a_response.txt"
echo ""
read -p "Press Enter when you've saved the response..."

end_time=$(date +%s.%N)
duration=$(echo "$end_time - $start_time" | bc)
echo "⏱️  Duration: $duration seconds"
echo "$duration" > "$results_dir/test_4a_duration.txt"

# Create summary report
echo ""
echo "📊 Creating Summary Report..."

cat > "$results_dir/baseline_summary.md" << EOF
# Baseline Test Results Summary
Date: $(date '+%Y-%m-%d %H:%M:%S')

## Test Durations
- Test 1a (Code Generation): $(cat "$results_dir/test_1a_duration.txt" 2>/dev/null || echo "N/A") seconds
- Test 2a (Debugging): $(cat "$results_dir/test_2a_duration.txt" 2>/dev/null || echo "N/A") seconds
- Test 3a (Math): $(cat "$results_dir/test_3a_duration.txt" 2>/dev/null || echo "N/A") seconds
- Test 4a (Research): $(cat "$results_dir/test_4a_duration.txt" 2>/dev/null || echo "N/A") seconds

## Quality Assessment
Please manually evaluate each response on a scale of 0-10 for:
- Correctness
- Completeness
- Code Quality
- Documentation

## Token Usage
Please record token counts from Claude interface if available:
- Input tokens per test
- Output tokens per test

## Notes
Add any observations here.
EOF

echo "✅ Baseline tests complete!"
echo "📁 All results saved to: $results_dir"
echo ""
echo "Next steps:"
echo "1. Review responses for quality"
echo "2. Fill in the quality assessment in: $results_dir/baseline_summary.md"
echo "3. Run swarm configuration tests to compare"