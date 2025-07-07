#!/bin/bash
# Run Swarm Configuration B: 3 Agents Hierarchical - Simple Tests

echo "🐝 Running Swarm Config B Tests (3 Agents, Hierarchical Topology)"
echo "================================================================"

# Create timestamp for this test run
timestamp=$(date +%Y%m%d_%H%M%S)
results_dir="bar_testing/test-results/simple/swarm_b_run_$timestamp"
mkdir -p "$results_dir"

echo "📁 Results will be saved to: $results_dir"
echo ""
echo "⚡ IMPORTANT: This test uses hierarchical coordination"
echo ""

# Function to create swarm setup commands
create_swarm_setup() {
    cat > "$results_dir/swarm_setup.txt" << 'EOF'
Use this SINGLE BatchTool message to initialize the swarm:

[BatchTool]:
  mcp__ruv-swarm__swarm_init { 
    topology: "hierarchical", 
    maxAgents: 3, 
    strategy: "specialized" 
  }
  mcp__ruv-swarm__agent_spawn { 
    type: "coordinator", 
    name: "lead-architect",
    capabilities: ["planning", "delegation", "integration"]
  }
  mcp__ruv-swarm__agent_spawn { 
    type: "coder", 
    name: "implementation-expert",
    capabilities: ["coding", "algorithms", "optimization"]
  }
  mcp__ruv-swarm__agent_spawn { 
    type: "analyst", 
    name: "quality-specialist",
    capabilities: ["testing", "validation", "documentation"]
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
echo "📋 Setting up Swarm Configuration B"
create_swarm_setup
echo "Setup instructions saved to: $results_dir/swarm_setup.txt"
echo ""
echo "INSTRUCTIONS:"
echo "1. Initialize the swarm using the commands in swarm_setup.txt"
echo "2. Note: Coordinator will delegate tasks to other agents"
echo "3. Verify with: mcp__ruv-swarm__swarm_status { verbose: true }"
echo ""
read -p "Press Enter when swarm is initialized and ready..."

# Run same tests as Config A but with hierarchical coordination
# [Test code similar to Config A, but emphasizing hierarchical flow]

# Create summary report template
cat > "$results_dir/swarm_b_summary.md" << EOF
# Swarm Configuration B Test Results
Date: $(date '+%Y-%m-%d %H:%M:%S')
Configuration: 3 Agents, Hierarchical Topology

## Hierarchical Flow Observations
- Coordinator planning effectiveness: [Excellent/Good/Fair/Poor]
- Delegation clarity: [Clear/Somewhat clear/Unclear]
- Integration quality: [Seamless/Minor issues/Major issues]

## Test Durations
[Similar structure to Config A]

## Key Differences from Config A (Flat)
- Planning phase overhead: _ seconds
- Integration benefits: 
- Coordination challenges: 

## Overall Assessment
- Best suited for: [Task types that benefit from hierarchical approach]
EOF

echo "✅ Swarm Configuration B tests ready to run!"