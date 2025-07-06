"""
Comprehensive tests for the SharedCounter class to verify all fixes work correctly.
"""

import unittest
import threading
import time
import random
from shared_counter_fixed import SharedCounter


class TestSharedCounter(unittest.TestCase):
    """Test cases for the thread-safe SharedCounter."""
    
    def setUp(self):
        """Create a fresh counter for each test."""
        self.counter = SharedCounter()
    
    def test_single_thread_increment(self):
        """Test basic increment in single-threaded context."""
        self.counter.increment(100)
        self.assertEqual(self.counter.get_count(), 100)
    
    def test_multiple_threads_correct_count(self):
        """Test that multiple threads produce correct total count."""
        num_threads = 10
        increments_per_thread = 1000
        
        def worker():
            self.counter.increment(increments_per_thread)
        
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        expected = num_threads * increments_per_thread
        actual = self.counter.get_count()
        self.assertEqual(actual, expected, 
                        f"Expected {expected}, got {actual}. Race condition detected!")
    
    def test_stress_test_concurrency(self):
        """Stress test with many threads and random delays."""
        num_threads = 20
        
        def worker():
            for _ in range(100):
                self.counter.increment(1)
                # Random small delay to increase chance of race conditions
                time.sleep(random.uniform(0, 0.0001))
        
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        expected = num_threads * 100
        actual = self.counter.get_count()
        self.assertEqual(actual, expected)
    
    def test_reset_functionality(self):
        """Test the reset method works correctly."""
        self.counter.increment(500)
        self.assertEqual(self.counter.get_count(), 500)
        
        self.counter.reset()
        self.assertEqual(self.counter.get_count(), 0)
    
    def test_reset_with_concurrent_access(self):
        """Test reset while other threads are accessing the counter."""
        stop_flag = threading.Event()
        reset_count = [0]
        
        def incrementer():
            while not stop_flag.is_set():
                self.counter.increment(1)
                time.sleep(0.001)
        
        def resetter():
            while not stop_flag.is_set():
                time.sleep(0.01)
                self.counter.reset()
                reset_count[0] += 1
        
        # Start threads
        threads = []
        for _ in range(3):
            t = threading.Thread(target=incrementer)
            threads.append(t)
            t.start()
        
        reset_thread = threading.Thread(target=resetter)
        threads.append(reset_thread)
        reset_thread.start()
        
        # Run for a short time
        time.sleep(0.1)
        stop_flag.set()
        
        # Wait for threads
        for t in threads:
            t.join()
        
        # Counter should be small (recently reset)
        final_count = self.counter.get_count()
        self.assertLess(final_count, 100, 
                       f"Count is {final_count}, suggesting reset isn't working")
        self.assertGreater(reset_count[0], 0, "No resets occurred")
    
    def test_get_count_consistency(self):
        """Test that get_count returns consistent values."""
        # Set initial value
        self.counter.increment(100)
        
        # Read multiple times from different threads
        results = []
        
        def reader():
            for _ in range(10):
                results.append(self.counter.get_count())
        
        threads = []
        for _ in range(5):
            t = threading.Thread(target=reader)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # All reads should return 100
        self.assertTrue(all(r == 100 for r in results), 
                       f"Inconsistent reads: {set(results)}")
    
    def test_thread_join_importance(self):
        """Demonstrate why joining threads is important."""
        results = []
        
        def slow_worker():
            time.sleep(0.1)  # Simulate slow work
            self.counter.increment(1000)
            results.append("done")
        
        t = threading.Thread(target=slow_worker)
        t.start()
        
        # Without join, we might check too early
        count_without_join = self.counter.get_count()
        
        # Now properly wait
        t.join()
        count_with_join = self.counter.get_count()
        
        self.assertEqual(count_without_join, 0, "Count should be 0 without join")
        self.assertEqual(count_with_join, 1000, "Count should be 1000 after join")
        self.assertEqual(len(results), 1, "Thread should have completed")


def run_tests():
    """Run all tests and display results."""
    print("=== Running SharedCounter Tests ===\n")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSharedCounter)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\nTests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_tests()