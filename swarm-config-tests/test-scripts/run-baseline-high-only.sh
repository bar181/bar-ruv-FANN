#!/bin/bash
# Run ONLY Baseline HIGH Tests in Claude Terminal

echo "🔴 BASELINE HIGH DIFFICULTY TESTS FOR CLAUDE"
echo "==========================================="
echo ""
echo "⚠️  These are OPTIONAL advanced tests"
echo "⏱️  Expected time: 60-100 minutes total"
echo "🧠 Tests require deep expertise and complex reasoning"
echo ""

# Initialize timing
suite_start=$(date +%s)

# Function to format time
format_time() {
    local seconds=$1
    local minutes=$((seconds / 60))
    local remaining_seconds=$((seconds % 60))
    echo "${minutes}m ${remaining_seconds}s"
}

echo "📋 High Difficulty Test Overview:"
echo "1. Rate-Limited API Client (15-20 min)"
echo "2. Complex Concurrency Debugging (15-20 min)"
echo "3. Vehicle Routing Optimization (20-25 min)"
echo "4. Framework Architecture Analysis (20-30 min)"
echo ""
echo "Press Enter to see the test prompts..."
read

cat << 'EOF'
Please complete these 4 HIGH DIFFICULTY tests. Work through each one carefully and note the time taken.
These are advanced challenges requiring deep expertise. Focus on approach quality over perfection.

════════════════════════════════════════════════════════════════════════════════

=== TEST 1: Code Generation - Rate-Limited API Client (15-20 min) ===

Create a Python class called RateLimitedAPIClient that implements the following requirements:

1. Support configurable rate limiting (e.g., 100 requests per minute)
2. Implement exponential backoff retry logic for failed requests
3. Handle concurrent requests using asyncio
4. Support request queuing when rate limit is reached
5. Provide detailed logging and metrics collection
6. Include proper error handling for network issues, timeouts, and API errors
7. Support both GET and POST methods
8. Include a circuit breaker pattern that opens after 5 consecutive failures

The client should be production-ready with type hints, docstrings, and comprehensive error handling.

Additional requirements:
- Include comprehensive unit tests using pytest and pytest-asyncio
- Mock external API calls appropriately
- Test rate limiting, retries, circuit breaker, and error scenarios
- Include usage examples for common scenarios
- Document design decisions and tradeoffs

════════════════════════════════════════════════════════════════════════════════

=== TEST 2: Debugging - Fix Complex Concurrency Bug (15-20 min) ===

Debug and fix the following issues in a distributed task processing system:

The provided code has several critical bugs:
1. Race condition causing duplicate task processing
2. Potential deadlock between worker threads
3. Memory leak in the task queue implementation
4. Incorrect error propagation causing silent failures
5. Task results occasionally being lost or corrupted

Here's the buggy code:

```python
import threading
import queue
import time
import random
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
import weakref

@dataclass
class Task:
    id: str
    payload: Dict[str, Any]
    callback: Optional[Callable] = None
    retry_count: int = 0
    max_retries: int = 3

class DistributedTaskProcessor:
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.task_queue = queue.Queue()
        self.result_store = {}
        self.processing_tasks = set()
        self.workers = []
        self.lock = threading.Lock()
        self.shutdown = False
        self._start_workers()
    
    def _start_workers(self):
        for i in range(self.num_workers):
            worker = threading.Thread(target=self._worker_loop, args=(i,))
            worker.start()
            self.workers.append(worker)
    
    def _worker_loop(self, worker_id: int):
        while not self.shutdown:
            try:
                task = self.task_queue.get(timeout=1)
                
                # Bug: Race condition here
                if task.id in self.processing_tasks:
                    self.task_queue.put(task)
                    continue
                
                self.processing_tasks.add(task.id)
                
                # Process task
                result = self._process_task(task)
                
                # Bug: Potential deadlock
                with self.lock:
                    self.result_store[task.id] = result
                    if task.callback:
                        task.callback(result)
                
                # Bug: Memory leak - tasks never removed from processing_tasks
                
            except queue.Empty:
                continue
            except Exception as e:
                # Bug: Error not properly handled
                print(f"Worker {worker_id} error: {e}")
    
    def _process_task(self, task: Task) -> Dict[str, Any]:
        # Simulate processing
        time.sleep(random.uniform(0.1, 0.5))
        
        # Randomly fail some tasks
        if random.random() < 0.1:
            raise Exception("Task processing failed")
        
        return {"task_id": task.id, "result": "processed", "data": task.payload}
    
    def submit_task(self, task: Task) -> str:
        # Bug: No check for duplicate task IDs
        self.task_queue.put(task)
        return task.id
    
    def get_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        # Bug: Not thread-safe
        return self.result_store.get(task_id)
    
    def shutdown_workers(self):
        self.shutdown = True
        for worker in self.workers:
            worker.join()
```

Requirements:
1. Identify and fix ALL bugs
2. Explain the root cause of each issue
3. Provide the corrected implementation
4. Add proper tests to verify the fixes
5. Ensure thread-safety throughout
6. Implement proper cleanup and resource management

════════════════════════════════════════════════════════════════════════════════

=== TEST 3: Mathematical Problem - Vehicle Routing Optimization (20-25 min) ===

Solve the following optimization problem and provide a complete solution with implementation:

A logistics company needs to optimize their delivery route system. They have:
- N delivery locations in a 2D plane with coordinates (x_i, y_i)
- M delivery trucks, each with capacity C_j
- Each location i has demand d_i (packages to deliver)
- Each truck starts from depot at (0, 0) and must return
- Time window constraints: location i must be visited between [a_i, b_i]
- Fuel cost is proportional to Euclidean distance traveled

Objectives:
1. Minimize total distance traveled by all trucks
2. Ensure all demands are met
3. Respect capacity constraints
4. Meet time window requirements
5. Balance load across trucks (minimize max - min packages per truck)

Tasks:
1. Formulate this as a mathematical optimization problem
2. Prove whether the problem is NP-hard
3. Develop an efficient approximation algorithm
4. Implement the algorithm in Python
5. Analyze time and space complexity
6. Provide bounds on the approximation ratio
7. Create visualizations of example solutions

Test with:
N = 20 locations
M = 4 trucks
Capacities: [50, 40, 45, 55]
Demands: randomly between 5-15 packages
Time windows: 2-hour windows between 8 AM - 6 PM
Average speed: 30 km/h

Provide complete mathematical formulation, implementation, and analysis.

════════════════════════════════════════════════════════════════════════════════

=== TEST 4: Research & Analysis - Large-Scale Platform Architecture (20-30 min) ===

Conduct a comprehensive analysis and comparison of modern web frameworks for building a large-scale, real-time collaborative platform with the following requirements:

System Requirements:
- Support 100,000+ concurrent users
- Real-time collaboration (< 100ms latency)
- Offline-first architecture with conflict resolution
- End-to-end encryption for sensitive data
- Microservices architecture support
- Multi-tenant SaaS capabilities
- Global deployment across 5+ regions
- 99.99% uptime SLA
- GDPR/HIPAA compliance
- Mobile and desktop clients

Analyze and compare:
1. Next.js with Vercel
2. SvelteKit with Cloudflare Workers
3. Remix with fly.io
4. Qwik with Deno Deploy
5. Astro with SSG/ISR capabilities

For each framework, provide:
1. Architecture patterns and best practices
2. Performance benchmarks and analysis
3. Scalability considerations
4. Security implications
5. Developer experience assessment
6. Cost analysis at scale
7. Integration capabilities
8. Community and ecosystem evaluation
9. Production case studies
10. Migration complexity from existing systems

Deliverables:
- Executive summary with recommendations
- Detailed technical comparison matrix
- Architecture diagrams for each approach
- Cost projections for 3-year TCO
- Risk assessment matrix
- Implementation roadmap
- Sample code for critical components
- Performance testing methodology

════════════════════════════════════════════════════════════════════════════════

When complete with ALL 4 tests, note the total time taken.
Focus on demonstrating expertise and thoughtful approaches rather than perfect solutions.
EOF

echo ""
echo "Press Enter after Claude completes ALL 4 high difficulty tests..."
read

# Final timing
suite_end=$(date +%s)
total_duration=$((suite_end - suite_start))

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📊 HIGH DIFFICULTY BASELINE TESTS COMPLETE"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Total Time: $(format_time $total_duration)"
echo "Expected: 60-100 minutes"
echo ""
echo "✅ High difficulty baseline data collected!"
echo ""
echo "Key evaluation points:"
echo "1. Approach quality and reasoning depth"
echo "2. Handling of complex requirements"
echo "3. Production-readiness of solutions"
echo "4. Completeness vs time tradeoffs"
echo ""
echo "These results establish the upper bound of single-agent complexity"
echo "and show where multi-agent swarms might provide the most value."