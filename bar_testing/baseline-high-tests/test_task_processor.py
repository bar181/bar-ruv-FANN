import pytest
import threading
import time
import random
from fixed_task_processor import DistributedTaskProcessor, Task
import concurrent.futures


class TestDistributedTaskProcessor:
    
    def test_basic_task_processing(self):
        """Test basic task submission and processing."""
        processor = DistributedTaskProcessor(num_workers=2)
        
        try:
            # Submit a simple task
            task = Task(id="test1", payload={"data": "test"})
            task_id = processor.submit_task(task)
            
            # Wait for processing
            time.sleep(1)
            
            # Check result
            result = processor.get_result(task_id)
            assert result is not None
            assert result["task_id"] == "test1"
            assert result["result"] == "processed"
            assert result["data"] == {"data": "test"}
            
        finally:
            processor.shutdown_workers()
    
    def test_duplicate_task_prevention(self):
        """Test that duplicate task IDs are properly handled."""
        processor = DistributedTaskProcessor(num_workers=2)
        
        try:
            # Submit first task
            task1 = Task(id="duplicate", payload={"version": 1})
            processor.submit_task(task1)
            
            # Try to submit duplicate while first is processing
            task2 = Task(id="duplicate", payload={"version": 2})
            
            # Should either raise error or handle gracefully
            # depending on timing
            try:
                processor.submit_task(task2)
                # If no error, wait and check that only one was processed
                time.sleep(1)
                result = processor.get_result("duplicate")
                assert result["data"]["version"] in [1, 2]
            except ValueError as e:
                assert "already being processed" in str(e)
                
        finally:
            processor.shutdown_workers()
    
    def test_concurrent_processing(self):
        """Test that multiple tasks are processed concurrently."""
        processor = DistributedTaskProcessor(num_workers=4)
        
        try:
            # Submit multiple tasks
            tasks = []
            for i in range(10):
                task = Task(id=f"concurrent_{i}", payload={"index": i})
                tasks.append(task)
                processor.submit_task(task)
            
            # Wait for all to complete
            time.sleep(3)
            
            # Check all results
            for i in range(10):
                result = processor.get_result(f"concurrent_{i}")
                assert result is not None
                assert result["data"]["index"] == i
                
        finally:
            processor.shutdown_workers()
    
    def test_error_handling_and_retry(self):
        """Test that errors are properly handled with retry logic."""
        processor = DistributedTaskProcessor(num_workers=2)
        
        # Monkey patch to force failures
        original_process = processor._process_task
        failure_count = {}
        
        def failing_process(task):
            count = failure_count.get(task.id, 0)
            failure_count[task.id] = count + 1
            
            # Fail first 2 attempts, succeed on 3rd
            if count < 2:
                raise Exception(f"Simulated failure {count + 1}")
            
            return original_process(task)
        
        processor._process_task = failing_process
        
        try:
            task = Task(id="retry_test", payload={"data": "test"})
            processor.submit_task(task)
            
            # Wait for retries
            time.sleep(2)
            
            result = processor.get_result("retry_test")
            assert result is not None
            assert result["result"] == "processed"
            
            # Check that it was retried
            assert failure_count["retry_test"] == 3  # 2 failures + 1 success
            
        finally:
            processor.shutdown_workers()
    
    def test_max_retries_exceeded(self):
        """Test that tasks fail after max retries."""
        processor = DistributedTaskProcessor(num_workers=1)
        
        # Force all attempts to fail
        def always_fail(task):
            raise Exception("Always fails")
        
        processor._process_task = always_fail
        
        try:
            task = Task(id="fail_test", payload={"data": "test"}, max_retries=2)
            processor.submit_task(task)
            
            # Wait for retries
            time.sleep(2)
            
            result = processor.get_result("fail_test")
            assert result is not None
            assert result["status"] == "failed"
            assert result["retry_count"] == 3  # initial + 2 retries
            
            # Check failed tasks tracking
            failed = processor.get_failed_tasks()
            assert "fail_test" in failed
            
        finally:
            processor.shutdown_workers()
    
    def test_callback_execution(self):
        """Test that callbacks are properly executed."""
        processor = DistributedTaskProcessor(num_workers=2)
        
        callback_results = []
        callback_lock = threading.Lock()
        
        def callback(result):
            with callback_lock:
                callback_results.append(result)
        
        try:
            # Submit tasks with callbacks
            for i in range(5):
                task = Task(
                    id=f"callback_{i}", 
                    payload={"index": i},
                    callback=callback
                )
                processor.submit_task(task)
            
            # Wait for processing
            time.sleep(2)
            
            # Check callbacks were executed
            with callback_lock:
                assert len(callback_results) == 5
                assert all(r["result"] == "processed" for r in callback_results)
                
        finally:
            processor.shutdown_workers()
    
    def test_no_deadlock_scenario(self):
        """Test that the fixed implementation doesn't deadlock."""
        processor = DistributedTaskProcessor(num_workers=4)
        
        # Create a callback that tries to access processor
        def recursive_callback(result):
            # Try to submit new task from callback
            if result["data"].get("level", 0) < 2:
                new_task = Task(
                    id=f"{result['task_id']}_child",
                    payload={"level": result["data"].get("level", 0) + 1}
                )
                try:
                    processor.submit_task(new_task)
                except:
                    pass
        
        try:
            # Submit initial tasks
            for i in range(5):
                task = Task(
                    id=f"deadlock_test_{i}",
                    payload={"level": 0},
                    callback=recursive_callback
                )
                processor.submit_task(task)
            
            # Wait with timeout - should not hang
            time.sleep(3)
            
            # Verify processor is still responsive
            status = processor.get_status()
            assert status["shutdown"] is False
            
        finally:
            processor.shutdown_workers(timeout=2)
    
    def test_memory_leak_prevention(self):
        """Test that memory is properly managed."""
        processor = DistributedTaskProcessor(num_workers=2)
        
        try:
            # Submit many tasks
            for i in range(100):
                task = Task(id=f"memory_{i}", payload={"data": "x" * 1000})
                processor.submit_task(task)
            
            # Wait for processing
            time.sleep(5)
            
            # Check that processing_tasks is empty
            status = processor.get_status()
            assert status["processing"] == 0
            
            # Clear results to free memory
            processor.clear_results()
            
            # Verify clearing worked
            assert processor.get_result("memory_0") is None
            
        finally:
            processor.shutdown_workers()
    
    def test_graceful_shutdown(self):
        """Test graceful shutdown of workers."""
        processor = DistributedTaskProcessor(num_workers=3)
        
        try:
            # Submit tasks that take time
            for i in range(10):
                task = Task(id=f"shutdown_{i}", payload={"data": i})
                processor.submit_task(task)
            
            # Start shutdown
            start_time = time.time()
            processor.shutdown_workers(timeout=5)
            shutdown_time = time.time() - start_time
            
            # Should complete within timeout
            assert shutdown_time < 6
            
            # Verify shutdown
            status = processor.get_status()
            assert status["shutdown"] is True
            
        except:
            # Force cleanup if test fails
            processor.shutdown = True
            raise
    
    def test_thread_safety_stress_test(self):
        """Stress test for thread safety with many concurrent operations."""
        processor = DistributedTaskProcessor(num_workers=8)
        
        try:
            # Use ThreadPoolExecutor for concurrent operations
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                
                # Submit tasks concurrently
                for i in range(100):
                    future = executor.submit(
                        processor.submit_task,
                        Task(id=f"stress_{i}", payload={"index": i})
                    )
                    futures.append(future)
                
                # Check results concurrently
                def check_result(task_id):
                    for _ in range(10):
                        result = processor.get_result(task_id)
                        if result:
                            return result
                        time.sleep(0.1)
                    return None
                
                # Wait a bit for processing to start
                time.sleep(1)
                
                # Check results concurrently
                result_futures = []
                for i in range(100):
                    future = executor.submit(check_result, f"stress_{i}")
                    result_futures.append(future)
                
                # Get status concurrently
                status_futures = []
                for _ in range(20):
                    future = executor.submit(processor.get_status)
                    status_futures.append(future)
                
                # Wait for all operations
                concurrent.futures.wait(futures + result_futures + status_futures)
                
            # Verify no crashes and data integrity
            final_status = processor.get_status()
            assert final_status["completed"] + final_status["failed"] <= 100
            
        finally:
            processor.shutdown_workers()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])