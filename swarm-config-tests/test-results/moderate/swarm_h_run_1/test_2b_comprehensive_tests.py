#!/usr/bin/env python3
"""
Comprehensive test suite for SharedCounter fixes
QA Division - Test 2b: Debugging (Moderate)
"""

import unittest
import threading
import time
from test_2b_shared_counter_fixed import SharedCounter


class TestSharedCounterFixes(unittest.TestCase):
    """Test suite verifying all bug fixes"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.counter = SharedCounter()
    
    def test_basic_functionality(self):
        """Test basic counter operations"""
        self.assertEqual(self.counter.get_count(), 0)
        
        self.counter.increment(1)
        self.assertEqual(self.counter.get_count(), 1)
        
        self.counter.add(5)
        self.assertEqual(self.counter.get_count(), 6)
        
        self.counter.subtract(2)
        self.assertEqual(self.counter.get_count(), 4)
        
        self.counter.reset()
        self.assertEqual(self.counter.get_count(), 0)
    
    def test_original_bug_scenario(self):
        """Test the exact scenario from the original buggy code"""
        counter = SharedCounter()
        threads = []
        
        def worker(counter):
            counter.increment(1000)  # Same as original
        
        # Create 5 threads as in original
        for i in range(5):
            t = threading.Thread(target=worker, args=(counter,))
            threads.append(t)
            t.start()
        
        # FIXED: Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Should always be 5000 now
        final_count = counter.get_count()
        self.assertEqual(final_count, 5000, 
                        f"Expected 5000, got {final_count}. Bug fix failed!")
    
    def test_concurrent_read_write(self):
        """Test concurrent read/write operations"""
        counter = SharedCounter()
        results = []
        
        def writer():
            """Writer thread"""
            for i in range(100):
                counter.increment(1)
                time.sleep(0.001)  # Small delay
        
        def reader():
            """Reader thread"""
            for _ in range(50):
                count = counter.get_count()
                results.append(count)
                time.sleep(0.002)  # Small delay
        
        # Start writer and reader threads
        writer_thread = threading.Thread(target=writer)
        reader_thread = threading.Thread(target=reader)
        
        writer_thread.start()
        reader_thread.start()
        
        writer_thread.join()
        reader_thread.join()
        
        # All reads should be consistent (no partial updates)
        self.assertEqual(counter.get_count(), 100)
        
        # Results should be monotonically increasing
        for i in range(1, len(results)):
            self.assertGreaterEqual(results[i], results[i-1], 
                                   "Read values should be monotonically increasing")
    
    def test_stress_multiple_threads(self):
        """Stress test with many threads"""
        counter = SharedCounter()
        num_threads = 20
        increments_per_thread = 100
        
        def stress_worker():
            counter.increment(increments_per_thread)
        
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=stress_worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        expected = num_threads * increments_per_thread
        actual = counter.get_count()
        self.assertEqual(actual, expected, 
                        f"Expected {expected}, got {actual}. Race condition detected!")
    
    def test_thread_safety_with_mixed_operations(self):
        """Test thread safety with mixed operations"""
        counter = SharedCounter()
        
        def incrementer():
            for _ in range(100):
                counter.increment(1)
        
        def adder():
            for _ in range(50):
                counter.add(2)
        
        def subtracter():
            for _ in range(25):
                counter.subtract(1)
        
        # Start all operations concurrently
        threads = [
            threading.Thread(target=incrementer),
            threading.Thread(target=incrementer),
            threading.Thread(target=adder),
            threading.Thread(target=subtracter)
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Calculate expected result
        expected = (100 * 2) + (50 * 2) - (25 * 1)  # 200 + 100 - 25 = 275
        actual = counter.get_count()
        self.assertEqual(actual, expected, 
                        f"Expected {expected}, got {actual}. Mixed operations failed!")
    
    def test_reset_during_concurrent_operations(self):
        """Test reset during concurrent operations"""
        counter = SharedCounter()
        
        def background_incrementer():
            for _ in range(1000):
                counter.increment(1)
                time.sleep(0.0001)
        
        # Start background incrementer
        bg_thread = threading.Thread(target=background_incrementer)
        bg_thread.start()
        
        # Wait a bit then reset
        time.sleep(0.1)
        counter.reset()
        
        # Let it finish
        bg_thread.join()
        
        # Count should be whatever happened after reset
        final_count = counter.get_count()
        self.assertGreaterEqual(final_count, 0)
        self.assertLess(final_count, 1000)  # Should be less than full amount
    
    def test_no_race_condition_on_reads(self):
        """Verify that reads don't interfere with each other"""
        counter = SharedCounter()
        counter.add(100)
        
        read_results = []
        
        def concurrent_reader(thread_id):
            for _ in range(10):
                count = counter.get_count()
                read_results.append((thread_id, count))
                time.sleep(0.001)
        
        # Start multiple reader threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=concurrent_reader, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All reads should return the same value (100)
        for thread_id, count in read_results:
            self.assertEqual(count, 100, 
                            f"Thread {thread_id} read {count}, expected 100")
    
    def test_performance_regression(self):
        """Test that fixes don't cause severe performance regression"""
        counter = SharedCounter()
        
        start_time = time.time()
        
        def performance_worker():
            counter.increment(1000)
        
        # Run with 10 threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=performance_worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete in reasonable time (< 5 seconds)
        self.assertLess(duration, 5.0, 
                       f"Performance regression detected: {duration:.2f}s")
        
        # Verify correctness
        self.assertEqual(counter.get_count(), 10000)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)