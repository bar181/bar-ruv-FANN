"""
Fixed Distributed Task Processor

This module provides a corrected version of the DistributedTaskProcessor
addressing all identified bugs:

1. Race condition in task processing
2. Deadlock between worker threads
3. Memory leak in processing_tasks
4. Incorrect error propagation
5. Lost/corrupted task results

Key fixes:
- Added proper thread synchronization
- Fixed memory management
- Improved error handling with proper propagation
- Added retry mechanism for failed tasks
- Implemented graceful shutdown
"""

import threading
import queue
import time
import random
from typing import Dict, Any, Optional, Callable, Set
from dataclasses import dataclass, field
import weakref
import logging
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import uuid
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class Task:
    """Enhanced task with status tracking"""
    id: str
    payload: Dict[str, Any]
    callback: Optional[Callable] = None
    retry_count: int = 0
    max_retries: int = 3
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class TaskResult:
    """Task result with metadata"""
    task_id: str
    result: Any
    status: TaskStatus
    execution_time: float
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class DistributedTaskProcessor:
    """
    Fixed distributed task processor with proper thread safety,
    memory management, and error handling.
    """
    
    def __init__(self, num_workers: int = 4, max_queue_size: int = 1000):
        self.num_workers = num_workers
        self.max_queue_size = max_queue_size
        
        # Thread-safe queues
        self.task_queue = queue.Queue(maxsize=max_queue_size)
        self.retry_queue = queue.Queue()
        
        # Thread-safe collections
        self.result_store: Dict[str, TaskResult] = {}
        self.processing_tasks: Set[str] = set()
        self.failed_tasks: Dict[str, int] = {}  # Track failure counts
        
        # Synchronization primitives
        self.result_lock = threading.RLock()  # Use RLock to prevent deadlocks
        self.processing_lock = threading.RLock()
        self.failed_lock = threading.Lock()
        
        # Worker management
        self.workers = []
        self.shutdown_event = threading.Event()
        self.worker_executor = ThreadPoolExecutor(max_workers=num_workers)
        
        # Statistics
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'retried_tasks': 0,
            'processing_time': 0.0
        }
        self.stats_lock = threading.Lock()
        
        # Start workers
        self._start_workers()
        
        # Start retry handler
        self.retry_thread = threading.Thread(target=self._retry_handler, daemon=True)
        self.retry_thread.start()
    
    def _start_workers(self):
        """Start worker threads"""
        for i in range(self.num_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                args=(i,),
                daemon=True  # Allow main thread to exit
            )
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"Started {self.num_workers} worker threads")
    
    def _worker_loop(self, worker_id: int):
        """Main worker loop with proper error handling"""
        logger.info(f"Worker {worker_id} started")
        
        while not self.shutdown_event.is_set():
            try:
                # Get task with timeout to allow checking shutdown
                task = self.task_queue.get(timeout=1)
                
                # FIX 1: Proper race condition handling
                with self.processing_lock:
                    if task.id in self.processing_tasks:
                        # Task already being processed, put back in queue
                        self.task_queue.put(task)
                        continue
                    
                    # Mark as processing
                    self.processing_tasks.add(task.id)
                    task.status = TaskStatus.PROCESSING
                    task.started_at = time.time()
                
                logger.debug(f"Worker {worker_id} processing task {task.id}")
                
                try:
                    # Process the task
                    result = self._process_task(task)
                    
                    # FIX 2: Prevent deadlock by using separate locks
                    # and ensuring consistent lock ordering
                    with self.result_lock:
                        task_result = TaskResult(
                            task_id=task.id,
                            result=result,
                            status=TaskStatus.COMPLETED,
                            execution_time=time.time() - task.started_at
                        )
                        self.result_store[task.id] = task_result
                        
                        # Execute callback outside of critical section
                        callback = task.callback
                    
                    # Execute callback outside locks to prevent deadlock
                    if callback:
                        try:
                            callback(result)
                        except Exception as e:
                            logger.error(f"Callback execution failed for task {task.id}: {e}")
                    
                    # Update statistics
                    with self.stats_lock:
                        self.stats['completed_tasks'] += 1
                        self.stats['processing_time'] += time.time() - task.started_at
                    
                    logger.debug(f"Worker {worker_id} completed task {task.id}")
                
                except Exception as e:
                    # FIX 4: Proper error propagation
                    self._handle_task_failure(task, e, worker_id)
                
                finally:
                    # FIX 3: Ensure tasks are removed from processing set
                    with self.processing_lock:
                        self.processing_tasks.discard(task.id)
                    
                    # Mark task as done in queue
                    self.task_queue.task_done()
                
            except queue.Empty:
                # Timeout waiting for task - check shutdown
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} encountered unexpected error: {e}")
        
        logger.info(f"Worker {worker_id} stopped")
    
    def _handle_task_failure(self, task: Task, error: Exception, worker_id: int):
        """Handle task failure with retry logic"""
        error_msg = str(error)
        
        with self.failed_lock:
            self.failed_tasks[task.id] = self.failed_tasks.get(task.id, 0) + 1
        
        # Check if we should retry
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskStatus.RETRYING
            task.error = error_msg
            
            # Add to retry queue with exponential backoff
            self.retry_queue.put((task, time.time() + (2 ** task.retry_count)))
            
            logger.warning(
                f"Worker {worker_id} failed task {task.id} (attempt {task.retry_count}): {error_msg}. "
                f"Scheduling retry."
            )
            
            with self.stats_lock:
                self.stats['retried_tasks'] += 1
        else:
            # Task failed permanently
            task.status = TaskStatus.FAILED
            task.error = error_msg
            task.completed_at = time.time()
            
            with self.result_lock:
                task_result = TaskResult(
                    task_id=task.id,
                    result=None,
                    status=TaskStatus.FAILED,
                    execution_time=time.time() - task.started_at,
                    error=error_msg
                )
                self.result_store[task.id] = task_result
            
            logger.error(
                f"Worker {worker_id} permanently failed task {task.id} "
                f"after {task.max_retries} retries: {error_msg}"
            )
            
            with self.stats_lock:
                self.stats['failed_tasks'] += 1
    
    def _retry_handler(self):
        """Handle task retries with delays"""
        while not self.shutdown_event.is_set():
            try:
                task, retry_time = self.retry_queue.get(timeout=1)
                
                # Wait until retry time
                current_time = time.time()
                if current_time < retry_time:
                    sleep_time = retry_time - current_time
                    time.sleep(min(sleep_time, 1))  # Max 1 second sleep
                    
                    # Put back in retry queue if not ready
                    if not self.shutdown_event.is_set():
                        self.retry_queue.put((task, retry_time))
                    continue
                
                # Re-submit task
                try:
                    self.task_queue.put(task, timeout=1)
                    logger.info(f"Retrying task {task.id} (attempt {task.retry_count})")
                except queue.Full:
                    # Queue is full, try again later
                    self.retry_queue.put((task, time.time() + 5))
                    logger.warning(f"Queue full, delaying retry for task {task.id}")
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Retry handler error: {e}")
    
    def _process_task(self, task: Task) -> Dict[str, Any]:
        """Process a single task (simulation)"""
        # Simulate processing time
        time.sleep(random.uniform(0.1, 0.5))
        
        # Randomly fail some tasks for testing
        if random.random() < 0.1:
            raise Exception(f"Task processing failed for task {task.id}")
        
        return {
            "task_id": task.id,
            "result": "processed",
            "data": task.payload,
            "processed_at": time.time(),
            "worker_info": f"Thread-{threading.current_thread().ident}"
        }
    
    def submit_task(self, task: Task) -> str:
        """
        Submit a task for processing
        
        Args:
            task: Task to process
            
        Returns:
            Task ID
            
        Raises:
            RuntimeError: If processor is shutting down
            queue.Full: If task queue is full
        """
        if self.shutdown_event.is_set():
            raise RuntimeError("Processor is shutting down")
        
        # Check for duplicate task IDs
        with self.processing_lock:
            if task.id in self.processing_tasks:
                raise ValueError(f"Task {task.id} is already being processed")
        
        with self.result_lock:
            if task.id in self.result_store:
                existing_result = self.result_store[task.id]
                if existing_result.status == TaskStatus.COMPLETED:
                    raise ValueError(f"Task {task.id} has already been completed")
        
        # Submit task
        self.task_queue.put(task, timeout=5)  # 5 second timeout
        
        with self.stats_lock:
            self.stats['total_tasks'] += 1
        
        logger.info(f"Submitted task {task.id}")
        return task.id
    
    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """
        Get task result
        
        Args:
            task_id: Task ID to get result for
            
        Returns:
            Task result or None if not found
        """
        # FIX 5: Thread-safe result retrieval
        with self.result_lock:
            return self.result_store.get(task_id)
    
    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Optional[TaskResult]:
        """
        Wait for task completion
        
        Args:
            task_id: Task ID to wait for
            timeout: Maximum time to wait
            
        Returns:
            Task result or None if timeout
        """
        start_time = time.time()
        
        while True:
            result = self.get_result(task_id)
            if result and result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                return result
            
            if timeout and (time.time() - start_time) > timeout:
                return None
            
            time.sleep(0.1)  # Small sleep to prevent busy waiting
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        with self.stats_lock:
            stats = self.stats.copy()
        
        with self.processing_lock:
            stats['currently_processing'] = len(self.processing_tasks)
        
        stats['queue_size'] = self.task_queue.qsize()
        stats['retry_queue_size'] = self.retry_queue.qsize()
        
        # Calculate average processing time
        if stats['completed_tasks'] > 0:
            stats['avg_processing_time'] = stats['processing_time'] / stats['completed_tasks']
        else:
            stats['avg_processing_time'] = 0.0
        
        return stats
    
    def shutdown(self, timeout: Optional[float] = 30):
        """
        Gracefully shutdown the processor
        
        Args:
            timeout: Maximum time to wait for shutdown
        """
        logger.info("Shutting down task processor...")
        
        # Signal shutdown
        self.shutdown_event.set()
        
        # Wait for task queue to be empty
        try:
            # Give some time for current tasks to complete
            time.sleep(1)
            
            # Wait for all tasks to be processed
            start_time = time.time()
            while not self.task_queue.empty():
                if timeout and (time.time() - start_time) > timeout:
                    logger.warning("Timeout waiting for task queue to empty")
                    break
                time.sleep(0.1)
            
            # Wait for workers to finish
            for worker in self.workers:
                if worker.is_alive():
                    worker.join(timeout=5)
            
            # Wait for retry thread
            if self.retry_thread.is_alive():
                self.retry_thread.join(timeout=5)
            
            # Shutdown executor
            self.worker_executor.shutdown(wait=True, timeout=timeout)
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        
        logger.info("Task processor shutdown complete")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.shutdown()
    
    @contextmanager
    def batch_submit(self):
        """Context manager for batch task submission"""
        submitted_tasks = []
        
        class BatchSubmitter:
            def __init__(self, processor):
                self.processor = processor
                self.tasks = []
            
            def add_task(self, task: Task) -> str:
                task_id = self.processor.submit_task(task)
                self.tasks.append(task_id)
                return task_id
            
            def wait_all(self, timeout: Optional[float] = None) -> List[TaskResult]:
                results = []
                for task_id in self.tasks:
                    result = self.processor.wait_for_task(task_id, timeout)
                    if result:
                        results.append(result)
                return results
        
        yield BatchSubmitter(self)


# Usage example and testing
if __name__ == "__main__":
    # Example usage
    with DistributedTaskProcessor(num_workers=4) as processor:
        # Submit some tasks
        tasks = []
        for i in range(10):
            task = Task(
                id=f"task_{i}",
                payload={"data": f"test_data_{i}", "value": i}
            )
            tasks.append(task)
            processor.submit_task(task)
        
        # Wait for all tasks to complete
        results = []
        for task in tasks:
            result = processor.wait_for_task(task.id, timeout=10)
            if result:
                results.append(result)
        
        # Print statistics
        stats = processor.get_stats()
        print(f"Statistics: {stats}")
        print(f"Completed {len(results)} tasks")
        
        # Test batch submission
        with processor.batch_submit() as batch:
            for i in range(5):
                batch.add_task(Task(
                    id=f"batch_task_{i}",
                    payload={"batch_data": i}
                ))
            
            batch_results = batch.wait_all(timeout=10)
            print(f"Batch completed {len(batch_results)} tasks")