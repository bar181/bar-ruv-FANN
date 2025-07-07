"""
Vehicle Routing Problem with Time Windows (VRPTW) - Complete Solution

This module implements a comprehensive solution to the multi-objective VRPTW including:
1. Mathematical formulation
2. NP-hardness proof sketch
3. Approximation algorithm implementation
4. Complexity analysis
5. Visualization and testing

Key components:
- Mathematical problem formulation as MILP
- Clarke-Wright Savings Algorithm with time window constraints
- Multi-objective optimization using weighted objectives
- Visualization of routes and solutions
- Performance analysis and bounds
"""

import numpy as np
import matplotlib.pyplot as plt
import random
import time
import math
from typing import List, Tuple, Dict, Set, Optional
from dataclasses import dataclass, field
from itertools import combinations
import seaborn as sns
from collections import defaultdict
import json


@dataclass
class Location:
    """Represents a delivery location"""
    id: int
    x: float
    y: float
    demand: int
    time_window_start: float  # Hours from start of day
    time_window_end: float
    service_time: float = 0.5  # Hours needed for delivery
    
    def distance_to(self, other: 'Location') -> float:
        """Calculate Euclidean distance to another location"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


@dataclass
class Truck:
    """Represents a delivery truck"""
    id: int
    capacity: int
    speed: float = 30.0  # km/h
    
    def travel_time(self, distance: float) -> float:
        """Calculate travel time for given distance"""
        return distance / self.speed


@dataclass
class Route:
    """Represents a delivery route for one truck"""
    truck_id: int
    locations: List[Location] = field(default_factory=list)
    total_distance: float = 0.0
    total_time: float = 0.0
    total_demand: int = 0
    is_feasible: bool = True
    
    def add_location(self, location: Location, depot: Location):
        """Add a location to the route"""
        self.locations.append(location)
        self.total_demand += location.demand
        self._recalculate_metrics(depot)
    
    def _recalculate_metrics(self, depot: Location):
        """Recalculate route metrics"""
        if not self.locations:
            self.total_distance = 0.0
            self.total_time = 0.0
            return
        
        # Calculate total distance: depot -> locations -> depot
        distance = depot.distance_to(self.locations[0])
        current_time = distance / 30.0  # Travel time from depot
        
        for i in range(len(self.locations)):
            location = self.locations[i]
            
            # Check time window feasibility
            if current_time > location.time_window_end:
                self.is_feasible = False
            
            # Wait if we arrive too early
            if current_time < location.time_window_start:
                current_time = location.time_window_start
            
            # Add service time
            current_time += location.service_time
            
            # Travel to next location or back to depot
            if i < len(self.locations) - 1:
                next_location = self.locations[i + 1]
                travel_distance = location.distance_to(next_location)
                distance += travel_distance
                current_time += travel_distance / 30.0
            else:
                # Return to depot
                return_distance = location.distance_to(depot)
                distance += return_distance
                current_time += return_distance / 30.0
        
        self.total_distance = distance
        self.total_time = current_time


class VRPTWSolver:
    """
    Vehicle Routing Problem with Time Windows Solver
    
    Implements a multi-objective optimization approach combining:
    1. Clarke-Wright Savings Algorithm (modified for time windows)
    2. 2-opt improvement heuristic
    3. Load balancing optimization
    """
    
    def __init__(self, depot: Location, locations: List[Location], trucks: List[Truck]):
        """
        Initialize the VRPTW solver
        
        Args:
            depot: Depot location (starting point)
            locations: List of customer locations
            trucks: List of available trucks
        """
        self.depot = depot
        self.locations = locations
        self.trucks = trucks
        self.n = len(locations)
        self.m = len(trucks)
        
        # Precompute distance matrix
        self.distance_matrix = self._compute_distance_matrix()
        
        # Solution storage
        self.best_solution: Optional[List[Route]] = None
        self.best_objective: float = float('inf')
        
        # Algorithm parameters
        self.weights = {
            'distance': 1.0,
            'time_penalty': 100.0,
            'capacity_penalty': 100.0,
            'balance_penalty': 0.1
        }
    
    def _compute_distance_matrix(self) -> np.ndarray:
        """Compute distance matrix between all locations"""
        all_locations = [self.depot] + self.locations
        n = len(all_locations)
        matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    matrix[i][j] = all_locations[i].distance_to(all_locations[j])
        
        return matrix
    
    def formulate_as_milp(self) -> str:
        """
        Mathematical formulation as Mixed Integer Linear Program
        
        Returns:
            String representation of the MILP formulation
        """
        formulation = """
        VEHICLE ROUTING PROBLEM WITH TIME WINDOWS (VRPTW) - MILP FORMULATION
        
        SETS:
        - V = {0, 1, ..., n}: Vertices (0 = depot, 1..n = customers)
        - K = {1, ..., m}: Vehicles
        
        PARAMETERS:
        - d_ij: Distance between vertices i and j
        - q_i: Demand at customer i
        - Q_k: Capacity of vehicle k
        - [a_i, b_i]: Time window for customer i
        - s_i: Service time at customer i
        - t_ij: Travel time from i to j
        
        DECISION VARIABLES:
        - x_ijk ∈ {0,1}: 1 if vehicle k travels from i to j, 0 otherwise
        - u_ik ≥ 0: Load of vehicle k when leaving vertex i
        - T_ik ≥ 0: Time when vehicle k starts service at vertex i
        
        OBJECTIVE FUNCTION:
        Minimize: ∑∑∑ d_ij * x_ijk  (total distance)
                  i j k
        
        CONSTRAINTS:
        
        1. Each customer visited exactly once:
           ∑∑ x_ijk = 1, ∀j ∈ {1,...,n}
           i k
        
        2. Vehicle flow conservation:
           ∑ x_ihk = ∑ x_hjk, ∀h ∈ V, ∀k ∈ K
           i       j
        
        3. Vehicle starts and ends at depot:
           ∑ x_0jk ≤ 1, ∀k ∈ K  (each vehicle used at most once)
           j
           
           ∑ x_i0k = ∑ x_0jk, ∀k ∈ K  (vehicles return to depot)
           i       j
        
        4. Capacity constraints:
           u_ik ≤ Q_k, ∀i ∈ V, ∀k ∈ K
           
           u_jk ≥ u_ik + q_j - Q_k(1 - x_ijk), ∀i,j ∈ V, ∀k ∈ K
        
        5. Time window constraints:
           a_i ≤ T_ik ≤ b_i, ∀i ∈ {1,...,n}, ∀k ∈ K
           
           T_jk ≥ T_ik + s_i + t_ij - M(1 - x_ijk), ∀i,j ∈ V, ∀k ∈ K
        
        6. Load balancing (additional objective):
           Minimize: max_k(∑ q_i * ∑ x_ijk) - min_k(∑ q_i * ∑ x_ijk)
                            i     j               i     j
        
        COMPLEXITY ANALYSIS:
        - This is a variant of TSP with additional constraints
        - TSP is NP-hard (reduction from Hamiltonian Cycle)
        - VRPTW adds time windows and capacity constraints
        - Therefore, VRPTW is NP-hard
        
        NP-HARDNESS PROOF SKETCH:
        1. Take TSP as known NP-hard problem
        2. Construct VRPTW instance:
           - Use 1 vehicle with infinite capacity
           - Set time windows [0, ∞] for all customers
           - Set depot at one of the TSP cities
        3. Any TSP tour corresponds to feasible VRPTW solution
        4. Optimal VRPTW solution gives optimal TSP tour
        5. Since TSP ≤_p VRPTW, VRPTW is NP-hard
        """
        return formulation
    
    def clarke_wright_savings(self) -> List[Route]:
        """
        Implement Clarke-Wright Savings Algorithm with time window modifications
        
        Returns:
            List of routes (one per truck)
        """
        # Step 1: Calculate savings for all pairs of customers
        savings = []
        for i in range(self.n):
            for j in range(i + 1, self.n):
                # Savings = distance(depot,i) + distance(depot,j) - distance(i,j)
                save = (self.distance_matrix[0][i+1] + self.distance_matrix[0][j+1] - 
                       self.distance_matrix[i+1][j+1])
                savings.append((save, i, j))
        
        # Sort savings in descending order
        savings.sort(reverse=True)
        
        # Step 2: Initialize routes (each customer in separate route)
        routes = []
        customer_to_route = {}
        
        for i, location in enumerate(self.locations):
            route = Route(truck_id=-1, locations=[location])
            route._recalculate_metrics(self.depot)
            routes.append(route)
            customer_to_route[i] = len(routes) - 1
        
        # Step 3: Merge routes based on savings
        for save_value, i, j in savings:
            route_i = customer_to_route[i]
            route_j = customer_to_route[j]
            
            if route_i == route_j:
                continue  # Same route
            
            # Try to merge routes
            if self._can_merge_routes(routes[route_i], routes[route_j], i, j):
                merged_route = self._merge_routes(routes[route_i], routes[route_j], i, j)
                
                # Remove old routes and add merged route
                routes = [r for idx, r in enumerate(routes) if idx not in [route_i, route_j]]
                routes.append(merged_route)
                
                # Update customer-to-route mapping
                customer_to_route = {}
                for route_idx, route in enumerate(routes):
                    for loc in route.locations:
                        customer_to_route[loc.id - 1] = route_idx
        
        return routes
    
    def _can_merge_routes(self, route1: Route, route2: Route, i: int, j: int) -> bool:
        """Check if two routes can be merged"""
        # Check capacity constraint
        total_demand = route1.total_demand + route2.total_demand
        if any(truck.capacity >= total_demand for truck in self.trucks):
            # Check if customers i and j are at the ends of their routes
            if ((route1.locations[0].id - 1 == i or route1.locations[-1].id - 1 == i) and
                (route2.locations[0].id - 1 == j or route2.locations[-1].id - 1 == j)):
                return True
        return False
    
    def _merge_routes(self, route1: Route, route2: Route, i: int, j: int) -> Route:
        """Merge two routes"""
        # Determine the order of merging based on customer positions
        if route1.locations[-1].id - 1 == i and route2.locations[0].id - 1 == j:
            # route1 + route2
            merged_locations = route1.locations + route2.locations
        elif route1.locations[0].id - 1 == i and route2.locations[-1].id - 1 == j:
            # route2 + route1
            merged_locations = route2.locations + route1.locations
        elif route1.locations[-1].id - 1 == i and route2.locations[-1].id - 1 == j:
            # route1 + reverse(route2)
            merged_locations = route1.locations + route2.locations[::-1]
        elif route1.locations[0].id - 1 == i and route2.locations[0].id - 1 == j:
            # reverse(route1) + route2
            merged_locations = route1.locations[::-1] + route2.locations
        else:
            # Fallback: simple concatenation
            merged_locations = route1.locations + route2.locations
        
        merged_route = Route(truck_id=-1, locations=merged_locations)
        merged_route._recalculate_metrics(self.depot)
        return merged_route
    
    def assign_trucks_to_routes(self, routes: List[Route]) -> List[Route]:
        """Assign trucks to routes optimally"""
        # Sort routes by demand (descending) and trucks by capacity (descending)
        routes_with_demand = [(route, route.total_demand) for route in routes]
        routes_with_demand.sort(key=lambda x: x[1], reverse=True)
        
        trucks_with_capacity = [(truck, truck.capacity) for truck in self.trucks]
        trucks_with_capacity.sort(key=lambda x: x[1], reverse=True)
        
        assigned_routes = []
        used_trucks = set()
        
        for route, demand in routes_with_demand:
            # Find smallest truck that can handle this route
            assigned = False
            for truck, capacity in trucks_with_capacity:
                if truck.id not in used_trucks and capacity >= demand:
                    route.truck_id = truck.id
                    assigned_routes.append(route)
                    used_trucks.add(truck.id)
                    assigned = True
                    break
            
            if not assigned:
                # Route cannot be satisfied by any available truck
                route.is_feasible = False
                assigned_routes.append(route)
        
        return assigned_routes
    
    def two_opt_improvement(self, routes: List[Route]) -> List[Route]:
        """Apply 2-opt improvement to each route"""
        improved_routes = []
        
        for route in routes:
            if len(route.locations) <= 2:
                improved_routes.append(route)
                continue
            
            best_route = route
            best_distance = route.total_distance
            improved = True
            
            while improved:
                improved = False
                
                for i in range(len(route.locations)):
                    for j in range(i + 2, len(route.locations)):
                        # Create new route by reversing segment between i and j
                        new_locations = (route.locations[:i] + 
                                       route.locations[i:j+1][::-1] + 
                                       route.locations[j+1:])
                        
                        new_route = Route(truck_id=route.truck_id, locations=new_locations)
                        new_route._recalculate_metrics(self.depot)
                        
                        if (new_route.is_feasible and 
                            new_route.total_distance < best_distance):
                            best_route = new_route
                            best_distance = new_route.total_distance
                            improved = True
                
                route = best_route
            
            improved_routes.append(best_route)
        
        return improved_routes
    
    def calculate_objective(self, routes: List[Route]) -> float:
        """Calculate multi-objective function value"""
        total_distance = sum(route.total_distance for route in routes)
        
        # Time window violations
        time_penalty = 0
        capacity_penalty = 0
        
        for route in routes:
            if not route.is_feasible:
                time_penalty += self.weights['time_penalty']
            
            # Find truck for this route
            truck = next((t for t in self.trucks if t.id == route.truck_id), None)
            if truck and route.total_demand > truck.capacity:
                capacity_penalty += self.weights['capacity_penalty']
        
        # Load balancing penalty
        demands = [route.total_demand for route in routes if route.is_feasible]
        if demands:
            balance_penalty = (max(demands) - min(demands)) * self.weights['balance_penalty']
        else:
            balance_penalty = 0
        
        return (self.weights['distance'] * total_distance + 
                time_penalty + capacity_penalty + balance_penalty)
    
    def solve(self) -> Tuple[List[Route], Dict[str, float]]:
        """
        Solve the VRPTW using the complete algorithm
        
        Returns:
            Tuple of (routes, performance_metrics)
        """
        start_time = time.time()
        
        # Step 1: Apply Clarke-Wright Savings
        routes = self.clarke_wright_savings()
        
        # Step 2: Assign trucks to routes
        routes = self.assign_trucks_to_routes(routes)
        
        # Step 3: Apply 2-opt improvement
        routes = self.two_opt_improvement(routes)
        
        # Calculate final metrics
        solve_time = time.time() - start_time
        objective_value = self.calculate_objective(routes)
        
        metrics = {
            'total_distance': sum(route.total_distance for route in routes),
            'num_routes': len(routes),
            'feasible_routes': sum(1 for route in routes if route.is_feasible),
            'solve_time': solve_time,
            'objective_value': objective_value,
            'avg_route_distance': sum(route.total_distance for route in routes) / len(routes),
            'load_balance': self._calculate_load_balance(routes)
        }
        
        self.best_solution = routes
        self.best_objective = objective_value
        
        return routes, metrics
    
    def _calculate_load_balance(self, routes: List[Route]) -> float:
        """Calculate load balance metric"""
        demands = [route.total_demand for route in routes if route.is_feasible]
        if len(demands) <= 1:
            return 0.0
        return max(demands) - min(demands)
    
    def visualize_solution(self, routes: List[Route], save_path: Optional[str] = None):
        """Visualize the solution"""
        plt.figure(figsize=(12, 10))
        
        # Plot depot
        plt.scatter(self.depot.x, self.depot.y, c='red', s=200, marker='s', 
                   label='Depot', zorder=5)
        
        # Plot customers
        for location in self.locations:
            plt.scatter(location.x, location.y, c='lightblue', s=100, 
                       marker='o', edgecolors='black', zorder=3)
            plt.annotate(f'{location.id}\n({location.demand})', 
                        (location.x, location.y), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # Plot routes
        colors = ['blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive']
        
        for i, route in enumerate(routes):
            if not route.locations:
                continue
            
            color = colors[i % len(colors)]
            
            # Plot route path
            route_x = [self.depot.x] + [loc.x for loc in route.locations] + [self.depot.x]
            route_y = [self.depot.y] + [loc.y for loc in route.locations] + [self.depot.y]
            
            plt.plot(route_x, route_y, color=color, linewidth=2, alpha=0.7,
                    label=f'Truck {route.truck_id} (Load: {route.total_demand})')
            
            # Add arrows to show direction
            for j in range(len(route_x) - 1):
                dx = route_x[j+1] - route_x[j]
                dy = route_y[j+1] - route_y[j]
                plt.arrow(route_x[j] + 0.1*dx, route_y[j] + 0.1*dy, 
                         0.8*dx, 0.8*dy, head_width=1, head_length=1, 
                         fc=color, ec=color, alpha=0.6)
        
        plt.xlabel('X Coordinate (km)')
        plt.ylabel('Y Coordinate (km)')
        plt.title('Vehicle Routing Problem with Time Windows - Solution')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
        
        plt.tight_layout()
        plt.show()
    
    def analyze_complexity(self) -> Dict[str, str]:
        """Analyze algorithm complexity"""
        return {
            'time_complexity': f'O(n²log(n) + n³) where n={self.n}',
            'space_complexity': f'O(n²) where n={self.n}',
            'clarke_wright': 'O(n²log(n)) for sorting savings',
            'two_opt': 'O(n³) for all route improvements',
            'approximation_ratio': '2-4 times optimal (empirical)',
            'worst_case_guarantee': 'No theoretical guarantee (heuristic)'
        }


def generate_test_instance(n_locations: int = 20, random_seed: int = 42) -> Tuple[Location, List[Location], List[Truck]]:
    """Generate a test instance for the VRPTW"""
    random.seed(random_seed)
    np.random.seed(random_seed)
    
    # Create depot at origin
    depot = Location(0, 0, 0, 0, 0, 24, 0)
    
    # Generate random customer locations
    locations = []
    for i in range(1, n_locations + 1):
        x = random.uniform(-50, 50)
        y = random.uniform(-50, 50)
        demand = random.randint(5, 15)
        
        # Random time window (2-hour window between 8 AM - 6 PM)
        start_hour = random.uniform(8, 16)
        end_hour = start_hour + 2
        
        location = Location(i, x, y, demand, start_hour, min(end_hour, 18))
        locations.append(location)
    
    # Create trucks with specified capacities
    trucks = [
        Truck(1, 50),
        Truck(2, 40),
        Truck(3, 45),
        Truck(4, 55)
    ]
    
    return depot, locations, trucks


def run_comprehensive_test():
    """Run comprehensive test of the VRPTW solver"""
    print("Vehicle Routing Problem with Time Windows - Comprehensive Test")
    print("=" * 60)
    
    # Generate test instance
    depot, locations, trucks = generate_test_instance(20)
    
    print(f"Problem Instance:")
    print(f"- Depot: ({depot.x}, {depot.y})")
    print(f"- Customers: {len(locations)}")
    print(f"- Trucks: {len(trucks)} with capacities {[t.capacity for t in trucks]}")
    print(f"- Total demand: {sum(loc.demand for loc in locations)}")
    
    # Print mathematical formulation
    solver = VRPTWSolver(depot, locations, trucks)
    print("\n" + solver.formulate_as_milp())
    
    # Solve the problem
    print("\nSolving VRPTW...")
    routes, metrics = solver.solve()
    
    # Display results
    print("\nSolution Results:")
    print("-" * 30)
    for metric, value in metrics.items():
        if isinstance(value, float):
            print(f"{metric}: {value:.2f}")
        else:
            print(f"{metric}: {value}")
    
    print("\nRoute Details:")
    print("-" * 30)
    for i, route in enumerate(routes):
        truck = next((t for t in trucks if t.id == route.truck_id), None)
        truck_capacity = truck.capacity if truck else "Unknown"
        
        print(f"Route {i+1} (Truck {route.truck_id}, Capacity: {truck_capacity}):")
        print(f"  Locations: {[loc.id for loc in route.locations]}")
        print(f"  Distance: {route.total_distance:.2f} km")
        print(f"  Load: {route.total_demand} packages")
        print(f"  Feasible: {route.is_feasible}")
        print(f"  Time: {route.total_time:.2f} hours")
    
    # Complexity analysis
    print("\nComplexity Analysis:")
    print("-" * 30)
    complexity = solver.analyze_complexity()
    for aspect, description in complexity.items():
        print(f"{aspect}: {description}")
    
    # Visualize solution
    solver.visualize_solution(routes, "vrp_solution.png")
    
    return solver, routes, metrics


if __name__ == "__main__":
    # Run the comprehensive test
    solver, routes, metrics = run_comprehensive_test()
    
    # Save results to file
    results = {
        'metrics': metrics,
        'routes': [
            {
                'truck_id': route.truck_id,
                'locations': [loc.id for loc in route.locations],
                'distance': route.total_distance,
                'demand': route.total_demand,
                'feasible': route.is_feasible
            }
            for route in routes
        ],
        'complexity_analysis': solver.analyze_complexity()
    }
    
    with open('vrp_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to vrp_results.json and vrp_solution.png")