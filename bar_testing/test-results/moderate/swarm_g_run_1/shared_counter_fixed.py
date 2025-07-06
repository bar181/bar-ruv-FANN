"""
Fixed SharedCounter implementation with proper thread safety.

This module demonstrates the corrected version of a shared counter
that properly handles concurrent access from multiple threads.
"""

import threading
import time


class SharedCounter:
    """A thread-safe counter that can be incremented by multiple threads."""
    
    def __init__(self):
        """Initialize the counter to 0 with a lock for thread safety."""
        self.count = 0
        self.lock = threading.Lock()
    
    def increment(self, times=1000):
        """
        Increment the counter a specified number of times.
        
        Args:
            times: Number of times to increment (default: 1000)
        """
        for _ in range(times):
            # FIX for Bug 1: Use the lock to ensure atomic operations
            with self.lock:
                # The critical section is now protected
                temp = self.count
                time.sleep(0.00001)  # Simulate some work
                self.count = temp + 1
    
    def get_count(self):
        """
        Get the current count value (thread-safe).
        
        Returns:
            The current counter value
        """
        # FIX for Bug 2: Use lock for thread-safe read
        with self.lock:
            return self.count
    
    def reset(self):
        """
        Reset the counter to 0 (thread-safe).
        
        Added as per requirement 4.
        """
        with self.lock:
            self.count = 0


def worker(counter):
    """Worker function that increments the counter."""
    counter.increment()


def demonstrate_fixed_code():
    """Demonstrate the fixed SharedCounter with proper thread handling."""
    print("=== Fixed SharedCounter Demo ===\n")
    
    # Create counter and threads
    counter = SharedCounter()
    threads = []
    
    print("Starting 5 threads, each incrementing 1000 times...")
    start_time = time.time()
    
    for i in range(5):
        t = threading.Thread(target=worker, args=(counter,))
        threads.append(t)
        t.start()
    
    # FIX for Bug 3 & 4: Properly wait for all threads to complete
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    # Now we can safely get the final count
    final_count = counter.get_count()
    print(f"Final count: {final_count} (expected: 5000)")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    
    # Demonstrate reset
    counter.reset()
    print(f"Count after reset: {counter.get_count()}")


def demonstrate_original_bugs():
    """Show what happens with the original buggy code."""
    print("\n=== Original Buggy Code Demo ===\n")
    
    class BuggyCounter:
        def __init__(self):
            self.count = 0
            self.lock = threading.Lock()  # Not used!
        
        def increment(self, times=1000):
            for _ in range(times):
                # Bug: No lock protection
                temp = self.count
                time.sleep(0.00001)
                self.count = temp + 1
        
        def get_count(self):
            # Bug: No lock protection
            return self.count
    
    counter = BuggyCounter()
    threads = []
    
    for i in range(5):
        t = threading.Thread(target=lambda: counter.increment(), args=())
        threads.append(t)
        t.start()
    
    # Bug: Not waiting for threads
    print(f"Count before threads finish: {counter.get_count()} (race condition!)")
    
    # Now wait for threads
    for t in threads:
        t.join()
    
    print(f"Final count: {counter.get_count()} (likely < 5000 due to race conditions)")


def bug_explanations():
    """Print explanations of each bug and its fix."""
    print("\n=== Bug Explanations ===\n")
    
    explanations = [
        ("Bug 1: Not using the lock in increment()",
         "The increment operation was not atomic. Multiple threads could read the same value, "
         "increment it, and write back, causing lost updates.",
         "Use 'with self.lock:' to protect the critical section."),
        
        ("Bug 2: Not thread-safe read in get_count()",
         "Reading self.count without a lock could return a partially updated value "
         "if another thread is in the middle of incrementing.",
         "Use 'with self.lock:' for thread-safe reads."),
        
        ("Bug 3: Not waiting for threads to complete",
         "Printing the count before threads finish gives incorrect results and "
         "makes debugging difficult.",
         "Use thread.join() to wait for each thread to complete."),
        
        ("Bug 4: No cleanup/join of threads",
         "Threads were left running without proper cleanup, which could cause "
         "resource leaks and unpredictable behavior.",
         "Always join threads after starting them to ensure proper cleanup.")
    ]
    
    for i, (bug, problem, fix) in enumerate(explanations, 1):
        print(f"{i}. {bug}")
        print(f"   Problem: {problem}")
        print(f"   Fix: {fix}")
        print()


if __name__ == "__main__":
    # Run demonstrations
    demonstrate_fixed_code()
    demonstrate_original_bugs()
    bug_explanations()