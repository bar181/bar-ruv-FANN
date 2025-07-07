"""
TaskQueue: A thread-safe priority queue implementation for task management.

This module provides a priority queue that supports HIGH, MEDIUM, and LOW priority levels,
with FIFO ordering for tasks of the same priority. The implementation is thread-safe
using threading.Lock.
"""

import heapq
import threading
from typing import Any, Optional, Tuple, List
from enum import IntEnum
import time


class Priority(IntEnum):
    """Priority levels for tasks in the queue."""
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class TaskQueue:
    """
    A thread-safe priority queue for managing tasks.
    
    Tasks are ordered by priority (HIGH > MEDIUM > LOW), with FIFO ordering
    for tasks of the same priority. All operations are thread-safe.
    
    Attributes:
        _lock: Threading lock for thread-safe operations
        _queue: Internal heap queue storing (priority, timestamp, task) tuples
        _counter: Monotonic counter for FIFO ordering within same priority
    """
    
    def __init__(self) -> None:
        """Initialize an empty TaskQueue."""
        self._lock = threading.Lock()
        self._queue: List[Tuple[int, float, Any]] = []
        self._counter = 0
        
    def add_task(self, task: Any, priority: int) -> None:
        """
        Add a task to the queue with the specified priority.
        
        Args:
            task: The task to add (can be any object)
            priority: Priority level (1=HIGH, 2=MEDIUM, 3=LOW)
            
        Raises:
            ValueError: If priority is not a valid Priority value
        """
        # Validate priority
        if not isinstance(priority, int) or priority not in [p.value for p in Priority]:
            raise ValueError(f"Invalid priority: {priority}. Must be 1 (HIGH), 2 (MEDIUM), or 3 (LOW)")
            
        with self._lock:
            # Use counter for FIFO ordering within same priority
            self._counter += 1
            heapq.heappush(self._queue, (priority, self._counter, task))
            
    def get_next_task(self) -> Optional[Any]:
        """
        Remove and return the highest priority task from the queue.
        
        Returns:
            The highest priority task, or None if the queue is empty
        """
        with self._lock:
            if not self._queue:
                return None
            
            _, _, task = heapq.heappop(self._queue)
            return task
            
    def peek(self) -> Optional[Any]:
        """
        Return the highest priority task without removing it from the queue.
        
        Returns:
            The highest priority task, or None if the queue is empty
        """
        with self._lock:
            if not self._queue:
                return None
                
            return self._queue[0][2]
            
    def is_empty(self) -> bool:
        """
        Check if the queue is empty.
        
        Returns:
            True if the queue is empty, False otherwise
        """
        with self._lock:
            return len(self._queue) == 0
            
    def size(self) -> int:
        """
        Get the number of tasks in the queue.
        
        Returns:
            The number of tasks currently in the queue
        """
        with self._lock:
            return len(self._queue)


# Usage example
def usage_example():
    """Demonstrate basic usage of the TaskQueue class."""
    print("=== TaskQueue Usage Example ===\n")
    
    # Create a task queue
    queue = TaskQueue()
    
    # Add tasks with different priorities
    queue.add_task("Fix critical bug", Priority.HIGH)
    queue.add_task("Implement new feature", Priority.MEDIUM)
    queue.add_task("Update documentation", Priority.LOW)
    queue.add_task("Security patch", Priority.HIGH)
    queue.add_task("Code review", Priority.MEDIUM)
    
    # Process tasks in priority order
    print("Processing tasks in priority order:")
    while not queue.is_empty():
        task = queue.get_next_task()
        print(f"- {task}")
        
    print("\nQueue is now empty:", queue.is_empty())
    
    # Demonstrate thread safety
    print("\n=== Thread Safety Example ===\n")
    
    queue2 = TaskQueue()
    tasks_added = []
    
    def worker(worker_id: int, num_tasks: int):
        """Worker thread that adds tasks to the queue."""
        for i in range(num_tasks):
            task = f"Task {i} from Worker {worker_id}"
            priority = Priority.HIGH if i == 0 else Priority.MEDIUM
            queue2.add_task(task, priority)
            tasks_added.append(task)
            time.sleep(0.001)  # Small delay to increase chance of interleaving
            
    # Create and start multiple threads
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker, args=(i, 3))
        threads.append(t)
        t.start()
        
    # Wait for all threads to complete
    for t in threads:
        t.join()
        
    print(f"Total tasks added by {len(threads)} threads: {queue2.size()}")
    print("All tasks processed successfully!")


if __name__ == "__main__":
    usage_example()