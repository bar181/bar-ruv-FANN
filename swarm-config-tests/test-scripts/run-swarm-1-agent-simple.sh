#!/bin/bash
# Run 1-Agent Swarm Tests (Simple) - Measuring Pure Swarm Overhead

echo "🐝 Running 1-Agent Swarm Tests (Simple Tasks)"
echo "=============================================="
echo ""
echo "⚡ Testing swarm infrastructure overhead with minimal coordination"
echo "🎯 Expected: 5-10% overhead compared to baseline"
echo ""

# Create timestamp for this test run
timestamp=$(date +%Y%m%d_%H%M%S)
results_dir="bar_testing/test-results/simple/swarm_1agent_run_$timestamp"
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

# Create swarm setup instructions
cat > "$results_dir/swarm_setup.txt" << 'EOF'
1-AGENT SWARM CONFIGURATION

Purpose: Measure pure swarm infrastructure overhead
Expected overhead: 5-10% over baseline

MANDATORY: Use BatchTool for ALL operations in ONE message:

[BatchTool]:
  mcp__ruv-swarm__swarm_init { 
    topology: "star", 
    maxAgents: 1, 
    strategy: "specialized" 
  }
  mcp__ruv-swarm__agent_spawn { 
    type: "coder",
    name: "solo-developer",
    capabilities: ["coding", "testing", "documentation", "review"]
  }
  mcp__ruv-swarm__memory_usage {
    action: "store",
    key: "swarm/1-agent/config",
    value: { 
      "test_run": "simple_tests",
      "timestamp": Date.now(),
      "purpose": "overhead_measurement"
    }
  }

CRITICAL: The spawned agent MUST use these coordination hooks:
1. npx ruv-swarm hook pre-task --description "[task]"
2. npx ruv-swarm hook post-edit --file "[file]" (after EVERY file operation)
3. npx ruv-swarm hook post-task --task-id "[task]"
EOF

echo "📋 1-Agent Swarm Setup Instructions"
echo "==================================="
cat "$results_dir/swarm_setup.txt"
echo ""
echo "==================================="
echo ""
read -p "Initialize 1-agent swarm with above config and press Enter when ready..."

# Run tests
total_start=$(date +%s)

echo ""
echo "📊 Running Simple Tests with 1-Agent Swarm"
echo "Expected behavior:"
echo "  - Single agent handles all aspects"
echo "  - Memory persistence for context"
echo "  - Hooks for automation"
echo "  - Minimal coordination overhead"
echo ""

# Test 1a: Code Generation
echo "▶️  Test 1a: Code Generation (1 Agent)"
echo "-------------------------------------"
echo "Expected: ~11-12 seconds (baseline: 10s + overhead)"
echo ""

# Copy baseline prompt
if [ -d "bar_testing/test-results/simple/baseline_run_"* ]; then
    cp bar_testing/test-results/simple/baseline_run_*/test_1a_prompt.txt "$results_dir/" 2>/dev/null
fi

start_1a=$(date +%s)
cat << 'EOF'
Orchestrate this task with your 1-agent swarm:

mcp__ruv-swarm__task_orchestrate { 
  task: "Implement merge_sorted_lists function with tests and documentation",
  strategy: "adaptive",
  maxAgents: 1,
  priority: "high"
}

The agent should:
1. Run pre-task hook
2. Implement the function
3. Run post-edit hook after creating the file
4. Add tests
5. Run post-task hook

Monitor with: mcp__ruv-swarm__swarm_monitor { duration: 20, interval: 5 }
EOF
echo ""
echo "💾 Save response to: $results_dir/test_1a_response.txt"
read -p "Press Enter when complete..."
end_1a=$(date +%s)
duration_1a=$(calculate_duration $start_1a $end_1a)
echo "⏱️  Duration: $duration_1a seconds"
echo "$duration_1a" > "$results_dir/test_1a_duration.txt"
echo ""

# Test 2a: Debugging
echo "▶️  Test 2a: Debugging (1 Agent)"
echo "-------------------------------"
echo "Expected: ~13-14 seconds (baseline: 12s + overhead)"
echo ""

if [ -d "bar_testing/test-results/simple/baseline_run_"* ]; then
    cp bar_testing/test-results/simple/baseline_run_*/test_2a_prompt.txt "$results_dir/" 2>/dev/null
fi

start_2a=$(date +%s)
cat << 'EOF'
Orchestrate debugging task:

mcp__ruv-swarm__task_orchestrate { 
  task: "Debug and fix the factorial function, explain issues, provide tests",
  strategy: "adaptive",
  maxAgents: 1,
  priority: "high"
}

Ensure agent uses memory to store findings:
mcp__ruv-swarm__memory_usage {
  action: "store",
  key: "debug/factorial/bugs",
  value: { "bugs_found": [...], "fixes": [...] }
}
EOF
echo ""
echo "💾 Save response to: $results_dir/test_2a_response.txt"
read -p "Press Enter when complete..."
end_2a=$(date +%s)
duration_2a=$(calculate_duration $start_2a $end_2a)
echo "⏱️  Duration: $duration_2a seconds"
echo "$duration_2a" > "$results_dir/test_2a_duration.txt"
echo ""

# Test 3a: Mathematical Problem
echo "▶️  Test 3a: Mathematical Problem (1 Agent)"
echo "-----------------------------------------"
echo "Expected: ~19-20 seconds (baseline: 18s + overhead)"
echo ""

if [ -d "bar_testing/test-results/simple/baseline_run_"* ]; then
    cp bar_testing/test-results/simple/baseline_run_*/test_3a_prompt.txt "$results_dir/" 2>/dev/null
fi

start_3a=$(date +%s)
cat << 'EOF'
Orchestrate math problem:

[BatchTool]:
  mcp__ruv-swarm__task_orchestrate { 
    task: "Solve fence optimization problem with mathematical derivation and Python implementation",
    strategy: "adaptive",
    maxAgents: 1
  }
  mcp__ruv-swarm__memory_usage {
    action: "store",
    key: "math/fence/solution",
    value: { "approach": "calculus", "result": "50x25=1250" }
  }

Check metrics: mcp__ruv-swarm__agent_metrics { metric: "all" }
EOF
echo ""
echo "💾 Save response to: $results_dir/test_3a_response.txt"
read -p "Press Enter when complete..."
end_3a=$(date +%s)
duration_3a=$(calculate_duration $start_3a $end_3a)
echo "⏱️  Duration: $duration_3a seconds"
echo "$duration_3a" > "$results_dir/test_3a_duration.txt"
echo ""

# Test 4a: Research
echo "▶️  Test 4a: Research & Analysis (1 Agent)"
echo "----------------------------------------"
echo "Expected: ~16-17 seconds (baseline: 15s + overhead)"
echo ""

if [ -d "bar_testing/test-results/simple/baseline_run_"* ]; then
    cp bar_testing/test-results/simple/baseline_run_*/test_4a_prompt.txt "$results_dir/" 2>/dev/null
fi

start_4a=$(date +%s)
cat << 'EOF'
Final orchestration:

mcp__ruv-swarm__task_orchestrate { 
  task: "Research and compare FastAPI, Aiohttp, Sanic for REST APIs with recommendation",
  strategy: "adaptive",
  maxAgents: 1
}

Get final metrics:
mcp__ruv-swarm__swarm_status { verbose: true }
mcp__ruv-swarm__memory_usage { action: "list", pattern: "*" }
EOF
echo ""
echo "💾 Save response to: $results_dir/test_4a_response.txt"
read -p "Press Enter when complete..."
end_4a=$(date +%s)
duration_4a=$(calculate_duration $start_4a $end_4a)
echo "⏱️  Duration: $duration_4a seconds"
echo "$duration_4a" > "$results_dir/test_4a_duration.txt"

# Calculate totals
total_end=$(date +%s)
total_duration=$(calculate_duration $total_start $total_end)

# Create summary
cat > "$results_dir/swarm_1agent_summary.md" << EOF
# 1-Agent Swarm Test Results
Date: $(date '+%Y-%m-%d %H:%M:%S')
Configuration: 1 Agent Swarm (Overhead Measurement)
Topology: Star (minimal coordination)
Strategy: Specialized

## Test Durations
- Test 1a: $duration_1a seconds (baseline: 10s)
- Test 2a: $duration_2a seconds (baseline: 12s)
- Test 3a: $duration_3a seconds (baseline: 18s)
- Test 4a: $duration_4a seconds (baseline: 15s)
- **Total Time**: $total_duration seconds (baseline: 55s)

## Overhead Analysis
- Test 1a overhead: $((duration_1a - 10)) seconds ($((100 * (duration_1a - 10) / 10))%)
- Test 2a overhead: $((duration_2a - 12)) seconds ($((100 * (duration_2a - 12) / 12))%)
- Test 3a overhead: $((duration_3a - 18)) seconds ($((100 * (duration_3a - 18) / 18))%)
- Test 4a overhead: $((duration_4a - 15)) seconds ($((100 * (duration_4a - 15) / 15))%)
- **Average Overhead**: $(((duration_1a + duration_2a + duration_3a + duration_4a - 55) * 100 / 55))%

## Quality Assessment
[To be filled after reviewing responses]

## Key Observations
1. Swarm initialization time: 
2. Memory operation overhead: 
3. Hook execution impact: 
4. Overall coordination cost: 

## Benefits Observed
- [ ] Memory persistence working
- [ ] Hooks executed successfully
- [ ] Metrics collected properly
- [ ] Neural training occurred

## Comparison to Baseline
- Speed: [X% slower due to infrastructure]
- Quality: [Same/Better/Worse]
- Additional features: [Memory, hooks, metrics]

## Conclusion
1-agent swarm overhead is [acceptable/high] at X%.
Main value comes from [memory/hooks/metrics] rather than coordination.
EOF

echo ""
echo "✅ 1-Agent Swarm tests complete!"
echo "📊 Total time: $total_duration seconds (baseline: 55s)"
echo "📊 Overhead: $((100 * (total_duration - 55) / 55))%"
echo "📁 Results saved to: $results_dir"
echo ""
echo "Next: Review if 5-10% overhead target was met and whether benefits justify it"