"""
Dijkstra's Algorithm implementation with path finding and analysis.

This module implements Dijkstra's shortest path algorithm with support for
finding optimal paths, analyzing complexity, and finding near-optimal paths.
"""

import heapq
from typing import Dict, List, Tuple, Optional, Set
import math


class DijkstraPathFinder:
    """
    A class implementing Dijkstra's algorithm for shortest path finding.
    
    Supports finding shortest paths, analyzing complexity, and finding
    paths within a specified percentage of the optimal solution.
    """
    
    def __init__(self, graph: Dict[str, Dict[str, int]]):
        """
        Initialize the path finder with a graph.
        
        Args:
            graph: Graph represented as adjacency list
                  {node: {neighbor: weight, ...}, ...}
        """
        self.graph = graph
        self.nodes = set(graph.keys())
        
    def dijkstra(self, start: str, end: str) -> Tuple[Optional[int], Optional[List[str]]]:
        """
        Find shortest path between two nodes using Dijkstra's algorithm.
        
        Args:
            start: Starting node
            end: Ending node
            
        Returns:
            Tuple of (shortest_distance, path) or (None, None) if no path exists
        """
        if start not in self.graph or end not in self.graph:
            return None, None
            
        # Initialize distances and previous nodes
        distances = {node: math.inf for node in self.nodes}
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
            
            # Found the destination
            if current_node == end:
                break
                
            # Check all neighbors
            for neighbor, weight in self.graph[current_node].items():
                if neighbor in visited:
                    continue
                    
                new_dist = current_dist + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (new_dist, neighbor))
        
        # Reconstruct path
        if distances[end] == math.inf:
            return None, None
            
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        
        return distances[end], path
    
    def find_all_paths_within_threshold(self, start: str, end: str, threshold_percent: float = 10) -> List[Tuple[int, List[str]]]:
        """
        Find all paths within a percentage threshold of the optimal path.
        
        Args:
            start: Starting node
            end: Ending node
            threshold_percent: Percentage above optimal (default: 10%)
            
        Returns:
            List of (distance, path) tuples within threshold
        """
        optimal_dist, optimal_path = self.dijkstra(start, end)
        if optimal_dist is None:
            return []
        
        max_allowed_dist = optimal_dist * (1 + threshold_percent / 100)
        valid_paths = []
        
        # Use DFS to find all paths within threshold
        def dfs(current: str, target: str, path: List[str], distance: int, visited: Set[str]):
            if distance > max_allowed_dist:
                return
                
            if current == target:
                valid_paths.append((distance, path[:]))
                return
                
            for neighbor, weight in self.graph[current].items():
                if neighbor not in visited:
                    visited.add(neighbor)
                    path.append(neighbor)
                    dfs(neighbor, target, path, distance + weight, visited)
                    path.pop()
                    visited.remove(neighbor)
        
        visited = {start}
        dfs(start, end, [start], 0, visited)
        
        # Sort by distance
        valid_paths.sort(key=lambda x: x[0])
        return valid_paths
    
    def analyze_complexity(self) -> str:
        """
        Analyze the time and space complexity of Dijkstra's algorithm.
        
        Returns:
            String description of complexity analysis
        """
        V = len(self.nodes)
        E = sum(len(neighbors) for neighbors in self.graph.values())
        
        analysis = f"""
Dijkstra's Algorithm Complexity Analysis:

Graph Properties:
- Vertices (V): {V}
- Edges (E): {E}

Time Complexity:
- Using binary heap: O((V + E) log V)
- Breakdown:
  * Each vertex is extracted from heap once: O(V log V)
  * Each edge is relaxed at most once: O(E log V)
  * Total: O((V + E) log V)

Space Complexity:
- Distance array: O(V)
- Priority queue: O(V) in worst case
- Previous array: O(V)
- Total: O(V)

For this specific graph:
- Time: O(({V} + {E}) log {V}) = O({V + E} log {V})
- Space: O({V})
"""
        return analysis


def solve_city_network_problem():
    """Solve the specific city network problem."""
    # Define the graph
    graph = {
        'A': {'B': 10, 'C': 15},
        'B': {'A': 10, 'C': 5, 'D': 20},
        'C': {'A': 15, 'B': 5, 'D': 10, 'E': 25},
        'D': {'B': 20, 'C': 10, 'E': 15},
        'E': {'C': 25, 'D': 15}
    }
    
    print("=== City Network Optimization Problem ===\n")
    print("Graph connections:")
    for city, connections in graph.items():
        connections_str = ", ".join(f"{neighbor}: {weight}" for neighbor, weight in connections.items())
        print(f"  {city}: {connections_str}")
    
    # Create path finder
    finder = DijkstraPathFinder(graph)
    
    # Find shortest path from A to E
    print("\n1. Finding shortest path from A to E:")
    distance, path = finder.dijkstra('A', 'E')
    print(f"   Shortest distance: {distance} minutes")
    print(f"   Path: {' -> '.join(path)}")
    
    # Prove optimality
    print("\n2. Proof of optimality:")
    print("   All possible paths from A to E:")
    all_paths = finder.find_all_paths_within_threshold('A', 'E', 100)  # Get all paths
    for i, (dist, path) in enumerate(all_paths[:10]):  # Show first 10
        print(f"   Path {i+1}: {' -> '.join(path)} = {dist} minutes")
    print(f"   (Showing first 10 of {len(all_paths)} total paths)")
    print(f"   Optimal path has minimum distance: {distance} minutes")
    
    # Complexity analysis
    print("\n3. Complexity Analysis:")
    print(finder.analyze_complexity())
    
    # Find near-optimal paths
    print("\n4. Paths within 10% of optimal:")
    near_optimal = finder.find_all_paths_within_threshold('A', 'E', 10)
    for i, (dist, path) in enumerate(near_optimal):
        percent_above = ((dist - distance) / distance) * 100
        print(f"   Path {i+1}: {' -> '.join(path)} = {dist} minutes (+{percent_above:.1f}%)")
    
    return finder


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n=== Testing Edge Cases ===\n")
    
    # Test disconnected graph
    disconnected_graph = {
        'A': {'B': 10},
        'B': {'A': 10},
        'C': {'D': 5},
        'D': {'C': 5}
    }
    
    finder = DijkstraPathFinder(disconnected_graph)
    print("Testing disconnected graph:")
    distance, path = finder.dijkstra('A', 'C')
    print(f"  A to C: {distance}, {path}")
    
    # Test single node
    single_node = {'A': {}}
    finder = DijkstraPathFinder(single_node)
    print("\nTesting single node:")
    distance, path = finder.dijkstra('A', 'A')
    print(f"  A to A: {distance}, {path}")
    
    # Test nonexistent nodes
    finder = DijkstraPathFinder({'A': {'B': 1}, 'B': {'A': 1}})
    print("\nTesting nonexistent nodes:")
    distance, path = finder.dijkstra('A', 'Z')
    print(f"  A to Z: {distance}, {path}")


if __name__ == "__main__":
    # Solve the main problem
    finder = solve_city_network_problem()
    
    # Test edge cases
    test_edge_cases()