"""
TaskQueue Implementation - A thread-safe priority queue for task management
Team 1 - 8-agent dual team swarm configuration
"""

import heapq
import threading
from typing import Any, Optional, Tuple, List
from enum import IntEnum
from datetime import datetime


class Priority(IntEnum):
    """Priority levels for tasks"""
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class TaskQueue:
    """
    A thread-safe priority queue for managing tasks.
    
    Tasks are ordered by priority (HIGH=1, MEDIUM=2, LOW=3).
    Within the same priority, tasks maintain FIFO order.
    """
    
    def __init__(self):
        """Initialize an empty TaskQueue with thread safety."""
        self._queue: List[Tuple[int, int, Any]] = []
        self._counter = 0  # For maintaining FIFO within same priority
        self._lock = threading.Lock()
    
    def add_task(self, task: Any, priority: int) -> None:
        """
        Add a task to the queue with specified priority.
        
        Args:
            task: The task to add (can be any object)
            priority: Priority level (1=HIGH, 2=MEDIUM, 3=LOW)
            
        Raises:
            ValueError: If priority is not 1, 2, or 3
        """
        if priority not in [Priority.HIGH, Priority.MEDIUM, Priority.LOW]:
            raise ValueError(f"Invalid priority {priority}. Must be 1 (HIGH), 2 (MEDIUM), or 3 (LOW)")
        
        with self._lock:
            # Use counter to maintain FIFO for same priority
            heapq.heappush(self._queue, (priority, self._counter, task))
            self._counter += 1
    
    def get_next_task(self) -> Optional[Any]:
        """
        Remove and return the highest priority task.
        
        Returns:
            The next task, or None if queue is empty
        """
        with self._lock:
            if not self._queue:
                return None
            
            _, _, task = heapq.heappop(self._queue)
            return task
    
    def peek(self) -> Optional[Any]:
        """
        Return the highest priority task without removing it.
        
        Returns:
            The next task, or None if queue is empty
        """
        with self._lock:
            if not self._queue:
                return None
            
            return self._queue[0][2]
    
    def is_empty(self) -> bool:
        """
        Check if the queue is empty.
        
        Returns:
            True if empty, False otherwise
        """
        with self._lock:
            return len(self._queue) == 0
    
    def size(self) -> int:
        """
        Get the number of tasks in the queue.
        
        Returns:
            Number of tasks in queue
        """
        with self._lock:
            return len(self._queue)
    
    def clear(self) -> None:
        """Remove all tasks from the queue."""
        with self._lock:
            self._queue.clear()
            self._counter = 0


# Usage example
def usage_example():
    """Demonstrate basic usage of TaskQueue."""
    print("=== TaskQueue Usage Example ===")
    
    queue = TaskQueue()
    
    # Add tasks with different priorities
    queue.add_task("Low priority task 1", Priority.LOW)
    queue.add_task("High priority task 1", Priority.HIGH)
    queue.add_task("Medium priority task 1", Priority.MEDIUM)
    queue.add_task("High priority task 2", Priority.HIGH)
    queue.add_task("Low priority task 2", Priority.LOW)
    
    print(f"Queue size: {queue.size()}")
    print(f"Next task (peek): {queue.peek()}")
    
    # Process tasks in priority order
    print("\nProcessing tasks in priority order:")
    while not queue.is_empty():
        task = queue.get_next_task()
        print(f"- {task}")
    
    print(f"\nQueue empty: {queue.is_empty()}")


# Unit tests
import unittest
import time
import random


class TestTaskQueue(unittest.TestCase):
    """Unit tests for TaskQueue class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.queue = TaskQueue()
    
    def test_empty_queue(self):
        """Test behavior of empty queue."""
        self.assertTrue(self.queue.is_empty())
        self.assertIsNone(self.queue.get_next_task())
        self.assertIsNone(self.queue.peek())
        self.assertEqual(self.queue.size(), 0)
    
    def test_add_and_get_single_task(self):
        """Test adding and retrieving a single task."""
        task = "Test task"
        self.queue.add_task(task, Priority.MEDIUM)
        
        self.assertFalse(self.queue.is_empty())
        self.assertEqual(self.queue.size(), 1)
        self.assertEqual(self.queue.peek(), task)
        self.assertEqual(self.queue.get_next_task(), task)
        self.assertTrue(self.queue.is_empty())
    
    def test_priority_ordering(self):
        """Test that tasks are retrieved in priority order."""
        self.queue.add_task("Low", Priority.LOW)
        self.queue.add_task("High", Priority.HIGH)
        self.queue.add_task("Medium", Priority.MEDIUM)
        
        self.assertEqual(self.queue.get_next_task(), "High")
        self.assertEqual(self.queue.get_next_task(), "Medium")
        self.assertEqual(self.queue.get_next_task(), "Low")
    
    def test_fifo_within_same_priority(self):
        """Test FIFO ordering for tasks with same priority."""
        tasks = ["First", "Second", "Third", "Fourth"]
        for task in tasks:
            self.queue.add_task(task, Priority.MEDIUM)
        
        for task in tasks:
            self.assertEqual(self.queue.get_next_task(), task)
    
    def test_invalid_priority(self):
        """Test that invalid priorities raise ValueError."""
        with self.assertRaises(ValueError):
            self.queue.add_task("Task", 0)
        
        with self.assertRaises(ValueError):
            self.queue.add_task("Task", 4)
        
        with self.assertRaises(ValueError):
            self.queue.add_task("Task", "HIGH")
    
    def test_thread_safety(self):
        """Test thread-safe operations."""
        results = []
        errors = []
        
        def producer(queue, n):
            """Add n tasks to queue."""
            try:
                for i in range(n):
                    priority = random.choice([Priority.HIGH, Priority.MEDIUM, Priority.LOW])
                    queue.add_task(f"Task-{i}", priority)
                    time.sleep(0.0001)
            except Exception as e:
                errors.append(e)
        
        def consumer(queue, n):
            """Consume n tasks from queue."""
            try:
                consumed = 0
                while consumed < n:
                    task = queue.get_next_task()
                    if task:
                        results.append(task)
                        consumed += 1
                    time.sleep(0.0001)
            except Exception as e:
                errors.append(e)
        
        # Create threads
        threads = []
        n_tasks = 50
        
        # Start producers
        for i in range(3):
            t = threading.Thread(target=producer, args=(self.queue, n_tasks))
            threads.append(t)
            t.start()
        
        # Start consumers
        for i in range(2):
            t = threading.Thread(target=consumer, args=(self.queue, n_tasks * 3 // 2))
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Verify no errors occurred
        self.assertEqual(len(errors), 0, f"Thread errors: {errors}")
        
        # Verify all tasks were consumed
        self.assertEqual(len(results), n_tasks * 3)
    
    def test_clear_queue(self):
        """Test clearing the queue."""
        for i in range(5):
            self.queue.add_task(f"Task {i}", Priority.MEDIUM)
        
        self.assertEqual(self.queue.size(), 5)
        self.queue.clear()
        self.assertEqual(self.queue.size(), 0)
        self.assertTrue(self.queue.is_empty())


if __name__ == "__main__":
    # Run usage example
    usage_example()
    
    print("\n\n=== Running Unit Tests ===")
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)