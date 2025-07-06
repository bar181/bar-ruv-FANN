#!/bin/bash
# Run Baseline HIGH DIFFICULTY Tests (No Swarm)

echo "🔴 Running Baseline HIGH DIFFICULTY Tests (Claude Native - No Swarm)"
echo "===================================================================="
echo ""
echo "⚠️  WARNING: These are OPTIONAL advanced tests"
echo "⏱️  Expected: 15-30 minutes per test (60-100 minutes total)"
echo "🧠 Tests require deep expertise and complex reasoning"
echo ""

# Create timestamp for this test run
timestamp=$(date +%Y%m%d_%H%M%S)
results_dir="bar_testing/test-results/high/baseline_run_$timestamp"
mkdir -p "$results_dir"

echo "📁 Results will be saved to: $results_dir"
echo ""

# Function to calculate duration
calculate_duration() {
    local start=$1
    local end=$2
    local duration=$((end - start))
    echo "$duration"
}

# Test 1: Code Generation - Rate-Limited API Client
echo "▶️  Test 1: Code Generation - Rate-Limited API Client (HIGH)"
echo "----------------------------------------------------------"
cat > "$results_dir/test_1_prompt.txt" << 'EOF'
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
EOF

echo "📝 Prompt saved to: $results_dir/test_1_prompt.txt"
echo "⏱️  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "🎯 This requires: async programming, rate limiting algorithms, circuit breakers"
start_1=$(date +%s)
echo ""
echo "COPY AND PASTE THIS PROMPT TO CLAUDE:"
echo "======================================"
cat "$results_dir/test_1_prompt.txt"
echo "======================================"
echo ""
echo "💾 Save response to: $results_dir/test_1_response.txt"
read -p "Press Enter when complete..."
end_1=$(date +%s)
duration_1=$(calculate_duration $start_1 $end_1)
echo "⏱️  Duration: $duration_1 seconds"
echo "$duration_1" > "$results_dir/test_1_duration.txt"
echo ""

# Test 2: Debugging - Complex Concurrency Bug
echo "▶️  Test 2: Debugging - Fix Complex Concurrency Bug (HIGH)"
echo "--------------------------------------------------------"
cat > "$results_dir/test_2_prompt.txt" << 'EOF'
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
EOF

echo "📝 Prompt saved to: $results_dir/test_2_prompt.txt"
echo "⏱️  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "🎯 This requires: concurrency expertise, race condition analysis, deadlock detection"
start_2=$(date +%s)
echo ""
echo "COPY AND PASTE THIS PROMPT TO CLAUDE:"
echo "======================================"
cat "$results_dir/test_2_prompt.txt"
echo "======================================"
echo ""
echo "💾 Save response to: $results_dir/test_2_response.txt"
read -p "Press Enter when complete..."
end_2=$(date +%s)
duration_2=$(calculate_duration $start_2 $end_2)
echo "⏱️  Duration: $duration_2 seconds"
echo "$duration_2" > "$results_dir/test_2_duration.txt"
echo ""

# Test 3: Mathematical Problem - Complex Optimization
echo "▶️  Test 3: Mathematical Problem - Vehicle Routing Optimization (HIGH)"
echo "-------------------------------------------------------------------"
cat > "$results_dir/test_3_prompt.txt" << 'EOF'
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
EOF

echo "📝 Prompt saved to: $results_dir/test_3_prompt.txt"
echo "⏱️  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "🎯 This requires: optimization theory, graph algorithms, complexity analysis"
start_3=$(date +%s)
echo ""
echo "COPY AND PASTE THIS PROMPT TO CLAUDE:"
echo "======================================"
cat "$results_dir/test_3_prompt.txt"
echo "======================================"
echo ""
echo "💾 Save response to: $results_dir/test_3_response.txt"
read -p "Press Enter when complete..."
end_3=$(date +%s)
duration_3=$(calculate_duration $start_3 $end_3)
echo "⏱️  Duration: $duration_3 seconds"
echo "$duration_3" > "$results_dir/test_3_duration.txt"
echo ""

# Test 4: Research & Analysis - Framework Evaluation
echo "▶️  Test 4: Research & Analysis - Framework Evaluation (HIGH)"
echo "----------------------------------------------------------"
cat > "$results_dir/test_4_prompt.txt" << 'EOF'
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
EOF

echo "📝 Prompt saved to: $results_dir/test_4_prompt.txt"
echo "⏱️  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "🎯 This requires: architecture expertise, framework knowledge, cost analysis"
start_4=$(date +%s)
echo ""
echo "COPY AND PASTE THIS PROMPT TO CLAUDE:"
echo "======================================"
cat "$results_dir/test_4_prompt.txt"
echo "======================================"
echo ""
echo "💾 Save response to: $results_dir/test_4_response.txt"
read -p "Press Enter when complete..."
end_4=$(date +%s)
duration_4=$(calculate_duration $start_4 $end_4)
echo "⏱️  Duration: $duration_4 seconds"
echo "$duration_4" > "$results_dir/test_4_duration.txt"

# Calculate totals
total_start=$start_1
total_end=$end_4
total_duration=$(calculate_duration $total_start $total_end)

# Create summary report
cat > "$results_dir/baseline_high_summary.md" << EOF
# Baseline HIGH DIFFICULTY Test Results
Date: $(date '+%Y-%m-%d %H:%M:%S')
Configuration: Claude Native (No Swarm)
Test Level: HIGH (15-30 minute tests)
Status: OPTIONAL ADVANCED TESTS

## Test Durations
- Test 1 (Rate-Limited API): $duration_1 seconds
- Test 2 (Concurrency Debug): $duration_2 seconds
- Test 3 (Vehicle Routing): $duration_3 seconds
- Test 4 (Framework Analysis): $duration_4 seconds
- **Total Time**: $total_duration seconds

## Performance Metrics
- Average per test: $((total_duration / 4)) seconds
- Expected range: 900-1800 seconds (15-30 minutes) per test

## Quality Assessment (0-10)

### Test 1 - Rate-Limited API Client:
#### Required Features:
- [ ] Configurable rate limiting implementation
- [ ] Exponential backoff retry logic
- [ ] Async/concurrent request handling
- [ ] Request queuing mechanism
- [ ] Circuit breaker pattern
- [ ] Comprehensive error handling
- [ ] Logging and metrics
- [ ] GET and POST support

#### Code Quality:
- [ ] Type hints throughout
- [ ] Comprehensive docstrings
- [ ] Production-ready error handling
- [ ] Clean architecture
- Quality Score: ___/10

### Test 2 - Concurrency Debugging:
#### Bugs Found:
- [ ] Race condition in task checking
- [ ] Deadlock potential identified
- [ ] Memory leak in processing_tasks
- [ ] Error propagation issues
- [ ] Thread-safety violations

#### Fix Quality:
- [ ] All bugs correctly identified
- [ ] Root causes explained
- [ ] Proper fixes implemented
- [ ] Tests verify fixes
- Quality Score: ___/10

### Test 3 - Vehicle Routing Optimization:
#### Mathematical Formulation:
- [ ] Complete ILP/MILP formulation
- [ ] NP-hardness proof
- [ ] Approximation algorithm
- [ ] Complexity analysis
- [ ] Approximation bounds

#### Implementation:
- [ ] Working algorithm
- [ ] Handles all constraints
- [ ] Efficient implementation
- [ ] Visualization included
- Quality Score: ___/10

### Test 4 - Framework Analysis:
#### Analysis Depth:
- [ ] All 5 frameworks covered
- [ ] Architecture patterns detailed
- [ ] Performance benchmarks
- [ ] Scalability analysis
- [ ] Security assessment
- [ ] Cost projections
- [ ] Risk matrix
- [ ] Implementation roadmap

#### Practical Value:
- [ ] Executive summary quality
- [ ] Technical comparison matrix
- [ ] Architecture diagrams
- [ ] Actionable recommendations
- Quality Score: ___/10

## Overall Assessment
- **Average Quality Score**: ___/10
- **Completeness**: ___% of requirements met
- **Production Readiness**: [High/Medium/Low]
- **Technical Depth**: [Exceptional/Strong/Adequate]

## Token Usage
- Test 1: ___ tokens (estimated)
- Test 2: ___ tokens (estimated)
- Test 3: ___ tokens (estimated)
- Test 4: ___ tokens (estimated)
- **Total**: ___ tokens

## Complexity Analysis
These HIGH difficulty tests push the boundaries:
1. **Test 1**: Requires deep async programming knowledge
2. **Test 2**: Demands expertise in concurrency and debugging
3. **Test 3**: Needs advanced math and algorithm skills
4. **Test 4**: Requires broad architectural knowledge

## Expected Outcomes
### For Claude Native:
- May struggle with complete solutions in single pass
- Could miss subtle concurrency bugs
- Mathematical proofs may be incomplete
- Framework analysis breadth vs depth tradeoff

### For Swarm Configurations:
- Specialized agents could excel in their domains
- Coordination crucial for integrated solutions
- High overhead but potentially superior results
- Best suited for Config C (5 agents) or higher

## Notes
- These tests are OPTIONAL due to high complexity
- Designed to find limits of single vs multi-agent
- Success criteria more flexible than simple/moderate
- Focus on approach quality over perfect solutions
EOF

echo ""
echo "✅ Baseline HIGH DIFFICULTY test prompts ready!"
echo "📊 Total test time: $total_duration seconds"
echo "📁 Results saved to: $results_dir"
echo ""
echo "⚠️  IMPORTANT NOTES:"
echo "1. These are OPTIONAL advanced tests"
echo "2. Expect 15-30 minutes per test"
echo "3. Focus on approach and reasoning quality"
echo "4. Perfect solutions not required"
echo "5. Best for comparing swarm benefits on complex tasks"