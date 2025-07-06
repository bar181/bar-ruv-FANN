# Test 1a: Code Generation - Simple Function Implementation

## 🟢 Difficulty: SIMPLE
**Expected Duration**: 2-3 minutes per configuration

## Test Overview
This test evaluates basic code generation capabilities by implementing a simple utility function with clear requirements.

## Test Prompt
```
Create a Python function called 'merge_sorted_lists' that:

1. Takes two sorted lists of integers as input
2. Returns a single sorted list containing all elements from both lists
3. Handles edge cases (empty lists, None values)
4. Includes type hints and a docstring
5. Write 3-5 unit tests for the function

Example:
merge_sorted_lists([1, 3, 5], [2, 4, 6]) → [1, 2, 3, 4, 5, 6]
```

## Expected Deliverables
- Function implementation
- Unit tests
- Brief explanation of approach

## Test Configurations

### 1. Claude Native (Baseline)
- **Setup**: Direct prompt to Claude
- **Expected Time**: 30-60 seconds

### 2. Swarm Config A: Simple Parallel (3 agents, flat)
- **Setup**: 
  ```javascript
  mcp__ruv-swarm__swarm_init { topology: "mesh", maxAgents: 3, strategy: "balanced" }
  mcp__ruv-swarm__agent_spawn { type: "coder", name: "implementer" }
  mcp__ruv-swarm__agent_spawn { type: "tester", name: "test-writer" }
  mcp__ruv-swarm__agent_spawn { type: "analyst", name: "reviewer" }
  ```
- **Expected Time**: 45-90 seconds

### 3. Swarm Config B: Hierarchical (3 agents)
- **Setup**: Same agents, hierarchical topology
- **Expected Time**: 60-120 seconds

## Evaluation Metrics

### Quick Assessment (2 minutes)
- [ ] Function works correctly
- [ ] Handles edge cases
- [ ] Has proper type hints
- [ ] Tests pass
- [ ] Code is clean and readable

### Measurement Focus
- **Primary**: Correctness and completion time
- **Secondary**: Code quality and test coverage
- **Token Efficiency**: Compare tokens used vs output quality

## Notes
- This simple test helps establish baseline performance
- Focus on speed and correctness over optimization
- Good for testing basic coordination overhead