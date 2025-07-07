"""
Fixed SharedCounter implementation - Race condition debugging test
Team 1 - 8-agent dual team swarm configuration
"""

import threading
import time


class SharedCounter:
    """Thread-safe shared counter implementation."""
    
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()
    
    def increment(self, times=1000):
        """
        Increment the counter 'times' times in a thread-safe manner.
        
        Fix for Bug 1: Using the lock to ensure atomic read-modify-write
        """
        for _ in range(times):
            with self.lock:  # Fix: Use lock to make increment atomic
                temp = self.count
                time.sleep(0.00001)  # Simulate some work
                self.count = temp + 1
    
    def get_count(self):
        """
        Thread-safe read of the counter value.
        
        Fix for Bug 2: Using lock for thread-safe read
        """
        with self.lock:  # Fix: Thread-safe read
            return self.count
    
    def reset(self):
        """
        Reset the counter to zero in a thread-safe manner.
        
        New method as requested in requirements
        """
        with self.lock:
            self.count = 0


def worker(counter):
    """Worker function for threads."""
    counter.increment()


def test_original_buggy_code():
    """Demonstrate the bugs in the original code."""
    print("=== Testing Original Buggy Code ===")
    
    class BuggySharedCounter:
        def __init__(self):
            self.count = 0
            self.lock = threading.Lock()
        
        def increment(self, times=1000):
            for _ in range(times):
                # Bug 1: Not using the lock
                temp = self.count
                time.sleep(0.00001)
                self.count = temp + 1
        
        def get_count(self):
            # Bug 2: Not thread-safe read
            return self.count
    
    counter = BuggySharedCounter()
    threads = []
    
    for i in range(5):
        t = threading.Thread(target=lambda: counter.increment(), args=())
        threads.append(t)
        t.start()
    
    # Bug 3: Not waiting for threads to complete
    print(f"Final count (before join): {counter.get_count()}")
    
    # Wait for threads
    for t in threads:
        t.join()
    
    print(f"Final count (after join): {counter.get_count()}")
    print(f"Expected: 5000, Actual: {counter.get_count()}")
    print(f"Lost updates: {5000 - counter.get_count()}\n")


def test_fixed_code():
    """Test the fixed implementation."""
    print("=== Testing Fixed Code ===")
    
    counter = SharedCounter()
    threads = []
    
    # Start time
    start_time = time.time()
    
    for i in range(5):
        t = threading.Thread(target=worker, args=(counter,))
        threads.append(t)
        t.start()
    
    # Fix for Bug 3: Properly wait for all threads to complete
    for t in threads:
        t.join()
    
    # Fix for Bug 4: Threads are properly joined above
    
    end_time = time.time()
    
    final_count = counter.get_count()
    print(f"Final count: {final_count}")
    print(f"Expected: 5000, Actual: {final_count}")
    print(f"Correct: {final_count == 5000}")
    print(f"Time taken: {end_time - start_time:.3f} seconds\n")
    
    return final_count == 5000


def test_reset_functionality():
    """Test the reset method."""
    print("=== Testing Reset Functionality ===")
    
    counter = SharedCounter()
    
    # Add some counts
    counter.increment(100)
    print(f"Count after increment: {counter.get_count()}")
    
    # Reset
    counter.reset()
    print(f"Count after reset: {counter.get_count()}")
    
    # Test reset with concurrent operations
    threads = []
    
    # Start some increment threads
    for i in range(3):
        t = threading.Thread(target=lambda: counter.increment(100), args=())
        threads.append(t)
        t.start()
    
    # Reset in the middle
    time.sleep(0.001)
    counter.reset()
    
    # Wait for threads
    for t in threads:
        t.join()
    
    print(f"Count after concurrent reset: {counter.get_count()}")
    print("(May vary due to timing of reset vs increments)\n")


def stress_test():
    """Stress test with more threads and iterations."""
    print("=== Stress Test ===")
    
    counter = SharedCounter()
    threads = []
    num_threads = 10
    increments_per_thread = 1000
    
    start_time = time.time()
    
    for i in range(num_threads):
        t = threading.Thread(target=lambda: counter.increment(increments_per_thread), args=())
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    final_count = counter.get_count()
    expected = num_threads * increments_per_thread
    
    print(f"Threads: {num_threads}, Increments per thread: {increments_per_thread}")
    print(f"Expected: {expected}, Actual: {final_count}")
    print(f"Correct: {final_count == expected}")
    print(f"Time taken: {end_time - start_time:.3f} seconds\n")
    
    return final_count == expected


# Bug explanations
bug_explanations = """
=== Bug Explanations ===

Bug 1: Race Condition in increment()
- The original code reads count, sleeps, then writes back
- Multiple threads can read the same value before any writes
- Result: Lost updates as threads overwrite each other's changes
- Fix: Use lock to make read-modify-write atomic

Bug 2: Non-thread-safe read in get_count()
- Reading without a lock can return inconsistent values
- Could read partially updated multi-byte values on some systems
- Fix: Use lock for consistent reads

Bug 3: Not waiting for thread completion
- Original code prints result before threads finish
- Shows incomplete/incorrect count
- Fix: Use join() to wait for all threads

Bug 4: No thread cleanup
- Threads weren't properly joined
- Resources not cleaned up
- Fix: Always join threads after starting them

Additional Enhancement:
- Added reset() method with proper locking
- Ensures thread-safe reset operation
"""


if __name__ == "__main__":
    # Run all tests
    test_original_buggy_code()
    
    fixed_correct = test_fixed_code()
    
    test_reset_functionality()
    
    stress_correct = stress_test()
    
    print(bug_explanations)
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Basic fix test: {'PASSED' if fixed_correct else 'FAILED'}")
    print(f"Stress test: {'PASSED' if stress_correct else 'FAILED'}")
    print("\nAll race conditions have been fixed!")
    print("The implementation is now thread-safe.")