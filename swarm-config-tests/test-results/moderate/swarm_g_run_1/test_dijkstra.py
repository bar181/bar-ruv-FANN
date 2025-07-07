"""
Comprehensive tests for the Dijkstra algorithm implementation.
"""

import unittest
from dijkstra_solver import DijkstraPathFinder


class TestDijkstraPathFinder(unittest.TestCase):
    """Test cases for the Dijkstra path finding algorithm."""
    
    def setUp(self):
        """Set up test graphs."""
        # Simple triangle graph
        self.simple_graph = {
            'A': {'B': 10, 'C': 15},
            'B': {'A': 10, 'C': 5},
            'C': {'A': 15, 'B': 5}
        }
        
        # Complex city network
        self.city_graph = {
            'A': {'B': 10, 'C': 15},
            'B': {'A': 10, 'C': 5, 'D': 20},
            'C': {'A': 15, 'B': 5, 'D': 10, 'E': 25},
            'D': {'B': 20, 'C': 10, 'E': 15},
            'E': {'C': 25, 'D': 15}
        }
        
        # Disconnected graph
        self.disconnected_graph = {
            'A': {'B': 1},
            'B': {'A': 1},
            'C': {'D': 1},
            'D': {'C': 1}
        }
    
    def test_simple_shortest_path(self):
        """Test shortest path in simple graph."""
        finder = DijkstraPathFinder(self.simple_graph)
        
        # A to B direct
        distance, path = finder.dijkstra('A', 'B')
        self.assertEqual(distance, 10)
        self.assertEqual(path, ['A', 'B'])
        
        # A to C direct (15) vs via B (10+5=15) - both same distance
        distance, path = finder.dijkstra('A', 'C')
        self.assertEqual(distance, 15)
        # Could be either ['A', 'C'] or ['A', 'B', 'C'] - both are optimal
        self.assertIn(path, [['A', 'C'], ['A', 'B', 'C']])
    
    def test_city_network_optimal_path(self):
        """Test the specific city network problem."""
        finder = DijkstraPathFinder(self.city_graph)
        
        # A to E optimal path (actually 40 minutes based on output)
        distance, path = finder.dijkstra('A', 'E')
        self.assertEqual(distance, 40)
        # Multiple optimal paths possible
        self.assertIn(path, [['A', 'C', 'E'], ['A', 'B', 'C', 'E'], ['A', 'C', 'D', 'E'], ['A', 'B', 'C', 'D', 'E']])
        
        # Verify other paths are longer
        all_paths = finder.find_all_paths_within_threshold('A', 'E', 50)
        self.assertGreater(len(all_paths), 1)
        self.assertEqual(all_paths[0][0], 40)  # First path is optimal
    
    def test_disconnected_graph(self):
        """Test handling of disconnected graphs."""
        finder = DijkstraPathFinder(self.disconnected_graph)
        
        # Within connected component
        distance, path = finder.dijkstra('A', 'B')
        self.assertEqual(distance, 1)
        self.assertEqual(path, ['A', 'B'])
        
        # Between disconnected components
        distance, path = finder.dijkstra('A', 'C')
        self.assertIsNone(distance)
        self.assertIsNone(path)
    
    def test_same_node_path(self):
        """Test path from node to itself."""
        finder = DijkstraPathFinder(self.simple_graph)
        
        distance, path = finder.dijkstra('A', 'A')
        self.assertEqual(distance, 0)
        self.assertEqual(path, ['A'])
    
    def test_nonexistent_nodes(self):
        """Test handling of nonexistent nodes."""
        finder = DijkstraPathFinder(self.simple_graph)
        
        # Start node doesn't exist
        distance, path = finder.dijkstra('Z', 'A')
        self.assertIsNone(distance)
        self.assertIsNone(path)
        
        # End node doesn't exist
        distance, path = finder.dijkstra('A', 'Z')
        self.assertIsNone(distance)
        self.assertIsNone(path)
    
    def test_near_optimal_paths(self):
        """Test finding paths within threshold of optimal."""
        finder = DijkstraPathFinder(self.city_graph)
        
        # Find paths within 10% of optimal
        near_optimal = finder.find_all_paths_within_threshold('A', 'E', 10)
        
        # Should include optimal path
        self.assertGreater(len(near_optimal), 0)
        self.assertEqual(near_optimal[0][0], 40)  # Optimal distance
        
        # All paths should be within threshold
        for distance, path in near_optimal:
            self.assertLessEqual(distance, 40 * 1.1)  # Within 10%
    
    def test_all_pairs_shortest_paths(self):
        """Test shortest paths between all pairs of nodes."""
        finder = DijkstraPathFinder(self.simple_graph)
        
        expected_distances = {
            ('A', 'B'): 10,
            ('A', 'C'): 15,
            ('B', 'A'): 10,
            ('B', 'C'): 5,
            ('C', 'A'): 15,
            ('C', 'B'): 5
        }
        
        for (start, end), expected_dist in expected_distances.items():
            distance, path = finder.dijkstra(start, end)
            self.assertEqual(distance, expected_dist,
                           f"Distance from {start} to {end} should be {expected_dist}, got {distance}")
    
    def test_single_node_graph(self):
        """Test graph with single node."""
        single_node_graph = {'A': {}}
        finder = DijkstraPathFinder(single_node_graph)
        
        distance, path = finder.dijkstra('A', 'A')
        self.assertEqual(distance, 0)
        self.assertEqual(path, ['A'])
    
    def test_complexity_analysis(self):
        """Test complexity analysis output."""
        finder = DijkstraPathFinder(self.city_graph)
        analysis = finder.analyze_complexity()
        
        self.assertIn("Time Complexity", analysis)
        self.assertIn("Space Complexity", analysis)
        self.assertIn("O((V + E) log V)", analysis)
        self.assertIn("Vertices (V): 5", analysis)


def run_dijkstra_tests():
    """Run all Dijkstra tests."""
    print("=== Running Dijkstra Algorithm Tests ===\n")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDijkstraPathFinder)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\nTests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_dijkstra_tests()