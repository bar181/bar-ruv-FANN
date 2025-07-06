#!/bin/bash
# Run Swarm Configuration E: 8 Agents (Balanced Dual Teams)

echo "🐝 Running Swarm Config E Tests (8 Agents - Dual Team Structure)"
echo "================================================================"

# Create timestamp for this test run
timestamp=$(date +%Y%m%d_%H%M%S)
results_dir="bar_testing/test-results/simple/swarm_e_run_$timestamp"
mkdir -p "$results_dir"

echo "📁 Results will be saved to: $results_dir"
echo ""
echo "⚡ Testing dual-team coordination with 8 agents"
echo ""

# Create swarm setup
cat > "$results_dir/swarm_setup.txt" << 'EOF'
Configuration: 8 Agents - Balanced Dual Teams

[BatchTool]:
  mcp__ruv-swarm__swarm_init { 
    topology: "hierarchical", 
    maxAgents: 8, 
    strategy: "balanced" 
  }
  // Leadership
  mcp__ruv-swarm__agent_spawn { type: "coordinator", name: "team-lead" }
  
  // Development team (3)
  mcp__ruv-swarm__agent_spawn { type: "coder", name: "senior-dev" }
  mcp__ruv-swarm__agent_spawn { type: "coder", name: "backend-dev" }
  mcp__ruv-swarm__agent_spawn { type: "coder", name: "frontend-dev" }
  
  // Quality team (3)
  mcp__ruv-swarm__agent_spawn { type: "tester", name: "qa-lead" }
  mcp__ruv-swarm__agent_spawn { type: "tester", name: "test-automation" }
  mcp__ruv-swarm__agent_spawn { type: "analyst", name: "code-reviewer" }
  
  // Support
  mcp__ruv-swarm__agent_spawn { type: "researcher", name: "tech-researcher" }
EOF

echo "📋 Setting up 8-Agent Swarm (Dual Teams)"
echo "Setup saved to: $results_dir/swarm_setup.txt"
echo ""
echo "⚠️  WARNING: This configuration may take longer to initialize"
read -p "Initialize swarm with above config and press Enter when ready..."

# Function to calculate duration
calculate_duration() {
    local start=$1
    local end=$2
    local duration=$((end - start))
    echo "$duration"
}

# Run tests
total_start=$(date +%s)

echo ""
echo "📊 Note: With 8 agents, expect more complex coordination patterns"
echo ""

for test in "1a" "2a" "3a" "4a"; do
    echo "▶️  Test $test (8 Agents: Dual Teams)"
    echo "-------------------------------------"
    
    start_time=$(date +%s)
    
    cp bar_testing/test-results/simple/baseline_run_*/test_${test}_prompt.txt "$results_dir/" 2>/dev/null
    
    echo "⏱️  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "📝 Orchestrate task to 8-agent swarm"
    echo "👥 Expected: Dev team handles implementation, QA team handles validation"
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
cat > "$results_dir/swarm_e_summary.md" << EOF
# Swarm Configuration E Test Results
Date: $(date '+%Y-%m-%d %H:%M:%S')
Configuration: 8 Agents - Balanced Dual Teams
Topology: Hierarchical
Team Structure: 1 Lead + 3 Dev + 3 QA + 1 Research

## Test Durations
- Test 1a: $(cat "$results_dir/test_1a_duration.txt" 2>/dev/null || echo "N/A") seconds
- Test 2a: $(cat "$results_dir/test_2a_duration.txt" 2>/dev/null || echo "N/A") seconds
- Test 3a: $(cat "$results_dir/test_3a_duration.txt" 2>/dev/null || echo "N/A") seconds
- Test 4a: $(cat "$results_dir/test_4a_duration.txt" 2>/dev/null || echo "N/A") seconds
- **Total Time**: $total_duration seconds

## Team Dynamics Analysis
### Development Team Performance:
- Senior dev leadership: [Effective/Moderate/Poor]
- Backend/Frontend coordination: [Excellent/Good/Fair/Poor]
- Code quality produced: [High/Medium/Low]

### Quality Team Performance:
- Test coverage: [Comprehensive/Good/Basic]
- Bug detection: [Excellent/Good/Fair]
- Integration with dev team: [Seamless/Some friction/Poor]

### Leadership & Support:
- Team lead effectiveness: [Strong/Moderate/Weak]
- Researcher contributions: [Valuable/Some/Minimal]

## Coordination Metrics
- Inter-team communication: [Smooth/Some delays/Bottlenecks]
- Task handoffs: [Clean/Some confusion/Problematic]
- Parallel execution efficiency: [High/Medium/Low]
- **Coordination overhead**: [X% of total time]

## Comparison Analysis
- vs Baseline (~47.5s): [X% slower/faster]
- vs 3 agents: [Compare efficiency]
- vs 5 agents: [Compare quality and speed]
- **Optimal team size finding**: [Is 8 too many for simple tasks?]

## Quality Assessment (0-10)
[Standard metrics plus team-specific quality measures]

## Key Observations
1. Team separation benefits: 
2. Communication bottlenecks: 
3. Unexpected emergent behaviors: 
4. Diminishing returns evidence: 

## Recommendations
8-agent teams excel at: [Complex multi-faceted tasks]
Not efficient for: [Simple tasks where overhead dominates]
Sweet spot: [Task complexity level where 8 agents shine]
EOF

echo "✅ 8-Agent Swarm tests complete!"
echo "📊 Total test time: $total_duration seconds"
echo "📁 Results saved to: $results_dir"
echo ""
echo "Analysis: Check if dual-team structure provides benefits or just overhead"