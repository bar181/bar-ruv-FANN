#!/bin/bash
# Run Swarm Configuration A1: Single Agent Tests

echo "🐝 Running Swarm Config A1 Tests (1 Agent - Swarm Overhead Test)"
echo "================================================================="

# Create timestamp for this test run
timestamp=$(date +%Y%m%d_%H%M%S)
results_dir="bar_testing/test-results/simple/swarm_a1_run_$timestamp"
mkdir -p "$results_dir"

echo "📁 Results will be saved to: $results_dir"
echo ""
echo "⚡ Testing swarm overhead with single agent configurations"
echo ""

# Function to calculate duration
calculate_duration() {
    local start=$1
    local end=$2
    local duration=$((end - start))
    echo "$duration"
}

# Test with different single agent types
echo "Choose single agent type to test:"
echo "1) Coder (solo-developer)"
echo "2) Coordinator (solo-architect)"
echo "3) Researcher (solo-analyst)"
read -p "Enter choice (1-3): " agent_choice

case $agent_choice in
    1)
        agent_type="coder"
        agent_name="solo-developer"
        capabilities='["coding", "testing", "documentation"]'
        ;;
    2)
        agent_type="coordinator"
        agent_name="solo-architect"
        capabilities='["planning", "implementation", "review"]'
        ;;
    3)
        agent_type="researcher"
        agent_name="solo-analyst"
        capabilities='["analysis", "implementation", "validation"]'
        ;;
    *)
        echo "Invalid choice. Using coder as default."
        agent_type="coder"
        agent_name="solo-developer"
        capabilities='["coding", "testing", "documentation"]'
        ;;
esac

# Create swarm setup
cat > "$results_dir/swarm_setup.txt" << EOF
Single Agent Configuration: $agent_type

[BatchTool]:
  mcp__ruv-swarm__swarm_init { 
    topology: "star", 
    maxAgents: 1, 
    strategy: "specialized" 
  }
  mcp__ruv-swarm__agent_spawn { 
    type: "$agent_type", 
    name: "$agent_name",
    capabilities: $capabilities
  }
EOF

echo "📋 Setting up Single Agent Swarm ($agent_type)"
echo "Setup saved to: $results_dir/swarm_setup.txt"
echo ""
read -p "Initialize swarm with above config and press Enter when ready..."

# Run same tests as baseline to compare overhead
echo ""
echo "Running simple tests with single agent swarm..."
echo "Compare these times with baseline to measure swarm overhead."
echo ""

# Test tracking
total_start=$(date +%s)

# Copy test prompts and run tests
for test in "1a" "2a" "3a" "4a"; do
    echo "▶️  Test $test (Single Agent: $agent_type)"
    echo "----------------------------------------"
    
    start_time=$(date +%s)
    
    # Copy prompt from baseline
    cp bar_testing/test-results/simple/baseline_run_*/test_${test}_prompt.txt "$results_dir/" 2>/dev/null
    
    echo "⏱️  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "📝 Orchestrate task to single agent"
    echo "💾 Save response to: $results_dir/test_${test}_response.txt"
    read -p "Press Enter when complete..."
    
    end_time=$(date +%s)
    duration=$(calculate_duration $start_time $end_time)
    echo "⏱️  Duration: $duration seconds"
    echo "$duration" > "$results_dir/test_${test}_duration.txt"
    echo ""
done

total_end=$(date +%s)
total_duration=$(calculate_duration $total_start $total_end)

# Create summary report
cat > "$results_dir/swarm_a1_summary.md" << EOF
# Swarm Configuration A1 Test Results
Date: $(date '+%Y-%m-%d %H:%M:%S')
Configuration: 1 Agent ($agent_type) - Swarm Overhead Test

## Agent Configuration
- Type: $agent_type
- Name: $agent_name
- Capabilities: $capabilities

## Test Durations
- Test 1a: $(cat "$results_dir/test_1a_duration.txt" 2>/dev/null || echo "N/A") seconds
- Test 2a: $(cat "$results_dir/test_2a_duration.txt" 2>/dev/null || echo "N/A") seconds
- Test 3a: $(cat "$results_dir/test_3a_duration.txt" 2>/dev/null || echo "N/A") seconds
- Test 4a: $(cat "$results_dir/test_4a_duration.txt" 2>/dev/null || echo "N/A") seconds
- **Total Time**: $total_duration seconds

## Overhead Analysis vs Baseline
- Baseline average: ~47.5 seconds per test
- Single agent average: [Calculate]
- **Swarm overhead**: [X seconds or Y%]

## Key Questions
1. Is there any benefit to using swarm with 1 agent? [Yes/No]
2. Does agent type affect performance? [$agent_type performance]
3. Quality compared to baseline: [Same/Better/Worse]
4. Token usage compared to baseline: [Higher/Same/Lower]

## Quality Assessment (0-10)
[Same format as baseline for comparison]

## Observations
### Swarm Infrastructure Cost:
- 

### Agent Type Effectiveness:
- 

### When Single Agent Swarm Makes Sense:
- 

## Recommendation
Use single agent swarm when: [Specific scenarios if any]
Otherwise use: [Claude Native baseline]
EOF

echo "✅ Single Agent Swarm tests complete!"
echo "📊 Total test time: $total_duration seconds"
echo "📁 Results saved to: $results_dir"
echo ""
echo "Next: Compare with baseline to measure pure swarm overhead"