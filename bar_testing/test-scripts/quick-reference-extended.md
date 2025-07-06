# Extended Quick Reference: All Swarm Test Configurations

## Complete Test Script Collection

### Baseline (No Swarm)
```bash
./bar_testing/test-scripts/run-baseline-simple-tests-fixed.sh
```
- Direct Claude responses, no swarm overhead
- Performance baseline for all comparisons

### Single Agent Configurations

#### Config A1: 1 Agent (Overhead Test)
```bash
./bar_testing/test-scripts/run-swarm-config-a1.sh
```
- Tests pure swarm infrastructure overhead
- Choose between coder, coordinator, or researcher
- Compare with baseline to measure swarm cost

### Two Agent Configurations

#### Config A2: 2 Agents (Minimal Team)
```bash
./bar_testing/test-scripts/run-swarm-config-a2.sh
```
- Minimal collaboration testing
- Options: Dev+Test, Coord+Impl, or Two Specialists
- Tests if 2 > 1 for simple tasks

### Three Agent Configurations

#### Config B: 3 Agents Flat
```bash
./bar_testing/test-scripts/run-swarm-config-a.sh
```
- Simple parallel processing
- Equal peers, no hierarchy

#### Config C: 3 Agents Hierarchical
```bash
./bar_testing/test-scripts/run-swarm-config-b.sh
```
- Coordinator leads two implementers
- Tests delegation efficiency

### Five Agent Configuration

#### Config D: 5 Agents Dynamic
```bash
./bar_testing/test-scripts/run-swarm-config-c.sh
```
- Full specialization coverage
- Adaptive coordination strategy

### Eight Agent Configuration

#### Config E: 8 Agents (Dual Teams)
```bash
./bar_testing/test-scripts/run-swarm-config-e.sh
```
- Development team + QA team structure
- Tests team-based coordination

### Twelve Agent Configuration

#### Config G: 12 Agents (Corporate)
```bash
./bar_testing/test-scripts/run-swarm-config-g.sh
```
- Full department structure with management layers
- Tests bureaucratic overhead

### Twenty Agent Configuration

#### Config H: 20 Agents (Stress Test)
```bash
./bar_testing/test-scripts/run-swarm-config-h.sh
```
- Maximum stress test
- Identifies system breaking points

## Test Execution Order

### Phase 1: Core Tests (2-3 hours)
1. Baseline (no swarm)
2. 1 agent (A1)
3. 2 agents (A2)
4. 3 agents flat (B)
5. 3 agents hierarchical (C)

### Phase 2: Scaling Tests (2-3 hours)
6. 5 agents (D)
7. 8 agents (E)

### Phase 3: Stress Tests (2+ hours)
8. 12 agents (G)
9. 20 agents (H)

## Key Metrics by Configuration

| Config | Agents | Expected Time | Overhead | Best For |
|--------|--------|--------------|----------|----------|
| Baseline | 0 | ~47.5s/test | 0% | Baseline |
| A1 | 1 | ~50s/test | 5-10% | Overhead measurement |
| A2 | 2 | ~45s/test | 10-15% | Simple collaboration |
| B | 3 | ~40s/test | 15-20% | Parallel tasks |
| C | 3 | ~42s/test | 20-25% | Structured tasks |
| D | 5 | ~38s/test | 25-30% | Complex tasks |
| E | 8 | ~45s/test | 35-45% | Large projects |
| G | 12 | ~60s/test | 60-80% | Enterprise tasks |
| H | 20 | ~120s+/test | 100%+ | Stress testing |

## Quick Analysis Commands

Check swarm status:
```javascript
mcp__ruv-swarm__swarm_status { verbose: true }
```

Monitor in real-time:
```javascript
mcp__ruv-swarm__swarm_monitor { duration: 30, interval: 2 }
```

Get performance metrics:
```javascript
mcp__ruv-swarm__agent_metrics { metric: "all" }
```

Memory usage by agent:
```javascript
mcp__ruv-swarm__memory_usage { detail: "by-agent" }
```

## Results Structure
```
bar_testing/test-results/simple/
├── baseline_run_*/          # No swarm baseline
├── swarm_a1_run_*/         # 1 agent
├── swarm_a2_run_*/         # 2 agents
├── swarm_a_run_*/          # 3 agents flat (Config B)
├── swarm_b_run_*/          # 3 agents hier (Config C)
├── swarm_c_run_*/          # 5 agents (Config D)
├── swarm_e_run_*/          # 8 agents
├── swarm_g_run_*/          # 12 agents
└── swarm_h_run_*/          # 20 agents
```

## Expected Patterns

### Efficiency Sweet Spot
- 1-2 agents: Minimal benefit, some overhead
- 3-5 agents: Optimal for most tasks
- 8 agents: Good for complex multi-faceted work
- 12+ agents: Overhead dominates except for massive tasks

### Quality vs Speed Tradeoff
- More agents ≠ better quality after ~5 agents
- Coordination overhead grows non-linearly
- Optimal configuration depends on task complexity

### When to Use Each Size
- **1 agent**: Never (use baseline instead)
- **2 agents**: Dev + QA pairs
- **3 agents**: Standard development tasks
- **5 agents**: Full-stack applications
- **8 agents**: Multi-team projects
- **12 agents**: Enterprise workflows
- **20 agents**: Only for stress testing