"""
Comprehensive unit tests for the fixed DistributedTaskProcessor

Tests verify all bug fixes:
1. No race conditions in duplicate task detection
2. No deadlocks under concurrent load
3. No memory leaks over time
4. Proper error propagation
5. Result integrity under stress
"""

import unittest
import threading
import time
import random
import gc
import tracemalloc
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch
import logging

from fixed_task_processor import DistributedTaskProcessor, Task, TaskResult


class TestDistributedTaskProcessor(unittest.TestCase):
    """Test suite for DistributedTaskProcessor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = DistributedTaskProcessor(num_workers=4)
        # Reduce cleanup interval for faster tests
        self.processor._cleanup_interval = 1
        
    def tearDown(self):
        """Clean up after tests"""
        self.processor.shutdown_gracefully(timeout=5)
    
    def test_basic_task_processing(self):
        """Test basic task submission and completion"""
        task = Task(id="test_1", payload={"data": "test"})
        task_id = self.processor.submit_task(task)
        
        # Wait for result
        result = self.processor.get_result(task_id, timeout=5)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["task_id"], "test_1")
        self.assertEqual(result["data"]["data"], "test")
        
        # Check stats
        stats = self.processor.get_stats()
        self.assertEqual(stats['tasks_submitted'], 1)
        self.assertEqual(stats['tasks_completed'], 1)
    
    def test_race_condition_prevention(self):
        """Test that duplicate task processing is prevented"""
        # Create a task that takes longer to process
        def slow_process(self, task):
            time.sleep(0.5)
            return {"task_id": task.id, "result": "processed"}
        
        # Temporarily replace process method
        original_process = self.processor._process_task
        self.processor._process_task = lambda task: slow_process(self.processor, task)
        
        try:
            # Submit same task from multiple threads
            task_id = "duplicate_test"
            results = []
            errors = []
            
            def submit_duplicate():
                try:
                    task = Task(id=task_id, payload={"data": "test"})
                    self.processor.submit_task(task)
                    results.append("submitted")
                except ValueError as e:
                    errors.append(str(e))
            
            # Try to submit same task ID multiple times
            threads = []
            for _ in range(5):
                thread = threading.Thread(target=submit_duplicate)
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            # Only one should succeed, others should get ValueError
            self.assertEqual(len(results), 1)
            self.assertEqual(len(errors), 4)
            self.assertTrue(all("already exists" in e for e in errors))
            
        finally:
            self.processor._process_task = original_process
    
    def test_no_deadlock_under_load(self):
        """Test that no deadlocks occur under heavy concurrent load"""
        num_tasks = 100
        results = []
        callbacks_executed = []
        
        def callback(result=None, error=None):
            callbacks_executed.append((result, error))
        
        # Submit many tasks concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            for i in range(num_tasks):
                task = Task(
                    id=f"load_test_{i}",
                    payload={"index": i},
                    callback=callback
                )
                future = executor.submit(self.processor.submit_task, task)
                futures.append(future)
            
            # Wait for all submissions
            for future in futures:
                future.result()
        
        # Wait for all tasks to complete (with timeout to detect deadlock)
        start_time = time.time()
        timeout = 30
        
        while len(results) < num_tasks and time.time() - start_time < timeout:
            for i in range(num_tasks):
                task_id = f"load_test_{i}"
                if task_id not in results:
                    result = self.processor.get_result(task_id, timeout=0)
                    if result:
                        results.append(task_id)
            time.sleep(0.1)
        
        # Verify all tasks completed
        self.assertEqual(len(results), num_tasks)
        self.assertGreater(len(callbacks_executed), 0)
        
        # No deadlock if we got here
        elapsed = time.time() - start_time
        self.assertLess(elapsed, timeout, "Possible deadlock detected")
    
    def test_memory_leak_prevention(self):
        """Test that old results are cleaned up to prevent memory leaks"""
        # Track memory usage
        tracemalloc.start()
        
        # Submit many tasks
        num_tasks = 1000
        for i in range(num_tasks):
            task = Task(id=f"memory_test_{i}", payload={"data": f"test_{i}" * 100})
            self.processor.submit_task(task)
        
        # Wait for all tasks to complete
        time.sleep(2)
        
        # Force garbage collection
        gc.collect()
        
        # Get baseline memory
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        baseline_results = len(self.processor.result_store)
        
        # Wait for cleanup cycle
        time.sleep(2)
        
        # Check that old results were cleaned up
        current_results = len(self.processor.result_store)
        self.assertLess(current_results, baseline_results, 
                       "Results should be cleaned up over time")
        
        # Memory should not grow unbounded
        gc.collect()
        final_mem, _ = tracemalloc.get_traced_memory()
        
        # Allow some growth but not proportional to task count
        memory_growth = final_mem - current_mem
        self.assertLess(memory_growth, num_tasks * 1000, 
                       "Memory growth should be bounded")
        
        tracemalloc.stop()
    
    def test_error_propagation(self):
        """Test that errors are properly propagated to callers"""
        # Create a task that will fail
        def failing_process(self, task):
            raise ValueError(f"Task {task.id} intentionally failed")
        
        original_process = self.processor._process_task
        self.processor._process_task = lambda task: failing_process(self.processor, task)
        
        try:
            # Submit task with no retries
            task = Task(id="error_test", payload={"data": "test"}, max_retries=0)
            task_id = self.processor.submit_task(task)
            
            # Wait for task to fail
            time.sleep(1)
            
            # Getting result should raise the error
            with self.assertRaises(ValueError) as context:
                self.processor.get_result(task_id, timeout=5)
            
            self.assertIn("intentionally failed", str(context.exception))
            
            # Check stats
            stats = self.processor.get_stats()
            self.assertEqual(stats['tasks_failed'], 1)
            
        finally:
            self.processor._process_task = original_process
    
    def test_retry_logic(self):
        """Test that retry logic works correctly"""
        attempt_count = 0
        
        def flaky_process(self, task):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception(f"Attempt {attempt_count} failed")
            return {"task_id": task.id, "result": "success", "attempts": attempt_count}
        
        original_process = self.processor._process_task
        self.processor._process_task = lambda task: flaky_process(self.processor, task)
        
        try:
            # Submit task that will fail twice then succeed
            task = Task(id="retry_test", payload={"data": "test"}, max_retries=3)
            task_id = self.processor.submit_task(task)
            
            # Wait for retries and success
            result = self.processor.get_result(task_id, timeout=10)
            
            self.assertIsNotNone(result)
            self.assertEqual(result["result"], "success")
            self.assertEqual(result["attempts"], 3)
            
            # Check retry stats
            stats = self.processor.get_stats()
            self.assertEqual(stats['tasks_retried'], 2)
            self.assertEqual(stats['tasks_completed'], 1)
            
        finally:
            self.processor._process_task = original_process
    
    def test_callback_execution(self):
        """Test that callbacks are executed correctly"""
        callback_results = []
        callback_errors = []
        callback_event = threading.Event()
        
        def test_callback(result=None, error=None):
            if error:
                callback_errors.append(error)
            else:
                callback_results.append(result)
            callback_event.set()
        
        # Test successful callback
        task = Task(id="callback_test", payload={"data": "test"}, callback=test_callback)
        self.processor.submit_task(task)
        
        # Wait for callback
        self.assertTrue(callback_event.wait(timeout=5))
        self.assertEqual(len(callback_results), 1)
        self.assertEqual(callback_results[0]["task_id"], "callback_test")
        
        # Test error callback
        callback_event.clear()
        
        def failing_process(self, task):
            raise ValueError("Test error")
        
        original_process = self.processor._process_task
        self.processor._process_task = lambda task: failing_process(self.processor, task)
        
        try:
            task = Task(id="callback_error_test", payload={"data": "test"}, 
                       callback=test_callback, max_retries=0)
            self.processor.submit_task(task)
            
            # Wait for error callback
            self.assertTrue(callback_event.wait(timeout=5))
            self.assertEqual(len(callback_errors), 1)
            self.assertIsInstance(callback_errors[0], ValueError)
            
        finally:
            self.processor._process_task = original_process
    
    def test_concurrent_result_access(self):
        """Test that concurrent result access is thread-safe"""
        task_id = "concurrent_result_test"
        task = Task(id=task_id, payload={"data": "test"})
        self.processor.submit_task(task)
        
        # Wait for completion
        result = self.processor.get_result(task_id, timeout=5)
        self.assertIsNotNone(result)
        
        # Access result from multiple threads concurrently
        results = []
        errors = []
        
        def access_result():
            try:
                for _ in range(100):
                    r = self.processor.get_result(task_id)
                    results.append(r)
            except Exception as e:
                errors.append(e)
        
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=access_result)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should have no errors and all results should be identical
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(results), 1000)
        self.assertTrue(all(r == results[0] for r in results))
    
    def test_graceful_shutdown(self):
        """Test graceful shutdown behavior"""
        # Submit some tasks
        for i in range(10):
            task = Task(id=f"shutdown_test_{i}", payload={"data": f"test_{i}"})
            self.processor.submit_task(task)
        
        # Start shutdown
        shutdown_thread = threading.Thread(
            target=self.processor.shutdown_gracefully,
            args=(5,)
        )
        shutdown_thread.start()
        
        # Try to submit task during shutdown - should still work initially
        try:
            task = Task(id="during_shutdown", payload={"data": "test"})
            self.processor.submit_task(task)
        except:
            pass  # May fail if shutdown progressed
        
        # Wait for shutdown
        shutdown_thread.join()
        
        # Verify shutdown completed
        self.assertTrue(self.processor.shutdown)
        
        # Workers should have stopped
        for worker in self.processor.workers:
            self.assertFalse(worker.is_alive())
    
    def test_batch_submit(self):
        """Test batch submission context manager"""
        submitted_tasks = []
        
        # Use batch submit
        with self.processor.batch_submit():
            for i in range(5):
                task = Task(id=f"batch_{i}", payload={"data": f"test_{i}"})
                self.processor.submit_task(task)
                submitted_tasks.append(task.id)
        
        # All tasks should be submitted after context exit
        time.sleep(1)
        
        for task_id in submitted_tasks:
            self.assertTrue(self.processor.is_task_complete(task_id) or 
                          task_id in self.processor.processing_tasks)
    
    def test_stress_test(self):
        """Comprehensive stress test with all features"""
        num_tasks = 500
        results = []
        errors = []
        
        def random_callback(result=None, error=None):
            if error:
                errors.append(error)
            else:
                results.append(result)
        
        # Configure some tasks to fail
        fail_indices = set(random.sample(range(num_tasks), num_tasks // 10))
        
        def stress_process(self, task):
            index = task.payload["index"]
            if index in fail_indices and task.retry_count == 0:
                raise Exception(f"Task {index} failed on first attempt")
            time.sleep(random.uniform(0.01, 0.1))
            return {"task_id": task.id, "index": index}
        
        original_process = self.processor._process_task
        self.processor._process_task = lambda task: stress_process(self.processor, task)
        
        try:
            # Submit all tasks concurrently
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = []
                for i in range(num_tasks):
                    task = Task(
                        id=f"stress_{i}",
                        payload={"index": i},
                        callback=random_callback if i % 2 == 0 else None,
                        max_retries=2
                    )
                    future = executor.submit(self.processor.submit_task, task)
                    futures.append(future)
                
                # Wait for all submissions
                for future in futures:
                    future.result()
            
            # Wait for all tasks to complete
            completed = 0
            timeout = 60
            while completed < num_tasks and time.time() - start_time < timeout:
                completed = sum(1 for i in range(num_tasks) 
                              if self.processor.is_task_complete(f"stress_{i}"))
                time.sleep(0.5)
            
            # Verify results
            self.assertEqual(completed, num_tasks)
            
            # Check stats
            stats = self.processor.get_stats()
            self.assertEqual(stats['tasks_submitted'], num_tasks)
            self.assertGreater(stats['tasks_completed'], 0)
            self.assertGreater(stats['tasks_retried'], 0)
            
            # Verify callbacks were executed
            self.assertGreater(len(results), 0)
            
            elapsed = time.time() - start_time
            print(f"Stress test completed {num_tasks} tasks in {elapsed:.2f} seconds")
            
        finally:
            self.processor._process_task = original_process


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main(verbosity=2)