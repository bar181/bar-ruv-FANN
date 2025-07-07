#!/usr/bin/env python3
"""
Fixed SharedCounter - Race Condition Resolution
QA Division - Test 2b: Debugging (Moderate)
Debugged by: QA Manager, Performance Engineer, Security Architect, Data Scientist, Quality Optimizer
"""

import threading
import time
from typing import List


class SharedCounter:
    """
    Thread-safe shared counter implementation.
    
    Fixes applied:
    1. Proper lock usage in increment method
    2. Thread-safe read operations
    3. Atomic operations with context manager
    4. Added reset functionality
    """
    
    def __init__(self):
        """Initialize counter with thread lock"""
        self.count = 0
        self.lock = threading.Lock()
    
    def increment(self, times: int = 1000) -> None:
        """
        Increment counter by specified amount in thread-safe manner.
        
        Args:
            times: Number of times to increment
        
        FIXES APPLIED:
        - Bug 1 FIXED: Now using lock properly for atomic increment
        - Removed artificial delay that exacerbated race condition
        - Single atomic operation per increment
        """
        for _ in range(times):
            with self.lock:
                # FIXED: Atomic increment operation
                self.count += 1
    
    def get_count(self) -> int:
        """
        Get current count value in thread-safe manner.
        
        Returns:
            Current count value
        
        FIXES APPLIED:
        - Bug 2 FIXED: Now thread-safe read operation
        """
        with self.lock:
            return self.count
    
    def reset(self) -> None:
        """
        Reset counter to zero in thread-safe manner.
        
        NEW FEATURE: Added as requested
        """
        with self.lock:
            self.count = 0
    
    def add(self, value: int) -> None:
        """
        Add specified value to counter atomically.
        
        Args:
            value: Value to add to counter
        """
        with self.lock:
            self.count += value
    
    def subtract(self, value: int) -> None:
        """
        Subtract specified value from counter atomically.
        
        Args:
            value: Value to subtract from counter
        """
        with self.lock:
            self.count -= value


def worker(counter: SharedCounter, thread_id: int) -> None:
    """
    Worker function that increments counter.
    
    Args:
        counter: SharedCounter instance
        thread_id: Thread identifier for logging
    """
    print(f"Thread {thread_id} starting...")
    counter.increment()
    print(f"Thread {thread_id} completed increment")


def demonstrate_fixed_implementation():
    """Demonstrate the fixed implementation works correctly"""
    print("=== Fixed SharedCounter Demonstration ===")
    
    # Create counter instance
    counter = SharedCounter()
    threads: List[threading.Thread] = []
    
    print(f"Initial count: {counter.get_count()}")
    
    # Create and start 5 threads
    for i in range(5):
        thread = threading.Thread(target=worker, args=(counter, i))
        threads.append(thread)
        thread.start()
    
    # FIXED: Bug 3 - Properly wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # FIXED: Bug 4 - All threads are now properly joined
    
    final_count = counter.get_count()
    print(f"Final count: {final_count}")
    print(f"Expected: 5000, Got: {final_count}")
    print(f"Success: {final_count == 5000}")
    
    return final_count == 5000


def stress_test_fixed_implementation():
    """Stress test the fixed implementation with more threads"""
    print("\n=== Stress Test: 10 Threads x 500 Increments ===")
    
    counter = SharedCounter()
    threads: List[threading.Thread] = []
    
    def stress_worker(counter: SharedCounter, increments: int):
        """Worker for stress test"""
        counter.increment(increments)
    
    # Create 10 threads, each doing 500 increments
    num_threads = 10
    increments_per_thread = 500
    
    for i in range(num_threads):
        thread = threading.Thread(target=stress_worker, args=(counter, increments_per_thread))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads
    for thread in threads:
        thread.join()
    
    expected = num_threads * increments_per_thread
    actual = counter.get_count()
    
    print(f"Expected: {expected}, Got: {actual}")
    print(f"Stress test success: {actual == expected}")
    
    return actual == expected


if __name__ == "__main__":
    # Demonstrate fixes
    basic_success = demonstrate_fixed_implementation()
    stress_success = stress_test_fixed_implementation()
    
    print(f"\n=== Summary ===")
    print(f"Basic test: {'PASS' if basic_success else 'FAIL'}")
    print(f"Stress test: {'PASS' if stress_success else 'FAIL'}")
    print(f"All bugs fixed: {basic_success and stress_success}")