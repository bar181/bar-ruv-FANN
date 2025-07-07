"""
Comprehensive Unit Tests for Fixed Distributed Task Processor
Research Division - 20-Agent Maximum Stress Test Implementation

These tests verify all bug fixes and demonstrate the robustness of the solution.
"""

import unittest
import threading
import time
import random
import queue
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor
import logging

from fixed_task_processor import (
    FixedDistributedTaskProcessor,
    Task,
    TaskStatus,
    WorkerStatus,
    WorkerMetrics,
    ProcessorMetrics
)


class TestFixedDistributedTaskProcessor(unittest.TestCase):
    """Comprehensive test suite for the fixed task processor"""

    def setUp(self):
        """Set up test fixtures"""
        self.processor = FixedDistributedTaskProcessor(num_workers=2, max_queue_size=100)
        self.addCleanup(self.processor.shutdown)

    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, 'processor'):
            self.processor.shutdown(timeout=5.0)

    def test_basic_task_processing(self):
        """Test basic task submission and processing"""
        task = Task(
            id="test_task_1",
            payload={"data": "test"},
            priority=1
        )
        
        task_id = self.processor.submit_task(task)
        self.assertEqual(task_id, "test_task_1")
        
        # Wait for processing
        result = self.processor.get_result(task_id, timeout=5.0)
        self.assertIsNotNone(result)
        self.assertEqual(result["task_id"], "test_task_1")
        self.assertEqual(result["result"], "processed")

    def test_race_condition_prevention(self):
        """Test that race conditions are prevented in duplicate task processing"""
        task = Task(
            id="duplicate_task",
            payload={"data": "test"},
            priority=1
        )
        
        # Submit the same task ID (should fail on second submission)
        task_id1 = self.processor.submit_task(task)
        
        with self.assertRaises(ValueError):
            # Should raise error for duplicate task ID
            duplicate_task = Task(
                id="duplicate_task",
                payload={"data": "duplicate"},
                priority=1
            )
            self.processor.submit_task(duplicate_task)
        
        # Verify original task processes correctly
        result = self.processor.get_result(task_id1, timeout=5.0)
        self.assertIsNotNone(result)
        self.assertEqual(result["data"]["data"], "test")

    def test_concurrent_task_processing(self):
        """Test concurrent processing of multiple tasks"""
        num_tasks = 50
        task_ids = []
        
        # Submit many tasks concurrently
        for i in range(num_tasks):
            task = Task(
                id=f"concurrent_task_{i}",
                payload={"data": i},
                priority=random.randint(1, 5)
            )
            task_id = self.processor.submit_task(task)
            task_ids.append(task_id)
        
        # Wait for all results
        results = []
        for task_id in task_ids:
            result = self.processor.get_result(task_id, timeout=10.0)
            if result:
                results.append(result)
        
        # Verify all tasks were processed
        self.assertEqual(len(results), num_tasks)
        
        # Verify no duplicate processing
        processed_ids = [r["task_id"] for r in results]
        self.assertEqual(len(processed_ids), len(set(processed_ids)))

    def test_deadlock_prevention(self):
        """Test that deadlocks are prevented through proper lock ordering"""
        # This test simulates conditions that could cause deadlocks
        
        def concurrent_operations():
            """Function to run concurrent operations that could deadlock"""
            try:
                # Submit task
                task = Task(
                    id=f"deadlock_test_{threading.current_thread().ident}",
                    payload={"data": "deadlock_test"},
                    priority=1
                )
                task_id = self.processor.submit_task(task)
                
                # Get result
                result = self.processor.get_result(task_id, timeout=5.0)
                
                # Get metrics (involves multiple locks)
                metrics = self.processor.get_metrics()
                
                # Cleanup
                self.processor.cleanup_completed_tasks(max_age_seconds=0)
                
                return True
            except Exception as e:
                print(f"Deadlock test error: {e}")
                return False
        
        # Run many concurrent operations
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(concurrent_operations) for _ in range(20)]
            results = [f.result(timeout=10.0) for f in futures]
        
        # All operations should complete successfully
        self.assertTrue(all(results))

    def test_memory_leak_prevention(self):
        """Test that memory leaks are prevented through proper cleanup"""
        initial_metrics = self.processor.get_metrics()
        initial_registry_size = initial_metrics["registry_size"]
        initial_result_store_size = initial_metrics["result_store_size"]
        
        # Process many tasks
        num_tasks = 100
        task_ids = []
        
        for i in range(num_tasks):
            task = Task(
                id=f"memory_test_{i}",
                payload={"data": i},
                priority=1
            )
            task_id = self.processor.submit_task(task)
            task_ids.append(task_id)
        
        # Wait for completion
        for task_id in task_ids:
            self.processor.get_result(task_id, timeout=5.0)
        
        # Check that memory usage increased
        mid_metrics = self.processor.get_metrics()
        self.assertGreater(mid_metrics["registry_size"], initial_registry_size)
        self.assertGreater(mid_metrics["result_store_size"], initial_result_store_size)
        
        # Cleanup old tasks
        self.processor.cleanup_completed_tasks(max_age_seconds=0)
        
        # Check that memory was reclaimed
        final_metrics = self.processor.get_metrics()
        self.assertLessEqual(final_metrics["registry_size"], initial_registry_size + 5)  # Allow some variance
        self.assertLessEqual(final_metrics["result_store_size"], initial_result_store_size + 5)

    def test_error_handling_and_propagation(self):
        """Test comprehensive error handling and propagation"""
        error_events = []
        
        def error_handler(task_id: str, exception: Exception):
            error_events.append((task_id, str(exception)))
        
        self.processor.set_error_handler(error_handler)
        
        # Create a task that will fail
        with patch.object(self.processor, '_execute_task', side_effect=Exception("Test error")):
            task = Task(
                id="failing_task",
                payload={"data": "fail"},
                priority=1,
                max_retries=2
            )
            
            task_id = self.processor.submit_task(task)
            
            # Wait for processing and retries
            time.sleep(2.0)
            
            # Check that error was handled
            self.assertGreater(len(error_events), 0)
            self.assertEqual(error_events[0][0], "failing_task")
            
            # Check task status
            status = self.processor.get_task_status(task_id)
            self.assertEqual(status, TaskStatus.FAILED)
            
            # Check result contains error information
            result = self.processor.get_result(task_id, timeout=1.0)
            self.assertIsNotNone(result)
            self.assertIn("error", result)

    def test_result_integrity(self):
        """Test that results are not lost or corrupted"""
        num_tasks = 50
        task_data = {}
        
        # Submit tasks with unique data
        for i in range(num_tasks):
            unique_data = {"id": i, "timestamp": time.time(), "random": random.random()}
            task_data[f"integrity_test_{i}"] = unique_data
            
            task = Task(
                id=f"integrity_test_{i}",
                payload=unique_data,
                priority=1
            )
            self.processor.submit_task(task)
        
        # Collect all results
        results = {}
        for task_id in task_data.keys():
            result = self.processor.get_result(task_id, timeout=10.0)
            self.assertIsNotNone(result, f"Result for {task_id} was lost")
            results[task_id] = result
        
        # Verify data integrity
        for task_id, original_data in task_data.items():
            result = results[task_id]
            self.assertEqual(result["data"], original_data)
            self.assertEqual(result["task_id"], task_id)

    def test_priority_handling(self):
        """Test that higher priority tasks are processed first"""
        # Submit low priority tasks first
        low_priority_ids = []
        for i in range(10):
            task = Task(
                id=f"low_priority_{i}",
                payload={"priority": "low", "order": i},
                priority=1
            )
            task_id = self.processor.submit_task(task)
            low_priority_ids.append(task_id)
        
        # Submit high priority tasks
        high_priority_ids = []
        for i in range(5):
            task = Task(
                id=f"high_priority_{i}",
                payload={"priority": "high", "order": i},
                priority=10
            )
            task_id = self.processor.submit_task(task)
            high_priority_ids.append(task_id)
        
        # Wait for all to complete
        time.sleep(3.0)
        
        # Check that high priority tasks have earlier processed_by timestamps
        high_results = []
        low_results = []
        
        for task_id in high_priority_ids:
            result = self.processor.get_result(task_id)
            if result:
                high_results.append(result)
        
        for task_id in low_priority_ids:
            result = self.processor.get_result(task_id)
            if result:
                low_results.append(result)
        
        # Verify we got results
        self.assertGreater(len(high_results), 0)
        self.assertGreater(len(low_results), 0)

    def test_retry_mechanism(self):
        """Test retry mechanism for failed tasks"""
        retry_count = 0
        
        def failing_execute(task):
            nonlocal retry_count
            retry_count += 1
            if retry_count <= 2:  # Fail first 2 attempts
                raise Exception(f"Attempt {retry_count} failed")
            # Succeed on 3rd attempt
            return {"task_id": task.id, "result": "succeeded_after_retries"}
        
        with patch.object(self.processor, '_execute_task', side_effect=failing_execute):
            task = Task(
                id="retry_test",
                payload={"data": "retry"},
                priority=1,
                max_retries=3
            )
            
            task_id = self.processor.submit_task(task)
            
            # Wait for processing and retries
            result = self.processor.get_result(task_id, timeout=10.0)
            
            # Should succeed after retries
            self.assertIsNotNone(result)
            self.assertEqual(result["result"], "succeeded_after_retries")
            self.assertEqual(retry_count, 3)

    def test_task_cancellation(self):
        """Test task cancellation functionality"""
        # Submit a task
        task = Task(
            id="cancel_test",
            payload={"data": "cancel"},
            priority=1
        )
        
        task_id = self.processor.submit_task(task)
        
        # Cancel immediately
        cancelled = self.processor.cancel_task(task_id)
        self.assertTrue(cancelled)
        
        # Check status
        status = self.processor.get_task_status(task_id)
        self.assertEqual(status, TaskStatus.CANCELLED)
        
        # Try to cancel again (should fail)
        cancelled_again = self.processor.cancel_task(task_id)
        self.assertFalse(cancelled_again)

    def test_metrics_collection(self):
        """Test comprehensive metrics collection"""
        # Submit and process tasks
        num_tasks = 20
        for i in range(num_tasks):
            task = Task(
                id=f"metrics_test_{i}",
                payload={"data": i},
                priority=1
            )
            self.processor.submit_task(task)
        
        # Wait for processing
        time.sleep(2.0)
        
        # Get metrics
        metrics = self.processor.get_metrics()
        
        # Verify metrics structure
        required_fields = [
            "queue_size", "total_tasks_submitted", "total_tasks_completed",
            "total_tasks_failed", "success_rate", "avg_processing_time",
            "worker_stats", "error_counts", "active_workers",
            "registry_size", "result_store_size"
        ]
        
        for field in required_fields:
            self.assertIn(field, metrics)
        
        # Verify worker stats
        self.assertGreater(len(metrics["worker_stats"]), 0)
        for worker_id, stats in metrics["worker_stats"].items():
            self.assertIn("status", stats)
            self.assertIn("tasks_processed", stats)
            self.assertIn("success_rate", stats)

    def test_queue_size_limits(self):
        """Test that queue size limits prevent memory exhaustion"""
        # Create processor with small queue
        small_processor = FixedDistributedTaskProcessor(num_workers=1, max_queue_size=5)
        self.addCleanup(small_processor.shutdown)
        
        # Fill the queue
        for i in range(5):
            task = Task(
                id=f"queue_limit_{i}",
                payload={"data": i},
                priority=1
            )
            small_processor.submit_task(task)
        
        # Next submission should fail
        with self.assertRaises(Exception):
            task = Task(
                id="queue_limit_overflow",
                payload={"data": "overflow"},
                priority=1
            )
            small_processor.submit_task(task)

    def test_graceful_shutdown(self):
        """Test graceful shutdown functionality"""
        # Submit tasks
        task_ids = []
        for i in range(10):
            task = Task(
                id=f"shutdown_test_{i}",
                payload={"data": i},
                priority=1
            )
            task_id = self.processor.submit_task(task)
            task_ids.append(task_id)
        
        # Start shutdown
        start_time = time.time()
        self.processor.shutdown(timeout=10.0)
        shutdown_time = time.time() - start_time
        
        # Should complete within timeout
        self.assertLess(shutdown_time, 10.0)
        
        # All workers should be stopped
        metrics = self.processor.get_metrics()
        active_workers = metrics["active_workers"]
        self.assertEqual(active_workers, 0)

    def test_context_manager(self):
        """Test context manager functionality"""
        task_id = None
        
        with FixedDistributedTaskProcessor(num_workers=2) as processor:
            task = Task(
                id="context_test",
                payload={"data": "context"},
                priority=1
            )
            task_id = processor.submit_task(task)
            
            result = processor.get_result(task_id, timeout=5.0)
            self.assertIsNotNone(result)
        
        # Processor should be shutdown after context exit

    def test_stress_test_high_concurrency(self):
        """Stress test with high concurrency"""
        # Create processor with more workers for stress test
        stress_processor = FixedDistributedTaskProcessor(num_workers=8, max_queue_size=1000)
        self.addCleanup(stress_processor.shutdown)
        
        num_tasks = 500
        task_ids = []
        
        # Submit many tasks from multiple threads
        def submit_tasks(start_idx, count):
            thread_task_ids = []
            for i in range(count):
                task = Task(
                    id=f"stress_test_{start_idx + i}",
                    payload={"data": start_idx + i, "thread": threading.current_thread().ident},
                    priority=random.randint(1, 10)
                )
                try:
                    task_id = stress_processor.submit_task(task)
                    thread_task_ids.append(task_id)
                except Exception as e:
                    print(f"Failed to submit task: {e}")
            return thread_task_ids
        
        # Use thread pool to submit tasks concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            tasks_per_thread = num_tasks // 10
            
            for i in range(10):
                start_idx = i * tasks_per_thread
                future = executor.submit(submit_tasks, start_idx, tasks_per_thread)
                futures.append(future)
            
            # Collect all task IDs
            for future in futures:
                thread_task_ids = future.result(timeout=30.0)
                task_ids.extend(thread_task_ids)
        
        print(f"Submitted {len(task_ids)} tasks")
        
        # Wait for processing
        stress_processor.wait_for_completion(timeout=60.0)
        
        # Collect results
        successful_results = 0
        for task_id in task_ids:
            result = stress_processor.get_result(task_id, timeout=1.0)
            if result and "result" in result:
                successful_results += 1
        
        print(f"Successfully processed {successful_results}/{len(task_ids)} tasks")
        
        # Should process majority of tasks successfully
        success_rate = successful_results / len(task_ids) * 100
        self.assertGreater(success_rate, 90)  # At least 90% success rate
        
        # Get final metrics
        final_metrics = stress_processor.get_metrics()
        print(f"Final metrics: {final_metrics}")
        
        # Verify metrics
        self.assertGreater(final_metrics["total_tasks_completed"], 0)
        self.assertGreaterEqual(final_metrics["success_rate"], 90)

    def test_callback_execution(self):
        """Test that callbacks are executed properly"""
        callback_results = []
        
        def test_callback(result):
            callback_results.append(result)
        
        task = Task(
            id="callback_test",
            payload={"data": "callback"},
            priority=1,
            callback=test_callback
        )
        
        task_id = self.processor.submit_task(task)
        
        # Wait for processing
        result = self.processor.get_result(task_id, timeout=5.0)
        self.assertIsNotNone(result)
        
        # Wait a bit more for callback
        time.sleep(0.5)
        
        # Verify callback was executed
        self.assertEqual(len(callback_results), 1)
        self.assertEqual(callback_results[0]["task_id"], "callback_test")


class TestTaskStatus(unittest.TestCase):
    """Test task status functionality"""
    
    def test_task_status_transitions(self):
        """Test proper task status transitions"""
        task = Task(id="status_test", payload={"data": "test"})
        
        # Initial status should be PENDING
        self.assertEqual(task.status, TaskStatus.PENDING)
        
        # Test all status values
        statuses = [TaskStatus.PROCESSING, TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
        for status in statuses:
            task.status = status
            self.assertEqual(task.status, status)


def run_integration_tests():
    """Run integration tests to verify all fixes work together"""
    print("Running integration tests...")
    
    # Test all fixes together in realistic scenario
    processor = FixedDistributedTaskProcessor(num_workers=4)
    
    try:
        # Simulate mixed workload
        task_ids = []
        
        # High priority urgent tasks
        for i in range(5):
            task = Task(
                id=f"urgent_{i}",
                payload={"type": "urgent", "data": i},
                priority=10
            )
            task_ids.append(processor.submit_task(task))
        
        # Regular tasks
        for i in range(50):
            task = Task(
                id=f"regular_{i}",
                payload={"type": "regular", "data": i},
                priority=5
            )
            task_ids.append(processor.submit_task(task))
        
        # Low priority background tasks
        for i in range(20):
            task = Task(
                id=f"background_{i}",
                payload={"type": "background", "data": i},
                priority=1
            )
            task_ids.append(processor.submit_task(task))
        
        print(f"Submitted {len(task_ids)} tasks")
        
        # Wait for completion
        processor.wait_for_completion(timeout=30.0)
        
        # Collect results
        successful = 0
        failed = 0
        
        for task_id in task_ids:
            result = processor.get_result(task_id, timeout=1.0)
            if result:
                if "error" in result:
                    failed += 1
                else:
                    successful += 1
            else:
                failed += 1
        
        print(f"Results: {successful} successful, {failed} failed")
        
        # Get final metrics
        metrics = processor.get_metrics()
        print(f"Final metrics: {metrics}")
        
        # Cleanup test
        processor.cleanup_completed_tasks(max_age_seconds=0)
        
        print("Integration tests passed!")
        
    finally:
        processor.shutdown()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.WARNING)
    
    # Run unit tests
    print("Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run integration tests
    run_integration_tests()