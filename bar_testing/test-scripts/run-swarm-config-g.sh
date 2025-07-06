#!/bin/bash
# Run Swarm Configuration G: 12 Agents (Department Structure)

echo "🐝 Running Swarm Config G Tests (12 Agents - Department Structure)"
echo "=================================================================="

# Create timestamp for this test run
timestamp=$(date +%Y%m%d_%H%M%S)
results_dir="bar_testing/test-results/simple/swarm_g_run_$timestamp"
mkdir -p "$results_dir"

echo "📁 Results will be saved to: $results_dir"
echo ""
echo "⚡ Testing corporate-style hierarchical organization with 12 agents"
echo ""

# Create swarm setup
cat > "$results_dir/swarm_setup.txt" << 'EOF'
Configuration: 12 Agents - Department Structure

[BatchTool]:
  mcp__ruv-swarm__swarm_init { 
    topology: "hierarchical", 
    maxAgents: 12, 
    strategy: "specialized" 
  }
  // Executive level
  mcp__ruv-swarm__agent_spawn { type: "coordinator", name: "cto" }
  
  // Department heads (3)
  mcp__ruv-swarm__agent_spawn { type: "coordinator", name: "dev-manager" }
  mcp__ruv-swarm__agent_spawn { type: "coordinator", name: "qa-manager" }
  mcp__ruv-swarm__agent_spawn { type: "coordinator", name: "research-lead" }
  
  // Development dept (4)
  mcp__ruv-swarm__agent_spawn { type: "coder", name: "backend-lead" }
  mcp__ruv-swarm__agent_spawn { type: "coder", name: "frontend-lead" }
  mcp__ruv-swarm__agent_spawn { type: "coder", name: "dev-1" }
  mcp__ruv-swarm__agent_spawn { type: "coder", name: "dev-2" }
  
  // QA dept (2)
  mcp__ruv-swarm__agent_spawn { type: "tester", name: "qa-engineer-1" }
  mcp__ruv-swarm__agent_spawn { type: "tester", name: "qa-engineer-2" }
  
  // Research dept (2)
  mcp__ruv-swarm__agent_spawn { type: "researcher", name: "researcher-1" }
  mcp__ruv-swarm__agent_spawn { type: "analyst", name: "analyst-1" }
EOF

echo "📋 Setting up 12-Agent Swarm (Department Structure)"
echo "Setup saved to: $results_dir/swarm_setup.txt"
echo ""
echo "⚠️  WARNING: High coordination overhead expected with department silos"
echo "⚠️  This configuration models corporate bureaucracy"
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
echo "📊 Note: With 12 agents in departments, expect:"
echo "   - Multiple management layers"
echo "   - Department silos affecting communication"
echo "   - Significant coordination overhead"
echo ""

for test in "1a" "2a" "3a" "4a"; do
    echo "▶️  Test $test (12 Agents: Department Structure)"
    echo "-------------------------------------"
    
    start_time=$(date +%s)
    
    cp bar_testing/test-results/simple/baseline_run_*/test_${test}_prompt.txt "$results_dir/" 2>/dev/null
    
    echo "⏱️  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "📝 Orchestrate task through department hierarchy"
    echo "👥 Expected flow: CTO → Dept Heads → Teams"
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
cat > "$results_dir/swarm_g_summary.md" << EOF
# Swarm Configuration G Test Results
Date: $(date '+%Y-%m-%d %H:%M:%S')
Configuration: 12 Agents - Department Structure
Topology: Hierarchical (Corporate)
Organization: 1 CTO + 3 Dept Heads + 8 Individual Contributors

## Test Durations
- Test 1a: $(cat "$results_dir/test_1a_duration.txt" 2>/dev/null || echo "N/A") seconds
- Test 2a: $(cat "$results_dir/test_2a_duration.txt" 2>/dev/null || echo "N/A") seconds
- Test 3a: $(cat "$results_dir/test_3a_duration.txt" 2>/dev/null || echo "N/A") seconds
- Test 4a: $(cat "$results_dir/test_4a_duration.txt" 2>/dev/null || echo "N/A") seconds
- **Total Time**: $total_duration seconds

## Organizational Analysis
### Management Structure:
- CTO effectiveness: [Strong/Moderate/Weak]
- Department head coordination: [Smooth/Siloed/Conflicting]
- Management overhead: [X% of total time]

### Department Performance:
#### Development Department (5 members):
- Internal coordination: [Excellent/Good/Fair/Poor]
- Output quality: [High/Medium/Low]
- Bottlenecks identified: 

#### QA Department (3 members):
- Test coverage: [Comprehensive/Good/Basic]
- Integration with dev: [Seamless/Delayed/Poor]
- Process efficiency: [High/Medium/Low]

#### Research Department (3 members):
- Contribution value: [High/Medium/Low]
- Knowledge sharing: [Effective/Limited/None]
- Innovation impact: 

## Coordination Metrics
- Vertical communication (hierarchy): [Fast/Moderate/Slow]
- Horizontal communication (cross-dept): [Good/Limited/None]
- Decision latency: [X seconds average]
- **Total coordination overhead**: [X% of execution time]

## Comparison Analysis
- vs Baseline (~47.5s): [X% slower/faster]
- vs 8 agents: [Compare structure benefits]
- vs 5 agents: [When does hierarchy help/hurt]
- **Breaking point**: [Where bureaucracy overwhelms productivity]

## Quality Assessment (0-10)
[Standard metrics plus department-specific measures]

## Key Observations
1. Management layer impact: 
2. Department silo effects: 
3. Communication patterns: 
4. Bureaucratic overhead: 
5. Task routing efficiency: 

## Corporate Structure Findings
### Benefits observed:
- Clear chain of command for: [Task types]
- Department specialization helps with: [Scenarios]

### Drawbacks observed:
- Excessive layers for: [Simple tasks]
- Silo communication delays in: [Scenarios]
- Management overhead dominates when: [Conditions]

## Recommendations
12-agent corporate structure suitable for:
- Large, complex projects requiring clear ownership
- Tasks needing strict approval workflows
- Scenarios where department isolation is beneficial

NOT recommended for:
- Simple tasks (overhead >> benefit)
- Rapid iteration requirements
- Cross-functional collaboration needs
EOF

echo "✅ 12-Agent Department Structure tests complete!"
echo "📊 Total test time: $total_duration seconds"
echo "📁 Results saved to: $results_dir"
echo ""
echo "Analysis: Evaluate if corporate hierarchy helps or hinders for these tasks"