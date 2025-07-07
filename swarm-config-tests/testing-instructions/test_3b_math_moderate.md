# Test 3b: Mathematical Problem - Graph Algorithm

## 🟡 Difficulty: MODERATE
**Expected Duration**: 5-8 minutes per configuration

## Test Overview
This test evaluates algorithmic thinking and graph theory application to a practical problem.

## Test Prompt
```
Solve the following network optimization problem:

You have a network of cities connected by roads with travel times:
- Cities: A, B, C, D, E
- Connections (bidirectional with travel time in minutes):
  A-B: 10, A-C: 15, B-C: 5, B-D: 20, C-D: 10, C-E: 25, D-E: 15

Tasks:
1. Find the shortest path from A to E
2. Prove your path is optimal
3. Implement Dijkstra's algorithm in Python that:
   - Works with any graph represented as adjacency list
   - Returns both shortest distance and path
   - Handles disconnected graphs gracefully
4. Calculate the time complexity
5. Modify to find all paths within 10% of optimal

Example graph format:
graph = {
    'A': {'B': 10, 'C': 15},
    'B': {'A': 10, 'C': 5, 'D': 20},
    ...
}
```

## Expected Deliverables
- Shortest path solution with explanation
- Dijkstra implementation with comments
- Complexity analysis
- Extended solution for near-optimal paths
- Test cases including edge cases

## Test Configurations

### 1. Claude Native (Baseline)
- **Setup**: Direct prompt
- **Expected Time**: 3-4 minutes

### 2. Swarm Config A: Simple Parallel (3 agents, flat)
- **Setup**: 
  ```javascript
  mcp__ruv-swarm__swarm_init { topology: "mesh", maxAgents: 3, strategy: "balanced" }
  mcp__ruv-swarm__agent_spawn { type: "researcher", name: "algorithm-expert" }
  mcp__ruv-swarm__agent_spawn { type: "coder", name: "dijkstra-implementer" }
  mcp__ruv-swarm__agent_spawn { type: "analyst", name: "complexity-analyzer" }
  ```
- **Expected Time**: 4-6 minutes

### 3. Swarm Config B: Hierarchical (3 agents)
- **Expected Time**: 5-7 minutes

### 4. Swarm Config C: Specialized Team (5 agents)
- **Setup**: Add optimization specialist and test designer
- **Expected Time**: 6-8 minutes

## Evaluation Metrics

### Assessment Checklist (5 minutes)
- [ ] Correct shortest path found
- [ ] Valid proof/explanation
- [ ] Working Dijkstra implementation
- [ ] Handles edge cases
- [ ] Correct complexity analysis
- [ ] Near-optimal paths feature works

### Performance Indicators
- Algorithm correctness
- Code efficiency
- Handling of edge cases
- Quality of analysis

## Notes
- Well-known algorithm with clear solution
- Tests both theory and implementation
- Extension adds moderate complexity