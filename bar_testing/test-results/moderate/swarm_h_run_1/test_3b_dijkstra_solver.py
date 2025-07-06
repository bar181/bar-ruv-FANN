#!/usr/bin/env python3
"""
Dijkstra's Algorithm Implementation with Path Finding
QA Division - Test 3b: Mathematical Problem (Moderate)
Implemented by: QA Manager, Performance Engineer, Security Architect, Data Scientist, Quality Optimizer
"""

import heapq
from typing import Dict, List, Tuple, Optional, Set
import math


class DijkstraPathFinder:
    """
    Comprehensive Dijkstra's algorithm implementation for shortest path finding.
    
    Features:
    - Shortest path and distance calculation
    - Handles disconnected graphs
    - Finds all paths within percentage of optimal
    - Comprehensive error handling
    - Performance optimized with binary heap
    """
    
    def __init__(self, graph: Dict[str, Dict[str, int]]):
        """
        Initialize with adjacency list representation.
        
        Args:
            graph: Dictionary where keys are nodes and values are 
                  dictionaries of {neighbor: weight}
        
        Raises:
            ValueError: If graph is empty or has invalid structure
        """
        if not graph:
            raise ValueError("Graph cannot be empty")
        
        # Validate graph structure
        for node, neighbors in graph.items():
            if not isinstance(neighbors, dict):
                raise ValueError(f"Neighbors for {node} must be a dictionary")
            for neighbor, weight in neighbors.items():
                if not isinstance(weight, (int, float)) or weight < 0:
                    raise ValueError(f"Weight {weight} for edge {node}-{neighbor} must be non-negative number")
        
        self.graph = graph
        self.nodes = set(graph.keys())
        
        # Add all referenced neighbors to nodes set
        for neighbors in graph.values():
            self.nodes.update(neighbors.keys())
    
    def dijkstra(self, start: str, end: str) -> Tuple[float, List[str]]:
        """
        Find shortest path from start to end using Dijkstra's algorithm.
        
        Args:
            start: Starting node
            end: Destination node
        
        Returns:
            Tuple of (distance, path) where:
            - distance: Shortest distance (float('inf') if no path)
            - path: List of nodes in shortest path (empty if no path)
        
        Raises:
            ValueError: If start or end nodes don't exist in graph
        """
        if start not in self.nodes:
            raise ValueError(f"Start node '{start}' not found in graph")
        if end not in self.nodes:
            raise ValueError(f"End node '{end}' not found in graph")
        
        # Initialize distances and previous nodes
        distances = {node: float('inf') for node in self.nodes}
        previous = {node: None for node in self.nodes}
        distances[start] = 0
        
        # Priority queue: (distance, node)
        pq = [(0, start)]
        visited = set()
        
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            # Found target
            if current_node == end:
                break
            
            # Skip if this distance is outdated
            if current_dist > distances[current_node]:
                continue
            
            # Check neighbors
            for neighbor, weight in self.graph.get(current_node, {}).items():
                new_distance = current_dist + weight
                
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (new_distance, neighbor))
        
        # Reconstruct path
        path = []
        if distances[end] != float('inf'):
            current = end
            while current is not None:
                path.append(current)
                current = previous[current]
            path.reverse()
        
        return distances[end], path
    
    def find_all_paths_within_threshold(self, start: str, end: str, threshold_percent: float = 10.0) -> List[Tuple[float, List[str]]]:
        """
        Find all paths within a percentage threshold of the optimal path.
        
        Args:
            start: Starting node
            end: Destination node
            threshold_percent: Percentage above optimal (default 10%)
        
        Returns:
            List of (distance, path) tuples within threshold
        """
        # First find optimal path
        optimal_dist, optimal_path = self.dijkstra(start, end)
        
        if optimal_dist == float('inf'):
            return []
        
        # Calculate threshold distance
        threshold_dist = optimal_dist * (1 + threshold_percent / 100)
        
        # Find all paths using modified Dijkstra
        all_paths = []
        
        # Use a modified approach to find multiple paths
        # Priority queue: (distance, node, path)
        pq = [(0, start, [start])]
        visited_with_distance = {}
        
        while pq:
            current_dist, current_node, path = heapq.heappop(pq)
            
            # Skip if we've found a better path to this node
            if current_node in visited_with_distance:
                if current_dist > visited_with_distance[current_node] * 1.1:  # Small tolerance
                    continue
            else:
                visited_with_distance[current_node] = current_dist
            
            # Found target within threshold
            if current_node == end and current_dist <= threshold_dist:
                all_paths.append((current_dist, path))
                continue
            
            # Skip if already too far
            if current_dist > threshold_dist:
                continue
            
            # Explore neighbors
            for neighbor, weight in self.graph.get(current_node, {}).items():
                if neighbor not in path:  # Avoid cycles
                    new_distance = current_dist + weight
                    new_path = path + [neighbor]
                    
                    if new_distance <= threshold_dist:
                        heapq.heappush(pq, (new_distance, neighbor, new_path))
        
        # Sort by distance
        all_paths.sort(key=lambda x: x[0])
        return all_paths
    
    def analyze_complexity(self) -> Dict[str, str]:
        """
        Analyze time and space complexity of the algorithm.
        
        Returns:
            Dictionary with complexity analysis
        """
        V = len(self.nodes)
        E = sum(len(neighbors) for neighbors in self.graph.values())
        
        return {
            "time_complexity": f"O((V + E) log V) = O(({V} + {E}) log {V})",
            "space_complexity": f"O(V) = O({V})",
            "vertices": V,
            "edges": E,
            "explanation": {
                "time": "Each edge is processed once, and heap operations are O(log V)",
                "space": "We store distances and previous nodes for each vertex"
            }
        }


# Test the specific problem from the prompt
def solve_network_problem():
    """Solve the specific network optimization problem"""
    
    print("=== Network Optimization Problem ===")
    print("Cities: A, B, C, D, E")
    print("Connections: A-B:10, A-C:15, B-C:5, B-D:20, C-D:10, C-E:25, D-E:15")
    
    # Create the graph
    graph = {
        'A': {'B': 10, 'C': 15},
        'B': {'A': 10, 'C': 5, 'D': 20},
        'C': {'A': 15, 'B': 5, 'D': 10, 'E': 25},
        'D': {'B': 20, 'C': 10, 'E': 15},
        'E': {'C': 25, 'D': 15}
    }
    
    pathfinder = DijkstraPathFinder(graph)
    
    # Find shortest path from A to E
    distance, path = pathfinder.dijkstra('A', 'E')
    
    print(f"\n1. Shortest path from A to E:")
    print(f"   Path: {' -> '.join(path)}")
    print(f"   Distance: {distance} minutes")
    
    # Prove optimality
    print(f"\n2. Proof of optimality:")
    print(f"   All possible paths from A to E:")
    
    # Manual verification of all paths
    all_possible_paths = [
        (['A', 'B', 'C', 'D', 'E'], 10 + 5 + 10 + 15),  # A->B->C->D->E = 40
        (['A', 'B', 'C', 'E'], 10 + 5 + 25),            # A->B->C->E = 40
        (['A', 'B', 'D', 'E'], 10 + 20 + 15),           # A->B->D->E = 45
        (['A', 'C', 'B', 'D', 'E'], 15 + 5 + 20 + 15),  # A->C->B->D->E = 55
        (['A', 'C', 'D', 'E'], 15 + 10 + 15),           # A->C->D->E = 40
        (['A', 'C', 'E'], 15 + 25),                     # A->C->E = 40
    ]
    
    for path_nodes, dist in all_possible_paths:
        print(f"   {' -> '.join(path_nodes)}: {dist} minutes")
    
    optimal_distance = min(dist for _, dist in all_possible_paths)
    print(f"   Minimum distance: {optimal_distance} minutes")
    print(f"   Our algorithm found: {distance} minutes")
    print(f"   Correctness: {'✓' if distance == optimal_distance else '✗'}")
    
    # Complexity analysis
    complexity = pathfinder.analyze_complexity()
    print(f"\n3. Complexity Analysis:")
    print(f"   Time: {complexity['time_complexity']}")
    print(f"   Space: {complexity['space_complexity']}")
    print(f"   Explanation: {complexity['explanation']['time']}")
    
    # Find near-optimal paths
    print(f"\n4. All paths within 10% of optimal:")
    near_optimal = pathfinder.find_all_paths_within_threshold('A', 'E', 10.0)
    for dist, path_nodes in near_optimal:
        deviation = ((dist - optimal_distance) / optimal_distance) * 100
        print(f"   {' -> '.join(path_nodes)}: {dist} minutes (+{deviation:.1f}%)")
    
    return distance, path


if __name__ == "__main__":
    try:
        distance, path = solve_network_problem()
        print(f"\n=== Final Answer ===")
        print(f"Shortest path from A to E: {' -> '.join(path)}")
        print(f"Distance: {distance} minutes")
    except Exception as e:
        print(f"Error: {e}")
        raise