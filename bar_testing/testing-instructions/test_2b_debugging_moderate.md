# Test 2b: Debugging - Fix Race Condition

## 🟡 Difficulty: MODERATE
**Expected Duration**: 5-8 minutes per configuration

## Test Overview
This test evaluates debugging skills on a concurrent program with a race condition and improper resource cleanup.

## Test Prompt
```
Debug and fix the following Python code that manages a shared counter with multiple threads:

```python
import threading
import time

class SharedCounter:
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()
    
    def increment(self, times=1000):
        for _ in range(times):
            # Bug 1: Not using the lock
            temp = self.count
            time.sleep(0.00001)  # Simulate some work
            self.count = temp + 1
    
    def get_count(self):
        # Bug 2: Not thread-safe read
        return self.count

def worker(counter):
    counter.increment()

# Test that demonstrates the bug:
counter = SharedCounter()
threads = []

for i in range(5):
    t = threading.Thread(target=worker, args=(counter,))
    threads.append(t)
    t.start()

# Bug 3: Not waiting for threads to complete
print(f"Final count: {counter.get_count()}")  # Should be 5000, but isn't

# Bug 4: No cleanup/join of threads
```

Requirements:
1. Fix all race conditions
2. Ensure thread-safe operations
3. Properly wait for thread completion
4. Add a reset() method
5. Write tests to verify the fixes work
```

## Expected Deliverables
- Fixed SharedCounter class
- Explanation of each bug
- Test code demonstrating fixes
- Proper thread cleanup

## Test Configurations

### 1. Claude Native (Baseline)
- **Setup**: Direct debugging prompt
- **Expected Time**: 2-3 minutes

### 2. Swarm Config A: Simple Parallel (3 agents, flat)
- **Setup**: 
  ```javascript
  mcp__ruv-swarm__swarm_init { topology: "mesh", maxAgents: 3, strategy: "balanced" }
  mcp__ruv-swarm__agent_spawn { type: "analyst", name: "concurrency-expert" }
  mcp__ruv-swarm__agent_spawn { type: "coder", name: "fix-developer" }
  mcp__ruv-swarm__agent_spawn { type: "tester", name: "thread-tester" }
  ```
- **Expected Time**: 3-5 minutes

### 3. Swarm Config B: Hierarchical (3 agents)
- **Expected Time**: 4-6 minutes

### 4. Swarm Config C: Specialized Team (5 agents)
- **Setup**: Add race condition specialist and performance analyst
- **Expected Time**: 5-8 minutes

## Evaluation Metrics

### Assessment Checklist (5 minutes)
- [ ] Race condition fixed
- [ ] Thread-safe read implemented
- [ ] Proper thread joining
- [ ] Clean resource management
- [ ] Tests verify fixes
- [ ] Clear explanations

### Critical Points
- Correct use of locks
- No deadlock potential
- Proper thread lifecycle management
- Test reliability

## Notes
- Common real-world bug pattern
- Tests understanding of concurrency
- Multiple valid fix approaches possible