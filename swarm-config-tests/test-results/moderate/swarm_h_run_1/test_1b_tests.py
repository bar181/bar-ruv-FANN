#!/usr/bin/env python3
"""
Comprehensive unit tests for TaskQueue class
QA Division - Test 1b: Code Generation (Moderate)
"""

import unittest
import threading
import time
from test_1b_taskqueue import TaskQueue, Priority


class TestTaskQueue(unittest.TestCase):
    """Test cases for TaskQueue class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.queue = TaskQueue()
    
    def test_empty_queue(self):
        """Test empty queue behavior"""
        self.assertTrue(self.queue.is_empty())
        self.assertEqual(self.queue.size(), 0)
        
        # Test exceptions on empty queue
        with self.assertRaises(IndexError):
            self.queue.get_next_task()
        
        with self.assertRaises(IndexError):
            self.queue.peek()
    
    def test_single_task(self):
        """Test adding and removing single task"""
        task = "Test task"
        self.queue.add_task(task, Priority.HIGH)
        
        self.assertFalse(self.queue.is_empty())
        self.assertEqual(self.queue.size(), 1)
        self.assertEqual(self.queue.peek(), task)
        self.assertEqual(self.queue.get_next_task(), task)
        self.assertTrue(self.queue.is_empty())
    
    def test_priority_ordering(self):
        """Test that tasks are returned in priority order"""
        # Add tasks in mixed order
        self.queue.add_task("Low task", Priority.LOW)
        self.queue.add_task("High task", Priority.HIGH)
        self.queue.add_task("Medium task", Priority.MEDIUM)
        
        # Should return in priority order: HIGH, MEDIUM, LOW
        self.assertEqual(self.queue.get_next_task(), "High task")
        self.assertEqual(self.queue.get_next_task(), "Medium task")
        self.assertEqual(self.queue.get_next_task(), "Low task")
    
    def test_fifo_within_priority(self):
        """Test FIFO ordering within same priority"""
        # Add multiple tasks with same priority
        self.queue.add_task("First high", Priority.HIGH)
        time.sleep(0.001)  # Ensure different timestamps
        self.queue.add_task("Second high", Priority.HIGH)
        time.sleep(0.001)
        self.queue.add_task("Third high", Priority.HIGH)
        
        # Should return in FIFO order
        self.assertEqual(self.queue.get_next_task(), "First high")
        self.assertEqual(self.queue.get_next_task(), "Second high")
        self.assertEqual(self.queue.get_next_task(), "Third high")
    
    def test_thread_safety(self):
        """Test thread safety with multiple threads"""
        num_threads = 5
        tasks_per_thread = 10
        results = []
        
        def worker(thread_id):
            """Worker function to add tasks"""
            for i in range(tasks_per_thread):
                self.queue.add_task(f"Task-{thread_id}-{i}", Priority.MEDIUM)
        
        def consumer():
            """Consumer function to get tasks"""
            while True:
                try:
                    task = self.queue.get_next_task()
                    results.append(task)
                except IndexError:
                    break
        
        # Start producer threads
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all producers to finish
        for thread in threads:
            thread.join()
        
        # Start consumer thread
        consumer_thread = threading.Thread(target=consumer)
        consumer_thread.start()
        consumer_thread.join()
        
        # Check results
        self.assertEqual(len(results), num_threads * tasks_per_thread)
        self.assertTrue(self.queue.is_empty())
    
    def test_invalid_inputs(self):
        """Test error handling for invalid inputs"""
        # Test None task
        with self.assertRaises(TypeError):
            self.queue.add_task(None)
        
        # Test invalid priority
        with self.assertRaises(ValueError):
            self.queue.add_task("task", 0)
        
        with self.assertRaises(ValueError):
            self.queue.add_task("task", 4)
        
        with self.assertRaises(ValueError):
            self.queue.add_task("task", -1)
    
    def test_clear_queue(self):
        """Test clearing the queue"""
        # Add some tasks
        self.queue.add_task("Task 1", Priority.HIGH)
        self.queue.add_task("Task 2", Priority.LOW)
        
        self.assertEqual(self.queue.size(), 2)
        
        # Clear queue
        self.queue.clear()
        
        self.assertTrue(self.queue.is_empty())
        self.assertEqual(self.queue.size(), 0)
    
    def test_complex_scenario(self):
        """Test complex scenario with mixed operations"""
        # Add initial tasks
        self.queue.add_task("Initial low", Priority.LOW)
        self.queue.add_task("Initial high", Priority.HIGH)
        
        # Get one task
        task = self.queue.get_next_task()
        self.assertEqual(task, "Initial high")
        
        # Add more tasks
        self.queue.add_task("New medium", Priority.MEDIUM)
        self.queue.add_task("New high", Priority.HIGH)
        
        # Check peek doesn't modify queue
        peek_task = self.queue.peek()
        self.assertEqual(peek_task, "New high")
        self.assertEqual(self.queue.size(), 3)
        
        # Process remaining tasks
        remaining = []
        while not self.queue.is_empty():
            remaining.append(self.queue.get_next_task())
        
        expected = ["New high", "New medium", "Initial low"]
        self.assertEqual(remaining, expected)


if __name__ == "__main__":
    unittest.main()