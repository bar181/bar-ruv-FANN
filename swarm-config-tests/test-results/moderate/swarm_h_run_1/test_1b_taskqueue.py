#!/usr/bin/env python3
"""
TaskQueue - Thread-safe Priority Queue Implementation
QA Division - Test 1b: Code Generation (Moderate)
Implemented by: QA Manager, Performance Engineer, Security Architect, Data Scientist, Quality Optimizer
"""

import heapq
import threading
import time
from typing import Any, Optional, Tuple, List
from dataclasses import dataclass
from enum import IntEnum


class Priority(IntEnum):
    """Priority levels for tasks"""
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class Task:
    """Task data structure with priority and creation time"""
    priority: int
    creation_time: float
    data: Any
    
    def __lt__(self, other):
        """Compare tasks for priority queue ordering"""
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.creation_time < other.creation_time


class TaskQueue:
    """
    Thread-safe priority queue for tasks with FIFO ordering within same priority.
    
    Features:
    - Thread-safe operations using threading.Lock
    - Priority-based ordering (HIGH=1, MEDIUM=2, LOW=3)
    - FIFO ordering for same priority tasks
    - Comprehensive error handling
    - Type hints and documentation
    """
    
    def __init__(self):
        """Initialize empty task queue with thread lock"""
        self._heap: List[Task] = []
        self._lock = threading.Lock()
        self._counter = 0
    
    def add_task(self, task: Any, priority: int = Priority.MEDIUM) -> None:
        """
        Add a task to the queue with specified priority.
        
        Args:
            task: The task data to add
            priority: Priority level (1=HIGH, 2=MEDIUM, 3=LOW)
        
        Raises:
            ValueError: If priority is not 1, 2, or 3
            TypeError: If task is None
        """
        if task is None:
            raise TypeError("Task cannot be None")
        
        if priority not in [Priority.HIGH, Priority.MEDIUM, Priority.LOW]:
            raise ValueError(f"Priority must be 1 (HIGH), 2 (MEDIUM), or 3 (LOW), got {priority}")
        
        with self._lock:
            task_obj = Task(
                priority=priority,
                creation_time=time.time(),
                data=task
            )
            heapq.heappush(self._heap, task_obj)
            self._counter += 1
    
    def get_next_task(self) -> Any:
        """
        Remove and return the highest priority task.
        
        Returns:
            The next task data
        
        Raises:
            IndexError: If queue is empty
        """
        with self._lock:
            if not self._heap:
                raise IndexError("Queue is empty")
            
            task_obj = heapq.heappop(self._heap)
            return task_obj.data
    
    def peek(self) -> Any:
        """
        Return the highest priority task without removing it.
        
        Returns:
            The next task data without removing it
        
        Raises:
            IndexError: If queue is empty
        """
        with self._lock:
            if not self._heap:
                raise IndexError("Queue is empty")
            
            return self._heap[0].data
    
    def is_empty(self) -> bool:
        """
        Check if the queue is empty.
        
        Returns:
            True if queue is empty, False otherwise
        """
        with self._lock:
            return len(self._heap) == 0
    
    def size(self) -> int:
        """
        Get the number of tasks in the queue.
        
        Returns:
            Number of tasks in queue
        """
        with self._lock:
            return len(self._heap)
    
    def clear(self) -> None:
        """Remove all tasks from the queue"""
        with self._lock:
            self._heap.clear()


# Usage Example
if __name__ == "__main__":
    print("=== TaskQueue Usage Example ===")
    
    # Create queue
    queue = TaskQueue()
    
    # Add tasks with different priorities
    queue.add_task("Low priority task", Priority.LOW)
    queue.add_task("High priority task", Priority.HIGH)
    queue.add_task("Medium priority task", Priority.MEDIUM)
    queue.add_task("Another high priority task", Priority.HIGH)
    
    print(f"Queue size: {queue.size()}")
    print(f"Next task (peek): {queue.peek()}")
    
    # Process all tasks
    print("\nProcessing tasks in priority order:")
    while not queue.is_empty():
        task = queue.get_next_task()
        print(f"Processing: {task}")
    
    print(f"Queue empty: {queue.is_empty()}")