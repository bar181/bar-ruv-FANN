# Test 2a: Debugging - Fix Simple Logic Error

## 🟢 Difficulty: SIMPLE
**Expected Duration**: 2-3 minutes per configuration

## Test Overview
This test evaluates basic debugging skills on a simple function with obvious logic errors.

## Test Prompt
```
Debug and fix the following Python function that should calculate the factorial of a number:

```python
def factorial(n):
    """Calculate factorial of n (n!)"""
    if n < 0:
        return "Error: Negative number"
    
    result = 0  # Bug 1: Should be 1
    for i in range(1, n):  # Bug 2: Should be range(1, n+1)
        result *= i
    
    return result

# Test cases that are failing:
assert factorial(0) == 1  # Returns 0
assert factorial(5) == 120  # Returns 0
assert factorial(1) == 1  # Returns 0
```

Requirements:
1. Identify and fix all bugs
2. Explain what was wrong
3. Add 2-3 more test cases
4. Ensure the function handles edge cases properly
```

## Expected Deliverables
- Fixed function
- Explanation of bugs
- Additional test cases
- Verification that all tests pass

## Test Configurations

### 1. Claude Native (Baseline)
- **Setup**: Direct debugging prompt
- **Expected Time**: 30-60 seconds

### 2. Swarm Config A: Simple Parallel (3 agents, flat)
- **Setup**: 
  ```javascript
  mcp__ruv-swarm__swarm_init { topology: "mesh", maxAgents: 3, strategy: "balanced" }
  mcp__ruv-swarm__agent_spawn { type: "analyst", name: "bug-finder" }
  mcp__ruv-swarm__agent_spawn { type: "coder", name: "fix-implementer" }
  mcp__ruv-swarm__agent_spawn { type: "tester", name: "test-validator" }
  ```
- **Expected Time**: 45-90 seconds

### 3. Swarm Config B: Hierarchical (3 agents)
- **Expected Time**: 60-120 seconds

## Evaluation Metrics

### Quick Assessment (2 minutes)
- [ ] All bugs identified
- [ ] Fixes are correct
- [ ] Original tests pass
- [ ] New tests added
- [ ] Clear explanation provided

### Key Observations
- Speed of bug identification
- Quality of explanations
- Completeness of testing

## Notes
- Simple bugs allow focus on coordination efficiency
- Clear right/wrong answers for easy evaluation
- Good warm-up test before complex debugging