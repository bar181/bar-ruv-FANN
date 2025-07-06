# Test 1b: Code Generation - Moderate Class Design

## 🟡 Difficulty: MODERATE
**Expected Duration**: 5-8 minutes per configuration

## Test Overview
This test evaluates intermediate code generation with a focus on class design, basic patterns, and error handling.

## Test Prompt
```
Create a Python class called 'TaskQueue' that implements:

1. A simple priority queue for tasks
2. Methods: add_task(task, priority), get_next_task(), peek(), is_empty()
3. Priority levels: HIGH (1), MEDIUM (2), LOW (3)
4. Tasks with same priority should be FIFO
5. Thread-safe implementation using threading.Lock
6. Basic error handling for invalid inputs
7. Include usage example and 5-7 unit tests

Requirements:
- Use heapq for efficiency
- Include type hints and docstrings
- Handle edge cases gracefully
```

## Expected Deliverables
- Complete TaskQueue implementation
- Unit tests demonstrating functionality
- Usage example
- Brief design notes

## Test Configurations

### 1. Claude Native (Baseline)
- **Setup**: Direct prompt to Claude
- **Expected Time**: 2-3 minutes

### 2. Swarm Config A: Simple Parallel (3 agents, flat)
- **Setup**: 
  ```javascript
  mcp__ruv-swarm__swarm_init { topology: "mesh", maxAgents: 3, strategy: "balanced" }
  mcp__ruv-swarm__agent_spawn { type: "coder", name: "class-designer" }
  mcp__ruv-swarm__agent_spawn { type: "tester", name: "test-developer" }
  mcp__ruv-swarm__agent_spawn { type: "analyst", name: "thread-safety-reviewer" }
  ```
- **Expected Time**: 3-5 minutes

### 3. Swarm Config B: Hierarchical (3 agents)
- **Expected Time**: 4-6 minutes

### 4. Swarm Config C: Specialized Team (5 agents)
- **Setup**: Add optimizer and documentation specialist
- **Expected Time**: 5-8 minutes

## Evaluation Metrics

### Assessment Checklist (5 minutes)
- [ ] All required methods implemented
- [ ] Priority ordering works correctly
- [ ] Thread-safe implementation
- [ ] Proper error handling
- [ ] Good test coverage
- [ ] Clean, maintainable code

### Performance Metrics
- Implementation completeness
- Test quality and coverage
- Thread-safety correctness
- Documentation quality

## Notes
- Moderate complexity allows testing of design decisions
- Thread-safety adds coordination challenge for swarms
- Good balance of features for 5-minute test