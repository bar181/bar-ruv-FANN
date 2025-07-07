#!/bin/bash
# Run Swarm Configuration A2: Two Agents Tests

echo "🐝 Running Swarm Config A2 Tests (2 Agents - Minimal Collaboration)"
echo "==================================================================="

# Create timestamp for this test run
timestamp=$(date +%Y%m%d_%H%M%S)
results_dir="bar_testing/test-results/simple/swarm_a2_run_$timestamp"
mkdir -p "$results_dir"

echo "📁 Results will be saved to: $results_dir"
echo ""
echo "⚡ Testing minimal collaboration with 2-agent configurations"
echo ""

# Function to calculate duration
calculate_duration() {
    local start=$1
    local end=$2
    local duration=$((end - start))
    echo "$duration"
}

# Choose 2-agent configuration
echo "Choose 2-agent configuration to test:"
echo "1) Developer + Tester (mesh topology)"
echo "2) Coordinator + Implementer (hierarchical)"
echo "3) Two Specialists (parallel coding)"
read -p "Enter choice (1-3): " config_choice

case $config_choice in
    1)
        config_name="dev-tester"
        topology="mesh"
        strategy="balanced"
        cat > "$results_dir/swarm_setup.txt" << 'EOF'
Configuration: Developer + Tester

[BatchTool]:
  mcp__ruv-swarm__swarm_init { 
    topology: "mesh", 
    maxAgents: 2, 
    strategy: "balanced" 
  }
  mcp__ruv-swarm__agent_spawn { 
    type: "coder", 
    name: "developer",
    capabilities: ["implementation", "algorithms"]
  }
  mcp__ruv-swarm__agent_spawn { 
    type: "tester", 
    name: "qa-engineer",
    capabilities: ["testing", "validation"]
  }
EOF
        ;;
    2)
        config_name="coord-impl"
        topology="hierarchical"
        strategy="specialized"
        cat > "$results_dir/swarm_setup.txt" << 'EOF'
Configuration: Coordinator + Implementer

[BatchTool]:
  mcp__ruv-swarm__swarm_init { 
    topology: "hierarchical", 
    maxAgents: 2, 
    strategy: "specialized" 
  }
  mcp__ruv-swarm__agent_spawn { 
    type: "coordinator", 
    name: "architect",
    capabilities: ["planning", "design"]
  }
  mcp__ruv-swarm__agent_spawn { 
    type: "coder", 
    name: "implementer",
    capabilities: ["coding", "execution"]
  }
EOF
        ;;
    3)
        config_name="two-specialists"
        topology="mesh"
        strategy="specialized"
        cat > "$results_dir/swarm_setup.txt" << 'EOF'
Configuration: Two Coding Specialists

[BatchTool]:
  mcp__ruv-swarm__swarm_init { 
    topology: "mesh", 
    maxAgents: 2, 
    strategy: "specialized" 
  }
  mcp__ruv-swarm__agent_spawn { 
    type: "coder", 
    name: "algorithm-specialist",
    capabilities: ["algorithms", "optimization"]
  }
  mcp__ruv-swarm__agent_spawn { 
    type: "coder", 
    name: "interface-specialist",
    capabilities: ["api", "validation"]
  }
EOF
        ;;
    *)
        echo "Invalid choice. Using Developer + Tester as default."
        config_name="dev-tester"
        topology="mesh"
        strategy="balanced"
        ;;
esac

echo "📋 Setting up 2-Agent Swarm ($config_name)"
echo "Setup saved to: $results_dir/swarm_setup.txt"
echo ""
read -p "Initialize swarm with above config and press Enter when ready..."

# Run tests
total_start=$(date +%s)

for test in "1a" "2a" "3a" "4a"; do
    echo ""
    echo "▶️  Test $test (2 Agents: $config_name)"
    echo "----------------------------------------"
    
    start_time=$(date +%s)
    
    cp bar_testing/test-results/simple/baseline_run_*/test_${test}_prompt.txt "$results_dir/" 2>/dev/null
    
    echo "⏱️  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "📝 Orchestrate task to 2-agent team"
    echo "💾 Save response to: $results_dir/test_${test}_response.txt"
    read -p "Press Enter when complete..."
    
    end_time=$(date +%s)
    duration=$(calculate_duration $start_time $end_time)
    echo "⏱️  Duration: $duration seconds"
    echo "$duration" > "$results_dir/test_${test}_duration.txt"
done

total_end=$(date +%s)
total_duration=$(calculate_duration $total_start $total_end)

# Create summary report
cat > "$results_dir/swarm_a2_summary.md" << EOF
# Swarm Configuration A2 Test Results
Date: $(date '+%Y-%m-%d %H:%M:%S')
Configuration: 2 Agents ($config_name)
Topology: $topology
Strategy: $strategy

## Test Durations
- Test 1a: $(cat "$results_dir/test_1a_duration.txt" 2>/dev/null || echo "N/A") seconds
- Test 2a: $(cat "$results_dir/test_2a_duration.txt" 2>/dev/null || echo "N/A") seconds
- Test 3a: $(cat "$results_dir/test_3a_duration.txt" 2>/dev/null || echo "N/A") seconds
- Test 4a: $(cat "$results_dir/test_4a_duration.txt" 2>/dev/null || echo "N/A") seconds
- **Total Time**: $total_duration seconds

## Performance vs Other Configs
- vs Baseline (~47.5s avg): [Faster/Slower by X%]
- vs 1 Agent: [Better/Worse]
- vs 3 Agents: [Compare when available]

## Collaboration Effectiveness
- Task division clarity: [Excellent/Good/Fair/Poor]
- Agent coordination: [Seamless/Minor issues/Major issues]
- Work overlap: [None/Some/Significant]
- Integration quality: [Excellent/Good/Fair/Poor]

## Agent Contributions
### Agent 1 contributions:
- 

### Agent 2 contributions:
- 

## Quality Assessment (0-10)
[Standard quality metrics]

## Key Findings
1. Optimal 2-agent pairing for simple tasks: [Which config worked best]
2. Coordination overhead: [Minimal/Moderate/High]
3. Quality improvement over single agent: [Yes/No]
4. Best use case for 2 agents: [Specific scenarios]

## Recommendation
2-agent swarms work best for: [Specific task types]
Not recommended for: [Task types where overhead not justified]
EOF

echo "✅ 2-Agent Swarm tests complete!"
echo "📊 Total test time: $total_duration seconds"
echo "📁 Results saved to: $results_dir"