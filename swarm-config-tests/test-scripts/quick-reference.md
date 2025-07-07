# Quick Reference: Running Swarm Tests

## Available Test Scripts

### Baseline (Claude Native)
```bash
./bar_testing/test-scripts/run-baseline-simple-tests-fixed.sh
```
- No swarm, direct Claude responses
- Establishes performance baseline

### Swarm Configurations

#### Config A: 3 Agents Flat
```bash
./bar_testing/test-scripts/run-swarm-config-a.sh
```
- Simple parallel processing
- Minimal coordination overhead

#### Config B: 3 Agents Hierarchical  
```bash
./bar_testing/test-scripts/run-swarm-config-b.sh
```
- Structured delegation
- Coordinator leads implementation

#### Config C: 5 Agents Dynamic
```bash
./bar_testing/test-scripts/run-swarm-config-c.sh
```
- Specialized expertise
- Adaptive coordination

## Test Execution Checklist

### Before Starting
- [ ] MCP server running: `npx ruv-swarm mcp start --protocol=stdio`
- [ ] Working directory: `/workspaces/ruv-FANN`
- [ ] Baseline tests completed for comparison

### For Each Swarm Test
1. **Initialize swarm** using BatchTool (all agents in ONE message)
2. **Verify setup** with `mcp__ruv-swarm__swarm_status`
3. **Run tests** using `mcp__ruv-swarm__task_orchestrate`
4. **Collect results** with `mcp__ruv-swarm__task_results`
5. **Record metrics** including timing and token usage

### Key Commands

Initialize swarm (example):
```javascript
[BatchTool]:
  mcp__ruv-swarm__swarm_init { topology: "mesh", maxAgents: 3, strategy: "balanced" }
  mcp__ruv-swarm__agent_spawn { type: "coder", name: "developer" }
  mcp__ruv-swarm__agent_spawn { type: "tester", name: "qa" }
  mcp__ruv-swarm__agent_spawn { type: "analyst", name: "reviewer" }
```

Orchestrate task:
```javascript
mcp__ruv-swarm__task_orchestrate {
  task: "Task description here",
  priority: "medium",
  strategy: "parallel",
  maxAgents: 3
}
```

Get results:
```javascript
mcp__ruv-swarm__task_results {
  taskId: "task_id_from_orchestrate",
  format: "detailed"
}
```

Monitor performance:
```javascript
mcp__ruv-swarm__agent_metrics { metric: "all" }
mcp__ruv-swarm__memory_usage { detail: "by-agent" }
```

## Results Location
All results stored in: `bar_testing/test-results/simple/`
- Baseline: `baseline_run_*`
- Config A: `swarm_a_run_*`
- Config B: `swarm_b_run_*`
- Config C: `swarm_c_run_*`

## Metrics to Track
1. **Execution time** per test
2. **Token usage** (input + output)
3. **Quality scores** (0-10 scale)
4. **Coordination overhead**
5. **Agent contribution** breakdown