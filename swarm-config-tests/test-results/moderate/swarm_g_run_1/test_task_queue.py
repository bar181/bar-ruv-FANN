"""
Unit tests for the TaskQueue class.

This module contains comprehensive tests for all TaskQueue functionality,
including priority ordering, FIFO within same priority, thread safety,
and error handling.
"""

import unittest
import threading
import time
from task_queue import TaskQueue, Priority


class TestTaskQueue(unittest.TestCase):
    """Test cases for the TaskQueue class."""
    
    def setUp(self):
        """Set up a fresh TaskQueue for each test."""
        self.queue = TaskQueue()
        
    def test_empty_queue(self):
        """Test behavior of an empty queue."""
        self.assertTrue(self.queue.is_empty())
        self.assertEqual(self.queue.size(), 0)
        self.assertIsNone(self.queue.get_next_task())
        self.assertIsNone(self.queue.peek())
        
    def test_single_task(self):
        """Test adding and retrieving a single task."""
        task = "Test task"
        self.queue.add_task(task, Priority.MEDIUM)
        
        self.assertFalse(self.queue.is_empty())
        self.assertEqual(self.queue.size(), 1)
        self.assertEqual(self.queue.peek(), task)
        self.assertEqual(self.queue.get_next_task(), task)
        self.assertTrue(self.queue.is_empty())
        
    def test_priority_ordering(self):
        """Test that tasks are returned in priority order."""
        # Add tasks in mixed priority order
        self.queue.add_task("Low priority", Priority.LOW)
        self.queue.add_task("High priority 1", Priority.HIGH)
        self.queue.add_task("Medium priority", Priority.MEDIUM)
        self.queue.add_task("High priority 2", Priority.HIGH)
        
        # Should get tasks in priority order: HIGH, HIGH, MEDIUM, LOW
        self.assertEqual(self.queue.get_next_task(), "High priority 1")
        self.assertEqual(self.queue.get_next_task(), "High priority 2")
        self.assertEqual(self.queue.get_next_task(), "Medium priority")
        self.assertEqual(self.queue.get_next_task(), "Low priority")
        
    def test_fifo_within_priority(self):
        """Test FIFO ordering for tasks with the same priority."""
        # Add multiple tasks with same priority
        tasks = ["Task 1", "Task 2", "Task 3", "Task 4"]
        for task in tasks:
            self.queue.add_task(task, Priority.MEDIUM)
            
        # Should get tasks in FIFO order
        for task in tasks:
            self.assertEqual(self.queue.get_next_task(), task)
            
    def test_mixed_operations(self):
        """Test mixed add and remove operations."""
        self.queue.add_task("Task 1", Priority.HIGH)
        self.queue.add_task("Task 2", Priority.LOW)
        
        self.assertEqual(self.queue.get_next_task(), "Task 1")
        
        self.queue.add_task("Task 3", Priority.HIGH)
        self.queue.add_task("Task 4", Priority.MEDIUM)
        
        self.assertEqual(self.queue.get_next_task(), "Task 3")
        self.assertEqual(self.queue.get_next_task(), "Task 4")
        self.assertEqual(self.queue.get_next_task(), "Task 2")
        
    def test_invalid_priority(self):
        """Test error handling for invalid priorities."""
        with self.assertRaises(ValueError):
            self.queue.add_task("Task", 0)  # Too low
            
        with self.assertRaises(ValueError):
            self.queue.add_task("Task", 4)  # Too high
            
        with self.assertRaises(ValueError):
            self.queue.add_task("Task", "HIGH")  # Wrong type
            
    def test_thread_safety(self):
        """Test thread-safe operations."""
        num_threads = 5
        tasks_per_thread = 100
        
        def add_tasks(thread_id):
            """Add multiple tasks from a single thread."""
            for i in range(tasks_per_thread):
                priority = Priority.HIGH if i % 3 == 0 else Priority.MEDIUM
                self.queue.add_task(f"Task {i} from Thread {thread_id}", priority)
                
        # Create and start threads
        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=add_tasks, args=(i,))
            threads.append(t)
            t.start()
            
        # Wait for all threads to complete
        for t in threads:
            t.join()
            
        # Verify all tasks were added
        self.assertEqual(self.queue.size(), num_threads * tasks_per_thread)
        
        # Verify we can retrieve all tasks
        count = 0
        while not self.queue.is_empty():
            task = self.queue.get_next_task()
            self.assertIsNotNone(task)
            count += 1
            
        self.assertEqual(count, num_threads * tasks_per_thread)
        
    def test_peek_does_not_modify_queue(self):
        """Test that peek doesn't remove items from the queue."""
        self.queue.add_task("Task 1", Priority.HIGH)
        self.queue.add_task("Task 2", Priority.LOW)
        
        # Peek multiple times
        for _ in range(3):
            self.assertEqual(self.queue.peek(), "Task 1")
            self.assertEqual(self.queue.size(), 2)
            
        # Verify queue is unchanged
        self.assertEqual(self.queue.get_next_task(), "Task 1")
        self.assertEqual(self.queue.get_next_task(), "Task 2")


def run_tests():
    """Run all unit tests and display results."""
    print("=== Running TaskQueue Unit Tests ===\n")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTaskQueue)
    
    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print(f"\nTests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_tests()