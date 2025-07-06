# Test 3a: Mathematical Problem - Simple Optimization

## 🟢 Difficulty: SIMPLE
**Expected Duration**: 2-3 minutes per configuration

## Test Overview
This test evaluates basic mathematical problem-solving and optimization skills.

## Test Prompt
```
Solve the following optimization problem:

A farmer has 100 meters of fencing and wants to create a rectangular enclosure 
against a straight wall (so only 3 sides need fencing).

1. Find the dimensions that maximize the enclosed area
2. Prove your answer is optimal using calculus
3. Implement a Python function that:
   - Takes fence_length as input
   - Returns optimal dimensions (width, length) and maximum area
   - Validates inputs (positive fence length)
4. Create a simple visualization showing the area vs. width relationship

Example: maximize_enclosure(100) → (width=25, length=50, area=1250)
```

## Expected Deliverables
- Mathematical solution with steps
- Proof of optimality
- Python implementation
- Simple plot/visualization
- Test cases

## Test Configurations

### 1. Claude Native (Baseline)
- **Setup**: Direct prompt
- **Expected Time**: 60-90 seconds

### 2. Swarm Config A: Simple Parallel (3 agents, flat)
- **Setup**: 
  ```javascript
  mcp__ruv-swarm__swarm_init { topology: "mesh", maxAgents: 3, strategy: "balanced" }
  mcp__ruv-swarm__agent_spawn { type: "researcher", name: "math-solver" }
  mcp__ruv-swarm__agent_spawn { type: "coder", name: "implementer" }
  mcp__ruv-swarm__agent_spawn { type: "analyst", name: "visualizer" }
  ```
- **Expected Time**: 90-120 seconds

### 3. Swarm Config B: Hierarchical (3 agents)
- **Expected Time**: 2-3 minutes

## Evaluation Metrics

### Quick Assessment (2 minutes)
- [ ] Correct mathematical solution
- [ ] Valid proof provided
- [ ] Working implementation
- [ ] Handles edge cases
- [ ] Clear visualization

### Key Points
- Correct formula derivation
- Implementation matches math
- Visualization aids understanding

## Notes
- Classic optimization problem
- Clear correct answer for validation
- Tests math-to-code translation