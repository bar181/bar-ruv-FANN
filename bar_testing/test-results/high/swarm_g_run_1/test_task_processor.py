"""
Comprehensive test suite for the Fixed Distributed Task Processor

Tests all bug fixes and new functionality:
1. Race condition fixes
2. Deadlock prevention
3. Memory leak prevention
4. Error handling and propagation
5. Result integrity
"""

import unittest
import threading
import time
import random
import queue
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor
import uuid

from fixed_task_processor import (
    DistributedTaskProcessor, Task, TaskResult, TaskStatus
)


class TestDistributedTaskProcessor(unittest.TestCase):
    """Test suite for the fixed task processor"""
    
    def setUp(self):
        """Set up test environment"""
        self.processor = DistributedTaskProcessor(num_workers=4)
    
    def tearDown(self):
        """Clean up after tests"""
        self.processor.shutdown(timeout=10)
    
    def test_basic_task_processing(self):
        """Test basic task submission and processing"""
        task = Task(
            id="test_task_1",
            payload={"data": "test_value"}
        )
        
        task_id = self.processor.submit_task(task)
        self.assertEqual(task_id, "test_task_1")
        
        # Wait for completion
        result = self.processor.wait_for_task(task_id, timeout=5)
        self.assertIsNotNone(result)
        self.assertEqual(result.status, TaskStatus.COMPLETED)
        self.assertEqual(result.task_id, task_id)
    
    def test_race_condition_fix(self):
        """Test that race conditions are properly handled"""
        # Create multiple tasks with same ID to test race condition handling
        task_id = "duplicate_task"
        tasks = [
            Task(id=task_id, payload={"data": f"attempt_{i}"})
            for i in range(5)
        ]
        
        # Submit first task
        submitted_id = self.processor.submit_task(tasks[0])
        self.assertEqual(submitted_id, task_id)
        
        # Try to submit duplicate tasks
        for task in tasks[1:]:
            with self.assertRaises(ValueError):
                self.processor.submit_task(task)
        
        # Wait for original task to complete
        result = self.processor.wait_for_task(task_id, timeout=5)
        self.assertIsNotNone(result)
        self.assertEqual(result.status, TaskStatus.COMPLETED)
    
    def test_concurrent_task_processing(self):
        """Test concurrent processing doesn't cause race conditions"""
        num_tasks = 20
        tasks = []
        
        # Submit tasks concurrently
        def submit_task(task_id):
            task = Task(
                id=f"concurrent_task_{task_id}",
                payload={"data": f"concurrent_data_{task_id}"}
            )
            return self.processor.submit_task(task)
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(submit_task, i) for i in range(num_tasks)]
            submitted_ids = [f.result() for f in futures]
        
        # Wait for all tasks to complete
        results = []
        for task_id in submitted_ids:
            result = self.processor.wait_for_task(task_id, timeout=10)
            if result:
                results.append(result)
        
        # Verify all tasks completed successfully
        self.assertEqual(len(results), num_tasks)
        completed_tasks = [r for r in results if r.status == TaskStatus.COMPLETED]
        self.assertEqual(len(completed_tasks), num_tasks)
    
    def test_memory_leak_prevention(self):
        """Test that processing_tasks set is properly cleaned up"""
        # Submit and process multiple tasks
        num_tasks = 50
        task_ids = []
        
        for i in range(num_tasks):
            task = Task(
                id=f"memory_test_task_{i}",
                payload={"data": f"memory_test_{i}"}
            )
            task_id = self.processor.submit_task(task)
            task_ids.append(task_id)
        
        # Wait for all tasks to complete
        for task_id in task_ids:
            result = self.processor.wait_for_task(task_id, timeout=10)
            self.assertIsNotNone(result)
        
        # Check that processing_tasks set is empty
        with self.processor.processing_lock:
            processing_count = len(self.processor.processing_tasks)
        
        self.assertEqual(processing_count, 0, 
                        "Processing tasks set should be empty after completion")
    
    def test_deadlock_prevention(self):
        """Test that deadlocks are prevented"""
        # Create tasks with callbacks that might cause deadlocks
        callback_results = []
        callback_lock = threading.Lock()
        
        def callback_with_lock(result):
            with callback_lock:
                callback_results.append(result)
                # Simulate some work
                time.sleep(0.1)
        
        # Submit multiple tasks with callbacks
        tasks = []
        for i in range(10):
            task = Task(
                id=f"callback_task_{i}",
                payload={"data": f"callback_data_{i}"},
                callback=callback_with_lock
            )
            tasks.append(task)
        
        # Submit all tasks
        for task in tasks:
            self.processor.submit_task(task)
        
        # Wait for completion
        start_time = time.time()
        while len(callback_results) < len(tasks):
            if time.time() - start_time > 15:  # 15 second timeout
                self.fail("Deadlock detected - callbacks not completing")
            time.sleep(0.1)
        
        self.assertEqual(len(callback_results), len(tasks))
    
    def test_error_handling_and_propagation(self):
        """Test proper error handling and propagation"""
        # Mock the _process_task method to simulate failures
        original_process_task = self.processor._process_task
        
        def failing_process_task(task):
            if "fail" in task.payload.get("data", ""):
                raise ValueError(f"Simulated failure for task {task.id}")
            return original_process_task(task)
        
        self.processor._process_task = failing_process_task
        
        # Submit a task that should fail
        failing_task = Task(
            id="failing_task",
            payload={"data": "fail_this_task"}
        )
        
        task_id = self.processor.submit_task(failing_task)
        
        # Wait for task to fail
        result = self.processor.wait_for_task(task_id, timeout=10)
        self.assertIsNotNone(result)
        self.assertEqual(result.status, TaskStatus.FAILED)
        self.assertIsNotNone(result.error)
        self.assertIn("Simulated failure", result.error)
    
    def test_retry_mechanism(self):
        """Test task retry mechanism"""
        # Track retry attempts
        attempt_count = 0
        original_process_task = self.processor._process_task
        
        def retry_process_task(task):
            nonlocal attempt_count
            attempt_count += 1
            
            if attempt_count < 3:  # Fail first two attempts
                raise ValueError(f"Retry test failure {attempt_count}")
            
            return original_process_task(task)
        
        self.processor._process_task = retry_process_task
        
        # Submit task that will retry
        task = Task(
            id="retry_task",
            payload={"data": "retry_test"},
            max_retries=3
        )
        
        task_id = self.processor.submit_task(task)
        
        # Wait for completion
        result = self.processor.wait_for_task(task_id, timeout=15)
        self.assertIsNotNone(result)
        self.assertEqual(result.status, TaskStatus.COMPLETED)
        self.assertEqual(attempt_count, 3)
    
    def test_result_integrity(self):
        """Test that results are not lost or corrupted"""
        # Submit multiple tasks and verify all results
        num_tasks = 30
        expected_results = {}
        
        for i in range(num_tasks):
            task_id = f"integrity_task_{i}"
            expected_data = f"integrity_data_{i}"
            
            task = Task(
                id=task_id,
                payload={"data": expected_data, "value": i}
            )
            
            self.processor.submit_task(task)
            expected_results[task_id] = {"data": expected_data, "value": i}
        
        # Wait for all tasks and verify results
        actual_results = {}
        for task_id in expected_results:
            result = self.processor.wait_for_task(task_id, timeout=10)
            self.assertIsNotNone(result, f"Result missing for {task_id}")
            self.assertEqual(result.status, TaskStatus.COMPLETED)
            
            # Verify result data integrity
            result_data = result.result
            self.assertIsNotNone(result_data)
            self.assertEqual(result_data["task_id"], task_id)
            self.assertEqual(result_data["data"], expected_results[task_id])
            
            actual_results[task_id] = result_data
        
        # Verify all results received
        self.assertEqual(len(actual_results), num_tasks)
    
    def test_graceful_shutdown(self):
        """Test graceful shutdown behavior"""
        # Submit some tasks
        for i in range(5):
            task = Task(
                id=f"shutdown_task_{i}",
                payload={"data": f"shutdown_data_{i}"}
            )
            self.processor.submit_task(task)
        
        # Shutdown should complete without hanging
        start_time = time.time()
        self.processor.shutdown(timeout=10)
        shutdown_time = time.time() - start_time
        
        self.assertLess(shutdown_time, 12, "Shutdown took too long")
    
    def test_queue_full_handling(self):
        """Test handling of full task queue"""
        # Create processor with small queue
        small_processor = DistributedTaskProcessor(
            num_workers=1,
            max_queue_size=5
        )
        
        try:
            # Fill the queue
            for i in range(5):
                task = Task(
                    id=f"queue_full_task_{i}",
                    payload={"data": f"queue_data_{i}"}
                )
                small_processor.submit_task(task)
            
            # Next task should raise queue.Full
            overflow_task = Task(
                id="overflow_task",
                payload={"data": "overflow_data"}
            )
            
            with self.assertRaises(queue.Full):
                small_processor.submit_task(overflow_task)
        
        finally:
            small_processor.shutdown(timeout=5)
    
    def test_statistics_tracking(self):
        """Test statistics collection"""
        # Initial stats
        stats = self.processor.get_stats()
        self.assertEqual(stats['total_tasks'], 0)
        self.assertEqual(stats['completed_tasks'], 0)
        
        # Submit and process tasks
        num_tasks = 10
        for i in range(num_tasks):
            task = Task(
                id=f"stats_task_{i}",
                payload={"data": f"stats_data_{i}"}
            )
            self.processor.submit_task(task)
        
        # Wait for completion
        time.sleep(2)
        
        # Check final stats
        final_stats = self.processor.get_stats()
        self.assertEqual(final_stats['total_tasks'], num_tasks)
        self.assertGreater(final_stats['completed_tasks'], 0)
        self.assertGreaterEqual(final_stats['avg_processing_time'], 0)
    
    def test_batch_submission(self):
        """Test batch submission context manager"""
        with self.processor.batch_submit() as batch:
            # Add multiple tasks
            task_ids = []
            for i in range(5):
                task = Task(
                    id=f"batch_task_{i}",
                    payload={"data": f"batch_data_{i}"}
                )
                task_id = batch.add_task(task)
                task_ids.append(task_id)
            
            # Wait for all tasks
            results = batch.wait_all(timeout=10)
            self.assertEqual(len(results), 5)
            
            # Verify all completed
            completed_results = [r for r in results if r.status == TaskStatus.COMPLETED]
            self.assertEqual(len(completed_results), 5)
    
    def test_context_manager(self):
        """Test context manager functionality"""
        with DistributedTaskProcessor(num_workers=2) as processor:
            # Submit task
            task = Task(
                id="context_task",
                payload={"data": "context_data"}
            )
            task_id = processor.submit_task(task)
            
            # Wait for completion
            result = processor.wait_for_task(task_id, timeout=5)
            self.assertIsNotNone(result)
            self.assertEqual(result.status, TaskStatus.COMPLETED)
        
        # Processor should be shut down after context exit
        self.assertTrue(processor.shutdown_event.is_set())


class TestTaskAndTaskResult(unittest.TestCase):
    """Test Task and TaskResult classes"""
    
    def test_task_creation(self):
        """Test task creation and defaults"""
        task = Task(
            id="test_task",
            payload={"data": "test"}
        )
        
        self.assertEqual(task.id, "test_task")
        self.assertEqual(task.payload, {"data": "test"})
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(task.retry_count, 0)
        self.assertEqual(task.max_retries, 3)
    
    def test_task_auto_id(self):
        """Test automatic ID generation"""
        task = Task(id="", payload={"data": "test"})
        self.assertIsNotNone(task.id)
        self.assertNotEqual(task.id, "")
    
    def test_task_result_creation(self):
        """Test task result creation"""
        result = TaskResult(
            task_id="test_task",
            result={"data": "result"},
            status=TaskStatus.COMPLETED,
            execution_time=0.5
        )
        
        self.assertEqual(result.task_id, "test_task")
        self.assertEqual(result.result, {"data": "result"})
        self.assertEqual(result.status, TaskStatus.COMPLETED)
        self.assertEqual(result.execution_time, 0.5)
        self.assertIsNone(result.error)


class TestStressConditions(unittest.TestCase):
    """Stress tests for the task processor"""
    
    def setUp(self):
        """Set up stress test environment"""
        self.processor = DistributedTaskProcessor(num_workers=8)
    
    def tearDown(self):
        """Clean up after stress tests"""
        self.processor.shutdown(timeout=15)
    
    def test_high_concurrency_stress(self):
        """Stress test with high concurrency"""
        num_tasks = 100
        num_threads = 20
        
        def submit_tasks(thread_id):
            for i in range(num_tasks // num_threads):
                task = Task(
                    id=f"stress_task_{thread_id}_{i}",
                    payload={"thread": thread_id, "task": i}
                )
                self.processor.submit_task(task)
        
        # Submit tasks from multiple threads
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=submit_tasks, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all submission threads
        for thread in threads:
            thread.join()
        
        # Wait for processing to complete
        stats = self.processor.get_stats()
        expected_tasks = stats['total_tasks']
        
        # Wait for completion
        start_time = time.time()
        while True:
            current_stats = self.processor.get_stats()
            if (current_stats['completed_tasks'] + current_stats['failed_tasks']) >= expected_tasks:
                break
            
            if time.time() - start_time > 30:  # 30 second timeout
                self.fail("Stress test timed out")
            
            time.sleep(0.1)
        
        # Verify final state
        final_stats = self.processor.get_stats()
        self.assertEqual(final_stats['total_tasks'], expected_tasks)
        self.assertGreater(final_stats['completed_tasks'], 0)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)