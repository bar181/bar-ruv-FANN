#!/bin/bash
# Run Swarm Configuration A: 3 Agents Flat - Simple Tests

echo "🐝 Running Swarm Config A Tests (3 Agents, Flat Topology)"
echo "========================================================"

# Create timestamp for this test run
timestamp=$(date +%Y%m%d_%H%M%S)
results_dir="bar_testing/test-results/simple/swarm_a_run_$timestamp"
mkdir -p "$results_dir"

echo "📁 Results will be saved to: $results_dir"
echo ""
echo "⚡ IMPORTANT: This test requires parallel execution using BatchTool"
echo ""

# Function to create swarm setup commands
create_swarm_setup() {
    cat > "$results_dir/swarm_setup.txt" << 'EOF'
Use this SINGLE BatchTool message to initialize the swarm:

[BatchTool]:
  mcp__ruv-swarm__swarm_init { 
    topology: "mesh", 
    maxAgents: 3, 
    strategy: "balanced" 
  }
  mcp__ruv-swarm__agent_spawn { 
    type: "coder", 
    name: "implementation-specialist",
    capabilities: ["coding", "algorithms", "data-structures"]
  }
  mcp__ruv-swarm__agent_spawn { 
    type: "tester", 
    name: "quality-assurance",
    capabilities: ["testing", "validation", "edge-cases"]
  }
  mcp__ruv-swarm__agent_spawn { 
    type: "analyst", 
    name: "code-reviewer",
    capabilities: ["review", "optimization", "documentation"]
  }
EOF
}

# Function to calculate duration
calculate_duration() {
    local start=$1
    local end=$2
    local duration=$((end - start))
    echo "$duration"
}

# Setup swarm first
echo "📋 Setting up Swarm Configuration A"
create_swarm_setup
echo "Setup instructions saved to: $results_dir/swarm_setup.txt"
echo ""
echo "INSTRUCTIONS:"
echo "1. Initialize the swarm using the commands in swarm_setup.txt"
echo "2. Verify swarm is ready with: mcp__ruv-swarm__swarm_status { verbose: true }"
echo ""
read -p "Press Enter when swarm is initialized and ready..."

# Test 1a: Code Generation
echo ""
echo "▶️  Test 1a: Code Generation - Merge Sorted Lists (Swarm A)"
echo "--------------------------------------------------------"
start_time=$(date +%s)

# Copy prompt from baseline
cp bar_testing/test-results/simple/baseline_run_*/test_1a_prompt.txt "$results_dir/" 2>/dev/null || \
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

cat > "$results_dir/test_1a_orchestrate.txt" << 'EOF'
mcp__ruv-swarm__task_orchestrate {
  task: "Create a Python function called 'merge_sorted_lists' that: 1. Takes two sorted lists of integers as input 2. Returns a single sorted list containing all elements from both lists 3. Handles edge cases (empty lists, None values) 4. Includes type hints and a docstring 5. Write 3-5 unit tests for the function. Example: merge_sorted_lists([1, 3, 5], [2, 4, 6]) → [1, 2, 3, 4, 5, 6]",
  priority: "medium",
  strategy: "parallel",
  maxAgents: 3
}
EOF

echo "⏱️  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "📝 Use the orchestrate command from: $results_dir/test_1a_orchestrate.txt"
echo "💾 Then get results with: mcp__ruv-swarm__task_results { taskId: \"<task-id>\", format: \"detailed\" }"
echo ""
read -p "Press Enter when you've saved the swarm response to test_1a_response.txt..."

end_time=$(date +%s)
duration=$(calculate_duration $start_time $end_time)
echo "⏱️  Duration: $duration seconds"
echo "$duration" > "$results_dir/test_1a_duration.txt"

# Repeat for other tests...
# Test 2a: Debugging
echo ""
echo "▶️  Test 2a: Debugging - Fix Factorial Function (Swarm A)"
echo "-------------------------------------------------------"
start_time=$(date +%s)

cp bar_testing/test-results/simple/baseline_run_*/test_2a_prompt.txt "$results_dir/" 2>/dev/null

echo "⏱️  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "📝 Orchestrate the debugging task to the swarm"
echo "💾 Save response to: $results_dir/test_2a_response.txt"
echo ""
read -p "Press Enter when complete..."

end_time=$(date +%s)
duration=$(calculate_duration $start_time $end_time)
echo "⏱️  Duration: $duration seconds"
echo "$duration" > "$results_dir/test_2a_duration.txt"

# Test 3a: Math Problem
echo ""
echo "▶️  Test 3a: Mathematical Problem - Fence Optimization (Swarm A)"
echo "--------------------------------------------------------------"
start_time=$(date +%s)

cp bar_testing/test-results/simple/baseline_run_*/test_3a_prompt.txt "$results_dir/" 2>/dev/null

echo "⏱️  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "📝 Orchestrate the math problem to the swarm"
echo "💾 Save response to: $results_dir/test_3a_response.txt"
echo ""
read -p "Press Enter when complete..."

end_time=$(date +%s)
duration=$(calculate_duration $start_time $end_time)
echo "⏱️  Duration: $duration seconds"
echo "$duration" > "$results_dir/test_3a_duration.txt"

# Test 4a: Research
echo ""
echo "▶️  Test 4a: Research & Analysis - Framework Comparison (Swarm A)"
echo "---------------------------------------------------------------"
start_time=$(date +%s)

cp bar_testing/test-results/simple/baseline_run_*/test_4a_prompt.txt "$results_dir/" 2>/dev/null

echo "⏱️  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "📝 Orchestrate the research task to the swarm"
echo "💾 Save response to: $results_dir/test_4a_response.txt"
echo ""
read -p "Press Enter when complete..."

end_time=$(date +%s)
duration=$(calculate_duration $start_time $end_time)
echo "⏱️  Duration: $duration seconds"
echo "$duration" > "$results_dir/test_4a_duration.txt"

# Get swarm metrics
echo ""
echo "📊 Collecting Swarm Metrics..."
cat > "$results_dir/collect_metrics.txt" << 'EOF'
Use these commands to collect final metrics:

mcp__ruv-swarm__agent_metrics { metric: "all" }
mcp__ruv-swarm__memory_usage { detail: "summary" }
mcp__ruv-swarm__swarm_status { verbose: true }
EOF

# Create summary report
echo ""
echo "📊 Creating Summary Report..."

cat > "$results_dir/swarm_a_summary.md" << EOF
# Swarm Configuration A Test Results
Date: $(date '+%Y-%m-%d %H:%M:%S')
Configuration: 3 Agents, Flat Topology (Mesh)

## Test Durations
- Test 1a (Code Generation): $(cat "$results_dir/test_1a_duration.txt" 2>/dev/null || echo "N/A") seconds
- Test 2a (Debugging): $(cat "$results_dir/test_2a_duration.txt" 2>/dev/null || echo "N/A") seconds
- Test 3a (Math): $(cat "$results_dir/test_3a_duration.txt" 2>/dev/null || echo "N/A") seconds
- Test 4a (Research): $(cat "$results_dir/test_4a_duration.txt" 2>/dev/null || echo "N/A") seconds

## Comparison to Baseline
- Baseline average: ~47.5 seconds
- Swarm A average: [Calculate after tests]
- Speedup factor: [Calculate]

## Quality Assessment (0-10 scale)
### Test 1a:
- Correctness: _/10
- Completeness: _/10
- Code Quality: _/10
- Documentation: _/10

### Test 2a:
- Correctness: _/10
- Completeness: _/10
- Code Quality: _/10
- Documentation: _/10

### Test 3a:
- Correctness: _/10
- Completeness: _/10
- Code Quality: _/10
- Documentation: _/10

### Test 4a:
- Correctness: _/10
- Completeness: _/10
- Code Quality: _/10
- Documentation: _/10

## Agent Collaboration Metrics
- Task distribution effectiveness: [Good/Fair/Poor]
- Integration quality: [Seamless/Minor issues/Major issues]
- Agent specialization benefit: [High/Medium/Low]

## Token Usage
- Total input tokens: _
- Total output tokens: _
- Compared to baseline (3160): [Higher/Lower by X%]

## Coordination Observations
### What worked well:
- 

### Challenges encountered:
- 

### Agent contribution breakdown:
- Coder: 
- Tester: 
- Analyst: 

## Overall Assessment
- Quality vs Baseline: [Better/Same/Worse]
- Speed vs Baseline: [Faster/Same/Slower]
- Token Efficiency: [Better/Same/Worse]
- **Recommendation**: [When to use this configuration]
EOF

echo "✅ Swarm Configuration A tests complete!"
echo "📁 All results saved to: $results_dir"
echo ""
echo "Next steps:"
echo "1. Review and compare agent outputs"
echo "2. Fill in quality assessments"
echo "3. Analyze coordination patterns"
echo "4. Compare with baseline results"