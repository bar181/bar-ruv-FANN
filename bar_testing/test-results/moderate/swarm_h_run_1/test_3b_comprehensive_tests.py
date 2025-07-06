#!/usr/bin/env python3
"""
Comprehensive test suite for Dijkstra's algorithm implementation
QA Division - Test 3b: Mathematical Problem (Moderate)
"""

import unittest
from test_3b_dijkstra_solver import DijkstraPathFinder


class TestDijkstraPathFinder(unittest.TestCase):
    """Test suite for DijkstraPathFinder class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Test graph from the problem
        self.test_graph = {
            'A': {'B': 10, 'C': 15},
            'B': {'A': 10, 'C': 5, 'D': 20},
            'C': {'A': 15, 'B': 5, 'D': 10, 'E': 25},
            'D': {'B': 20, 'C': 10, 'E': 15},
            'E': {'C': 25, 'D': 15}
        }
        self.pathfinder = DijkstraPathFinder(self.test_graph)
    
    def test_specific_problem_solution(self):
        """Test the specific A to E problem from the prompt"""
        distance, path = self.pathfinder.dijkstra('A', 'E')
        
        # Should find one of the optimal paths with distance 40
        self.assertEqual(distance, 40)
        self.assertTrue(path[0] == 'A' and path[-1] == 'E')
        
        # Verify path is valid
        self.assertTrue(self._is_valid_path(path))
        
        # Verify distance calculation
        calculated_distance = self._calculate_path_distance(path)
        self.assertEqual(calculated_distance, distance)
    
    def test_all_optimal_paths(self):
        """Test that algorithm finds optimal paths between all pairs"""
        expected_distances = {
            ('A', 'B'): 10,
            ('A', 'C'): 15,
            ('A', 'D'): 25,  # A->C->D = 15+10 = 25
            ('A', 'E'): 40,  # Multiple paths with distance 40
            ('B', 'C'): 5,
            ('B', 'D'): 15,  # B->C->D = 5+10 = 15
            ('B', 'E'): 30,  # B->C->D->E = 5+10+15 = 30
            ('C', 'D'): 10,
            ('C', 'E'): 25,
            ('D', 'E'): 15
        }
        
        for (start, end), expected_dist in expected_distances.items():
            with self.subTest(start=start, end=end):
                distance, path = self.pathfinder.dijkstra(start, end)
                self.assertEqual(distance, expected_dist, 
                               f"Path {start}->{end}: expected {expected_dist}, got {distance}")
                self.assertTrue(self._is_valid_path(path))
    
    def test_disconnected_graph(self):
        """Test handling of disconnected graphs"""
        disconnected_graph = {
            'A': {'B': 10},
            'B': {'A': 10},
            'C': {'D': 5},
            'D': {'C': 5}
        }
        
        pathfinder = DijkstraPathFinder(disconnected_graph)
        
        # Should find path within connected component
        distance, path = pathfinder.dijkstra('A', 'B')
        self.assertEqual(distance, 10)
        self.assertEqual(path, ['A', 'B'])
        
        # Should not find path between disconnected components
        distance, path = pathfinder.dijkstra('A', 'C')
        self.assertEqual(distance, float('inf'))
        self.assertEqual(path, [])
    
    def test_single_node_graph(self):
        """Test graph with single node"""
        single_node_graph = {'A': {}}
        pathfinder = DijkstraPathFinder(single_node_graph)
        
        distance, path = pathfinder.dijkstra('A', 'A')
        self.assertEqual(distance, 0)
        self.assertEqual(path, ['A'])
    
    def test_self_loops(self):
        """Test handling of self-loops"""
        graph_with_loops = {
            'A': {'A': 5, 'B': 10},
            'B': {'A': 10}
        }
        
        pathfinder = DijkstraPathFinder(graph_with_loops)
        
        # Path to self should be 0, not using self-loop
        distance, path = pathfinder.dijkstra('A', 'A')
        self.assertEqual(distance, 0)
        self.assertEqual(path, ['A'])
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Empty graph
        with self.assertRaises(ValueError):
            DijkstraPathFinder({})
        
        # Invalid graph structure
        with self.assertRaises(ValueError):
            DijkstraPathFinder({'A': 'invalid'})
        
        # Negative weights
        with self.assertRaises(ValueError):
            DijkstraPathFinder({'A': {'B': -5}})
        
        # Invalid start/end nodes
        with self.assertRaises(ValueError):
            self.pathfinder.dijkstra('X', 'A')
        
        with self.assertRaises(ValueError):
            self.pathfinder.dijkstra('A', 'X')
    
    def test_near_optimal_paths(self):
        """Test finding paths within threshold of optimal"""
        # Find paths within 10% of optimal from A to E
        near_optimal = self.pathfinder.find_all_paths_within_threshold('A', 'E', 10.0)
        
        # Should find multiple paths with distance 40 (all optimal)
        self.assertGreater(len(near_optimal), 0)
        
        # All paths should be within threshold
        optimal_dist = 40
        threshold_dist = optimal_dist * 1.1  # 10% above optimal
        
        for distance, path in near_optimal:
            self.assertLessEqual(distance, threshold_dist)
            self.assertTrue(self._is_valid_path(path))
            self.assertEqual(path[0], 'A')
            self.assertEqual(path[-1], 'E')
    
    def test_complexity_analysis(self):
        """Test complexity analysis method"""
        complexity = self.pathfinder.analyze_complexity()
        
        # Check required fields
        self.assertIn('time_complexity', complexity)
        self.assertIn('space_complexity', complexity)
        self.assertIn('vertices', complexity)
        self.assertIn('edges', complexity)
        
        # Check values make sense
        self.assertEqual(complexity['vertices'], 5)
        self.assertGreater(complexity['edges'], 0)
        
        # Check complexity strings contain expected terms
        self.assertIn('log', complexity['time_complexity'])
        self.assertIn('O', complexity['time_complexity'])
    
    def test_bidirectional_paths(self):
        """Test that algorithm works correctly with bidirectional edges"""
        # Test reverse direction
        distance_ab, path_ab = self.pathfinder.dijkstra('A', 'B')
        distance_ba, path_ba = self.pathfinder.dijkstra('B', 'A')
        
        # Should have same distance (bidirectional)
        self.assertEqual(distance_ab, distance_ba)
        
        # Paths should be reverse of each other
        self.assertEqual(path_ab, list(reversed(path_ba)))
    
    def test_large_graph_performance(self):
        """Test performance with larger graph"""
        # Create a larger graph (grid-like)
        large_graph = {}
        for i in range(10):
            for j in range(10):
                node = f"{i},{j}"
                large_graph[node] = {}
                
                # Connect to adjacent nodes
                if i > 0:
                    large_graph[node][f"{i-1},{j}"] = 1
                if i < 9:
                    large_graph[node][f"{i+1},{j}"] = 1
                if j > 0:
                    large_graph[node][f"{i},{j-1}"] = 1
                if j < 9:
                    large_graph[node][f"{i},{j+1}"] = 1
        
        pathfinder = DijkstraPathFinder(large_graph)
        
        # Find path from corner to corner
        distance, path = pathfinder.dijkstra("0,0", "9,9")
        
        # Should find a path
        self.assertNotEqual(distance, float('inf'))
        self.assertGreater(len(path), 0)
        self.assertEqual(path[0], "0,0")
        self.assertEqual(path[-1], "9,9")
        
        # Manhattan distance should be 18
        self.assertEqual(distance, 18)
    
    def _is_valid_path(self, path):
        """Helper method to validate a path"""
        if not path:
            return False
        
        for i in range(len(path) - 1):
            current = path[i]
            next_node = path[i + 1]
            
            if current not in self.test_graph:
                return False
            if next_node not in self.test_graph[current]:
                return False
        
        return True
    
    def _calculate_path_distance(self, path):
        """Helper method to calculate total distance of a path"""
        if not path or len(path) < 2:
            return 0
        
        total_distance = 0
        for i in range(len(path) - 1):
            current = path[i]
            next_node = path[i + 1]
            total_distance += self.test_graph[current][next_node]
        
        return total_distance


if __name__ == "__main__":
    unittest.main(verbosity=2)