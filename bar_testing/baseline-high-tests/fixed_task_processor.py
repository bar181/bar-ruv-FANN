import threading
import queue
import time
import random
from typing import Dict, Any, Optional, Callable, Set
from dataclasses import dataclass
import weakref
import logging
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Task:
    id: str
    payload: Dict[str, Any]
    callback: Optional[Callable] = None
    retry_count: int = 0
    max_retries: int = 3


class DistributedTaskProcessor:
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.task_queue = queue.Queue()
        self.result_store = {}
        self.processing_tasks = set()
        self.workers = []
        
        # FIX 1 & 5: Use separate locks to prevent deadlock
        # and ensure thread-safe operations
        self.processing_lock = threading.RLock()  # For processing_tasks
        self.result_lock = threading.RLock()      # For result_store
        
        self.shutdown = False
        
        # FIX 3: Use weakref to prevent memory leaks
        # Store task references that auto-cleanup
        self.task_registry = weakref.WeakValueDictionary()
        
        # Track failed tasks for retry
        self.failed_tasks = {}
        self.failed_tasks_lock = threading.Lock()
        
        self._start_workers()
    
    def _start_workers(self):
        for i in range(self.num_workers):
            worker = threading.Thread(
                target=self._worker_loop, 
                args=(i,),
                name=f"Worker-{i}"
            )
            worker.daemon = True  # Ensure clean shutdown
            worker.start()
            self.workers.append(worker)
    
    def _worker_loop(self, worker_id: int):
        while not self.shutdown:
            try:
                # Get task with timeout to allow shutdown check
                task = self.task_queue.get(timeout=1)
                
                # FIX 1: Atomic check-and-add to prevent race condition
                with self.processing_lock:
                    if task.id in self.processing_tasks:
                        # Task already being processed, put it back
                        logger.warning(f"Worker {worker_id}: Task {task.id} already processing")
                        self.task_queue.put(task)
                        continue
                    # Add to processing set atomically
                    self.processing_tasks.add(task.id)
                
                try:
                    # Process task
                    result = self._process_task(task)
                    
                    # FIX 2: Store result without holding lock during callback
                    with self.result_lock:
                        self.result_store[task.id] = result
                    
                    # FIX 2: Execute callback outside of lock to prevent deadlock
                    if task.callback:
                        try:
                            task.callback(result)
                        except Exception as e:
                            logger.error(f"Worker {worker_id}: Callback error for task {task.id}: {e}")
                    
                    # Successfully processed, remove from failed tasks if present
                    with self.failed_tasks_lock:
                        self.failed_tasks.pop(task.id, None)
                        
                except Exception as e:
                    # FIX 4: Proper error propagation and retry logic
                    logger.error(f"Worker {worker_id}: Task {task.id} failed: {e}")
                    
                    # Handle retry logic
                    task.retry_count += 1
                    if task.retry_count <= task.max_retries:
                        logger.info(f"Worker {worker_id}: Retrying task {task.id} (attempt {task.retry_count})")
                        # Add exponential backoff
                        time.sleep(0.1 * (2 ** (task.retry_count - 1)))
                        self.task_queue.put(task)
                    else:
                        # Max retries exceeded, store error result
                        error_result = {
                            "task_id": task.id,
                            "error": str(e),
                            "status": "failed",
                            "retry_count": task.retry_count
                        }
                        
                        with self.result_lock:
                            self.result_store[task.id] = error_result
                        
                        with self.failed_tasks_lock:
                            self.failed_tasks[task.id] = error_result
                        
                        # Call error callback if provided
                        if task.callback:
                            try:
                                task.callback(error_result)
                            except Exception as cb_error:
                                logger.error(f"Worker {worker_id}: Error callback failed: {cb_error}")
                
                finally:
                    # FIX 3: Always remove from processing set to prevent memory leak
                    with self.processing_lock:
                        self.processing_tasks.discard(task.id)
                    
            except queue.Empty:
                continue
            except Exception as e:
                # Catch any unexpected errors to keep worker alive
                logger.error(f"Worker {worker_id} unexpected error: {e}")
    
    def _process_task(self, task: Task) -> Dict[str, Any]:
        """Process a task - simulates work."""
        # Store task in registry for potential cleanup
        self.task_registry[task.id] = task
        
        # Simulate processing
        time.sleep(random.uniform(0.1, 0.5))
        
        # Randomly fail some tasks
        if random.random() < 0.1:
            raise Exception(f"Task {task.id} processing failed")
        
        return {
            "task_id": task.id, 
            "result": "processed", 
            "data": task.payload,
            "processed_at": time.time()
        }
    
    def submit_task(self, task: Task) -> str:
        """Submit a task for processing."""
        # FIX 1: Check for duplicate task IDs
        with self.processing_lock:
            if task.id in self.processing_tasks:
                raise ValueError(f"Task {task.id} is already being processed")
        
        with self.result_lock:
            if task.id in self.result_store:
                logger.warning(f"Task {task.id} already has a result, overwriting")
        
        self.task_queue.put(task)
        return task.id
    
    def get_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get result for a task (thread-safe)."""
        # FIX 5: Thread-safe result retrieval
        with self.result_lock:
            return self.result_store.get(task_id)
    
    def is_processing(self, task_id: str) -> bool:
        """Check if a task is currently being processed."""
        with self.processing_lock:
            return task_id in self.processing_tasks
    
    def get_failed_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get all failed tasks."""
        with self.failed_tasks_lock:
            return self.failed_tasks.copy()
    
    def clear_results(self):
        """Clear stored results to free memory."""
        with self.result_lock:
            self.result_store.clear()
        
        with self.failed_tasks_lock:
            self.failed_tasks.clear()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current processor status."""
        with self.processing_lock:
            processing_count = len(self.processing_tasks)
        
        with self.result_lock:
            results_count = len(self.result_store)
        
        with self.failed_tasks_lock:
            failed_count = len(self.failed_tasks)
            
        return {
            "workers": self.num_workers,
            "queue_size": self.task_queue.qsize(),
            "processing": processing_count,
            "completed": results_count - failed_count,
            "failed": failed_count,
            "shutdown": self.shutdown
        }
    
    def shutdown_workers(self, timeout: float = 10.0):
        """Gracefully shutdown all workers."""
        logger.info("Initiating shutdown...")
        self.shutdown = True
        
        # Wait for workers to finish current tasks
        start_time = time.time()
        for worker in self.workers:
            remaining_time = timeout - (time.time() - start_time)
            if remaining_time > 0:
                worker.join(timeout=remaining_time)
                if worker.is_alive():
                    logger.warning(f"Worker {worker.name} did not shutdown gracefully")
        
        # Clear any remaining tasks
        while not self.task_queue.empty():
            try:
                self.task_queue.get_nowait()
            except queue.Empty:
                break
        
        logger.info("Shutdown complete")


# Bug Analysis Document
BUG_ANALYSIS = """
# Bug Analysis and Fixes

## Bug 1: Race Condition in Duplicate Task Detection
**Root Cause**: The check for task.id in processing_tasks and the subsequent add operation were not atomic, allowing multiple workers to process the same task.

**Fix**: Used threading.RLock() with atomic check-and-add operation inside the lock.

## Bug 2: Potential Deadlock Between Worker Threads
**Root Cause**: Holding the main lock while executing callbacks could cause deadlock if the callback tried to submit new tasks or access other locked resources.

**Fix**: 
- Separated locks for different resources (processing_lock, result_lock)
- Execute callbacks outside of any locks
- Use RLock to allow recursive locking if needed

## Bug 3: Memory Leak in Task Queue Implementation
**Root Cause**: Tasks were added to processing_tasks but never removed after completion, causing unbounded memory growth.

**Fix**: 
- Always remove task ID from processing_tasks in a finally block
- Added weakref.WeakValueDictionary for automatic cleanup of task objects
- Added clear_results() method for manual memory management

## Bug 4: Incorrect Error Propagation
**Root Cause**: Errors were only logged but not properly handled, causing silent failures and lost results.

**Fix**: 
- Implemented retry logic with exponential backoff
- Store error results in result_store
- Track failed tasks separately
- Execute error callbacks when max retries exceeded

## Bug 5: Thread-Safety Issues in get_result()
**Root Cause**: Direct access to result_store dictionary without synchronization could cause race conditions and corrupted data.

**Fix**: 
- All access to shared data structures now uses appropriate locks
- Implemented thread-safe getter methods
- Used copy() when returning dictionaries to prevent external modification

## Additional Improvements:
1. Added daemon threads for clean shutdown
2. Implemented graceful shutdown with timeout
3. Added comprehensive status monitoring
4. Improved logging for debugging
5. Added methods to check task processing status
6. Implemented proper cleanup mechanisms
"""