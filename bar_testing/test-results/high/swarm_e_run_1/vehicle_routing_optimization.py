"""
Vehicle Routing Problem with Time Windows (VRPTW) Solution

This implementation provides:
1. Mathematical formulation as Mixed Integer Linear Programming (MILP)
2. NP-hardness proof through reduction
3. Efficient approximation algorithms
4. Visualization capabilities
5. Complexity analysis
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Set, Optional
from dataclasses import dataclass
from collections import defaultdict
import random
import math
import time
from itertools import combinations
import heapq


@dataclass
class Location:
    """Represents a delivery location"""
    id: int
    x: float
    y: float
    demand: int
    time_window_start: float  # Hours from 0 (midnight)
    time_window_end: float


@dataclass
class Truck:
    """Represents a delivery truck"""
    id: int
    capacity: int
    current_load: int = 0
    route: List[int] = None
    total_distance: float = 0.0
    
    def __post_init__(self):
        if self.route is None:
            self.route = []


@dataclass
class Solution:
    """Represents a complete solution"""
    routes: Dict[int, List[int]]  # truck_id -> list of location_ids
    total_distance: float
    computation_time: float
    feasible: bool
    load_balance_score: float


class VehicleRoutingOptimizer:
    """
    Solves the Vehicle Routing Problem with Time Windows (VRPTW)
    
    Mathematical Formulation:
    
    Decision Variables:
    - x_ijk: Binary, 1 if truck k travels from location i to j
    - y_ik: Binary, 1 if location i is served by truck k
    - t_i: Arrival time at location i
    
    Objective:
    Minimize Σ_i Σ_j Σ_k c_ij * x_ijk
    where c_ij is the distance from location i to j
    
    Constraints:
    1. Each location visited exactly once: Σ_k y_ik = 1 ∀i
    2. Capacity constraints: Σ_i d_i * y_ik ≤ C_k ∀k
    3. Time window constraints: a_i ≤ t_i ≤ b_i ∀i
    4. Flow conservation: Σ_j x_jik = Σ_j x_ijk = y_ik ∀i,k
    5. Subtour elimination: Various formulations (MTZ, DFJ, etc.)
    """
    
    def __init__(self, locations: List[Location], trucks: List[Truck], 
                 depot: Tuple[float, float] = (0, 0), avg_speed: float = 30.0):
        self.locations = locations
        self.trucks = trucks
        self.depot = depot
        self.avg_speed = avg_speed  # km/h
        
        # Precompute distance matrix
        self.n_locations = len(locations)
        self.n_trucks = len(trucks)
        self.distance_matrix = self._compute_distance_matrix()
        
    def _compute_distance_matrix(self) -> np.ndarray:
        """Compute Euclidean distances between all pairs of locations"""
        n = self.n_locations + 1  # +1 for depot
        matrix = np.zeros((n, n))
        
        # Depot is at index 0
        for i in range(1, n):
            loc_i = self.locations[i-1]
            # Distance from depot to location i
            matrix[0][i] = matrix[i][0] = math.sqrt(
                (loc_i.x - self.depot[0])**2 + (loc_i.y - self.depot[1])**2
            )
            
            # Distance between locations
            for j in range(i+1, n):
                loc_j = self.locations[j-1]
                dist = math.sqrt((loc_i.x - loc_j.x)**2 + (loc_i.y - loc_j.y)**2)
                matrix[i][j] = matrix[j][i] = dist
        
        return matrix
    
    def prove_np_hardness(self) -> str:
        """
        Proof that VRPTW is NP-hard
        
        Returns a formal proof by reduction from TSP
        """
        proof = """
        THEOREM: The Vehicle Routing Problem with Time Windows (VRPTW) is NP-hard.
        
        PROOF by reduction from Traveling Salesman Problem (TSP):
        
        1. TSP is known to be NP-hard.
        
        2. We show TSP ≤_p VRPTW (TSP reduces to VRPTW in polynomial time).
        
        3. Construction:
           Given a TSP instance with n cities and distance matrix D:
           - Create a VRPTW instance with:
             * n delivery locations at the same coordinates as TSP cities
             * 1 truck with capacity = n (can visit all locations)
             * Each location has demand = 1
             * All time windows = [0, ∞) (no time constraints)
             * Depot at arbitrary location
        
        4. Correspondence:
           - Any TSP tour of length L corresponds to a VRPTW solution of length L + 2*d₀
             where d₀ is the distance from depot to the tour
           - The optimal VRPTW solution gives the optimal TSP tour
        
        5. The reduction takes O(n²) time to construct the distance matrix
        
        6. Therefore, since TSP is NP-hard and reduces to VRPTW, VRPTW is NP-hard.
        
        COROLLARY: No polynomial-time algorithm exists for VRPTW unless P = NP.
        
        PRACTICAL IMPLICATION: We must use approximation algorithms or heuristics.
        """
        return proof
    
    def solve_clarke_wright_savings(self) -> Solution:
        """
        Clarke-Wright Savings Algorithm
        
        Time Complexity: O(n² log n)
        Approximation Ratio: No fixed bound, but typically within 10-15% of optimal
        """
        start_time = time.time()
        
        # Initialize: each location is served by a separate route
        routes = {truck.id: [] for truck in self.trucks}
        unassigned = set(range(self.n_locations))
        
        # Calculate savings s_ij = d_0i + d_0j - d_ij for all pairs
        savings = []
        for i in range(self.n_locations):
            for j in range(i+1, self.n_locations):
                s = (self.distance_matrix[0][i+1] + 
                     self.distance_matrix[0][j+1] - 
                     self.distance_matrix[i+1][j+1])
                savings.append((s, i, j))
        
        # Sort savings in descending order
        savings.sort(reverse=True)
        
        # Merge routes based on savings
        for saving, i, j in savings:
            if i in unassigned and j in unassigned:
                # Find feasible truck
                for truck in self.trucks:
                    if self._can_merge_locations(truck, i, j):
                        routes[truck.id].extend([i, j])
                        unassigned.discard(i)
                        unassigned.discard(j)
                        truck.current_load += (self.locations[i].demand + 
                                             self.locations[j].demand)
                        break
            elif i in unassigned or j in unassigned:
                # Try to add to existing route
                loc_to_add = i if i in unassigned else j
                for truck_id, route in routes.items():
                    if self._can_add_to_route(self.trucks[truck_id], route, loc_to_add):
                        best_pos = self._find_best_insertion(route, loc_to_add)
                        route.insert(best_pos, loc_to_add)
                        unassigned.discard(loc_to_add)
                        self.trucks[truck_id].current_load += self.locations[loc_to_add].demand
                        break
        
        # Assign remaining locations
        for loc in unassigned:
            for truck in self.trucks:
                if truck.current_load + self.locations[loc].demand <= truck.capacity:
                    routes[truck.id].append(loc)
                    truck.current_load += self.locations[loc].demand
                    break
        
        # Calculate total distance
        total_distance = self._calculate_total_distance(routes)
        
        # Check feasibility
        feasible = len(unassigned) == 0 and self._check_time_windows(routes)
        
        computation_time = time.time() - start_time
        
        return Solution(
            routes=routes,
            total_distance=total_distance,
            computation_time=computation_time,
            feasible=feasible,
            load_balance_score=self._calculate_load_balance(routes)
        )
    
    def solve_genetic_algorithm(self, population_size: int = 100, 
                              generations: int = 500) -> Solution:
        """
        Genetic Algorithm for VRPTW
        
        Time Complexity: O(g * p * n²) where g=generations, p=population_size
        """
        start_time = time.time()
        
        # Initialize population
        population = []
        for _ in range(population_size):
            chromosome = self._generate_random_solution()
            population.append(chromosome)
        
        best_solution = None
        best_fitness = float('inf')
        
        for generation in range(generations):
            # Evaluate fitness
            fitness_scores = []
            for chromosome in population:
                fitness = self._evaluate_fitness(chromosome)
                fitness_scores.append(fitness)
                
                if fitness < best_fitness:
                    best_fitness = fitness
                    best_solution = chromosome.copy()
            
            # Selection
            selected = self._tournament_selection(population, fitness_scores)
            
            # Crossover and mutation
            new_population = []
            for i in range(0, len(selected), 2):
                if i+1 < len(selected):
                    parent1, parent2 = selected[i], selected[i+1]
                    child1, child2 = self._crossover(parent1, parent2)
                    child1 = self._mutate(child1)
                    child2 = self._mutate(child2)
                    new_population.extend([child1, child2])
                else:
                    new_population.append(selected[i])
            
            population = new_population[:population_size]
        
        # Convert best chromosome to solution
        routes = self._chromosome_to_routes(best_solution)
        
        computation_time = time.time() - start_time
        
        return Solution(
            routes=routes,
            total_distance=best_fitness,
            computation_time=computation_time,
            feasible=self._check_feasibility(routes),
            load_balance_score=self._calculate_load_balance(routes)
        )
    
    def solve_simulated_annealing(self, initial_temp: float = 1000, 
                                cooling_rate: float = 0.995,
                                iterations: int = 10000) -> Solution:
        """
        Simulated Annealing for VRPTW
        
        Time Complexity: O(iterations * n)
        """
        start_time = time.time()
        
        # Generate initial solution using nearest neighbor
        current_solution = self._nearest_neighbor_solution()
        current_cost = self._calculate_total_distance(current_solution)
        
        best_solution = current_solution.copy()
        best_cost = current_cost
        
        temperature = initial_temp
        
        for iteration in range(iterations):
            # Generate neighbor solution
            neighbor = self._generate_neighbor(current_solution)
            neighbor_cost = self._calculate_total_distance(neighbor)
            
            # Accept or reject
            delta = neighbor_cost - current_cost
            if delta < 0 or random.random() < math.exp(-delta / temperature):
                current_solution = neighbor
                current_cost = neighbor_cost
                
                if current_cost < best_cost:
                    best_solution = current_solution.copy()
                    best_cost = current_cost
            
            # Cool down
            temperature *= cooling_rate
        
        computation_time = time.time() - start_time
        
        return Solution(
            routes=best_solution,
            total_distance=best_cost,
            computation_time=computation_time,
            feasible=self._check_feasibility(best_solution),
            load_balance_score=self._calculate_load_balance(best_solution)
        )
    
    def _can_merge_locations(self, truck: Truck, loc1: int, loc2: int) -> bool:
        """Check if two locations can be merged into truck's route"""
        total_demand = self.locations[loc1].demand + self.locations[loc2].demand
        return truck.current_load + total_demand <= truck.capacity
    
    def _can_add_to_route(self, truck: Truck, route: List[int], 
                         location: int) -> bool:
        """Check if location can be added to existing route"""
        return truck.current_load + self.locations[location].demand <= truck.capacity
    
    def _find_best_insertion(self, route: List[int], location: int) -> int:
        """Find best position to insert location in route"""
        if not route:
            return 0
        
        best_pos = 0
        min_increase = float('inf')
        
        for i in range(len(route) + 1):
            increase = self._calculate_insertion_cost(route, location, i)
            if increase < min_increase:
                min_increase = increase
                best_pos = i
        
        return best_pos
    
    def _calculate_insertion_cost(self, route: List[int], location: int, 
                                position: int) -> float:
        """Calculate cost increase of inserting location at position"""
        if not route:
            return 2 * self.distance_matrix[0][location + 1]
        
        if position == 0:
            # Insert at beginning
            return (self.distance_matrix[0][location + 1] + 
                   self.distance_matrix[location + 1][route[0] + 1] - 
                   self.distance_matrix[0][route[0] + 1])
        elif position == len(route):
            # Insert at end
            return (self.distance_matrix[route[-1] + 1][location + 1] + 
                   self.distance_matrix[location + 1][0] - 
                   self.distance_matrix[route[-1] + 1][0])
        else:
            # Insert in middle
            prev_loc = route[position - 1]
            next_loc = route[position]
            return (self.distance_matrix[prev_loc + 1][location + 1] + 
                   self.distance_matrix[location + 1][next_loc + 1] - 
                   self.distance_matrix[prev_loc + 1][next_loc + 1])
    
    def _calculate_total_distance(self, routes: Dict[int, List[int]]) -> float:
        """Calculate total distance for all routes"""
        total = 0.0
        
        for truck_id, route in routes.items():
            if not route:
                continue
            
            # From depot to first location
            total += self.distance_matrix[0][route[0] + 1]
            
            # Between consecutive locations
            for i in range(len(route) - 1):
                total += self.distance_matrix[route[i] + 1][route[i+1] + 1]
            
            # From last location back to depot
            total += self.distance_matrix[route[-1] + 1][0]
        
        return total
    
    def _check_time_windows(self, routes: Dict[int, List[int]]) -> bool:
        """Check if all time windows are satisfied"""
        for truck_id, route in routes.items():
            current_time = 0.0
            current_pos = 0  # Start at depot
            
            for loc_idx in route:
                # Travel time to location
                travel_time = self.distance_matrix[current_pos][loc_idx + 1] / self.avg_speed
                current_time += travel_time
                
                # Check time window
                location = self.locations[loc_idx]
                if current_time > location.time_window_end:
                    return False
                
                # Wait if arrived too early
                if current_time < location.time_window_start:
                    current_time = location.time_window_start
                
                # Service time (assume 10 minutes per location)
                current_time += 10/60  # Convert to hours
                current_pos = loc_idx + 1
        
        return True
    
    def _check_feasibility(self, routes: Dict[int, List[int]]) -> bool:
        """Check if solution is feasible"""
        # Check all locations are visited
        visited = set()
        for route in routes.values():
            visited.update(route)
        
        if len(visited) != self.n_locations:
            return False
        
        # Check capacity constraints
        for truck_id, route in routes.items():
            total_demand = sum(self.locations[loc].demand for loc in route)
            if total_demand > self.trucks[truck_id].capacity:
                return False
        
        # Check time windows
        return self._check_time_windows(routes)
    
    def _calculate_load_balance(self, routes: Dict[int, List[int]]) -> float:
        """Calculate load balance score (lower is better)"""
        loads = []
        for truck_id, route in routes.items():
            load = sum(self.locations[loc].demand for loc in route)
            loads.append(load)
        
        if not loads:
            return 0.0
        
        return max(loads) - min(loads) if loads else 0.0
    
    def _generate_random_solution(self) -> List[int]:
        """Generate random chromosome representation"""
        # Chromosome: permutation of locations + truck separators
        locations = list(range(self.n_locations))
        random.shuffle(locations)
        
        # Insert truck separators
        chromosome = []
        truck_idx = 0
        current_load = 0
        
        for loc in locations:
            if current_load + self.locations[loc].demand > self.trucks[truck_idx].capacity:
                if truck_idx < self.n_trucks - 1:
                    chromosome.append(-1)  # Separator
                    truck_idx += 1
                    current_load = 0
            
            chromosome.append(loc)
            current_load += self.locations[loc].demand
        
        return chromosome
    
    def _evaluate_fitness(self, chromosome: List[int]) -> float:
        """Evaluate fitness of chromosome (lower is better)"""
        routes = self._chromosome_to_routes(chromosome)
        distance = self._calculate_total_distance(routes)
        
        # Add penalty for infeasibility
        penalty = 0
        if not self._check_feasibility(routes):
            penalty = 10000
        
        # Add penalty for load imbalance
        balance_penalty = self._calculate_load_balance(routes) * 10
        
        return distance + penalty + balance_penalty
    
    def _chromosome_to_routes(self, chromosome: List[int]) -> Dict[int, List[int]]:
        """Convert chromosome to routes"""
        routes = {i: [] for i in range(self.n_trucks)}
        truck_idx = 0
        
        for gene in chromosome:
            if gene == -1:  # Separator
                truck_idx = min(truck_idx + 1, self.n_trucks - 1)
            else:
                routes[truck_idx].append(gene)
        
        return routes
    
    def _tournament_selection(self, population: List[List[int]], 
                            fitness_scores: List[float],
                            tournament_size: int = 3) -> List[List[int]]:
        """Tournament selection for genetic algorithm"""
        selected = []
        
        for _ in range(len(population)):
            tournament_idx = random.sample(range(len(population)), tournament_size)
            tournament_fitness = [fitness_scores[i] for i in tournament_idx]
            winner_idx = tournament_idx[np.argmin(tournament_fitness)]
            selected.append(population[winner_idx].copy())
        
        return selected
    
    def _crossover(self, parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
        """Order crossover for genetic algorithm"""
        # Simplified crossover - swap subsequences
        size = len(parent1)
        start = random.randint(0, size - 1)
        end = random.randint(start, size - 1)
        
        child1 = parent1.copy()
        child2 = parent2.copy()
        
        # Swap subsequences
        child1[start:end], child2[start:end] = child2[start:end], child1[start:end]
        
        return child1, child2
    
    def _mutate(self, chromosome: List[int], mutation_rate: float = 0.1) -> List[int]:
        """Mutation operator for genetic algorithm"""
        if random.random() < mutation_rate:
            # Swap two random positions
            i, j = random.sample(range(len(chromosome)), 2)
            chromosome[i], chromosome[j] = chromosome[j], chromosome[i]
        
        return chromosome
    
    def _nearest_neighbor_solution(self) -> Dict[int, List[int]]:
        """Generate initial solution using nearest neighbor heuristic"""
        routes = {i: [] for i in range(self.n_trucks)}
        unvisited = set(range(self.n_locations))
        
        for truck_idx in range(self.n_trucks):
            if not unvisited:
                break
            
            current_pos = 0  # Start at depot
            current_load = 0
            truck = self.trucks[truck_idx]
            
            while unvisited:
                # Find nearest unvisited location that fits
                nearest = None
                min_dist = float('inf')
                
                for loc in unvisited:
                    if current_load + self.locations[loc].demand <= truck.capacity:
                        dist = self.distance_matrix[current_pos][loc + 1]
                        if dist < min_dist:
                            min_dist = dist
                            nearest = loc
                
                if nearest is None:
                    break
                
                routes[truck_idx].append(nearest)
                unvisited.remove(nearest)
                current_load += self.locations[nearest].demand
                current_pos = nearest + 1
        
        return routes
    
    def _generate_neighbor(self, solution: Dict[int, List[int]]) -> Dict[int, List[int]]:
        """Generate neighbor solution for simulated annealing"""
        neighbor = {k: v.copy() for k, v in solution.items()}
        
        # Random neighborhood operation
        operation = random.choice(['swap', 'relocate', '2-opt'])
        
        if operation == 'swap':
            # Swap two locations
            trucks_with_routes = [k for k, v in neighbor.items() if len(v) > 0]
            if len(trucks_with_routes) >= 2:
                truck1, truck2 = random.sample(trucks_with_routes, 2)
                if neighbor[truck1] and neighbor[truck2]:
                    idx1 = random.randint(0, len(neighbor[truck1]) - 1)
                    idx2 = random.randint(0, len(neighbor[truck2]) - 1)
                    neighbor[truck1][idx1], neighbor[truck2][idx2] = \
                        neighbor[truck2][idx2], neighbor[truck1][idx1]
        
        elif operation == 'relocate':
            # Move location to different truck
            trucks_with_routes = [k for k, v in neighbor.items() if len(v) > 0]
            if trucks_with_routes:
                from_truck = random.choice(trucks_with_routes)
                to_truck = random.choice(list(neighbor.keys()))
                if neighbor[from_truck] and from_truck != to_truck:
                    idx = random.randint(0, len(neighbor[from_truck]) - 1)
                    location = neighbor[from_truck].pop(idx)
                    neighbor[to_truck].append(location)
        
        elif operation == '2-opt':
            # 2-opt within a route
            truck = random.choice([k for k, v in neighbor.items() if len(v) > 3])
            if truck is not None:
                route = neighbor[truck]
                i = random.randint(0, len(route) - 2)
                j = random.randint(i + 1, len(route) - 1)
                route[i:j+1] = route[i:j+1][::-1]
        
        return neighbor
    
    def visualize_solution(self, solution: Solution, save_path: Optional[str] = None):
        """Visualize the routing solution"""
        plt.figure(figsize=(12, 10))
        
        # Plot depot
        plt.scatter(self.depot[0], self.depot[1], c='black', s=200, 
                   marker='s', label='Depot', zorder=5)
        
        # Plot locations
        for loc in self.locations:
            plt.scatter(loc.x, loc.y, c='red', s=100, zorder=4)
            plt.annotate(f'{loc.id}\n({loc.demand})', 
                        (loc.x, loc.y), fontsize=8, ha='center')
        
        # Plot routes
        colors = plt.cm.rainbow(np.linspace(0, 1, self.n_trucks))
        
        for truck_idx, route in solution.routes.items():
            if not route:
                continue
            
            color = colors[truck_idx]
            
            # Plot route
            route_x = [self.depot[0]]
            route_y = [self.depot[1]]
            
            for loc_idx in route:
                loc = self.locations[loc_idx]
                route_x.append(loc.x)
                route_y.append(loc.y)
            
            route_x.append(self.depot[0])
            route_y.append(self.depot[1])
            
            plt.plot(route_x, route_y, color=color, linewidth=2, 
                    marker='o', markersize=6, 
                    label=f'Truck {truck_idx} ({len(route)} stops)')
        
        plt.title(f'Vehicle Routing Solution\nTotal Distance: {solution.total_distance:.2f} km')
        plt.xlabel('X Coordinate (km)')
        plt.ylabel('Y Coordinate (km)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def get_complexity_analysis(self) -> Dict[str, str]:
        """Return complexity analysis for each algorithm"""
        return {
            "Clarke-Wright Savings": {
                "Time": "O(n² log n)",
                "Space": "O(n²)",
                "Description": "Efficient constructive heuristic"
            },
            "Genetic Algorithm": {
                "Time": "O(g × p × n²)",
                "Space": "O(p × n)",
                "Description": "Population-based metaheuristic"
            },
            "Simulated Annealing": {
                "Time": "O(iterations × n)",
                "Space": "O(n)",
                "Description": "Local search metaheuristic"
            },
            "Nearest Neighbor": {
                "Time": "O(n²)",
                "Space": "O(n)",
                "Description": "Simple greedy heuristic"
            }
        }
    
    def get_approximation_bounds(self) -> Dict[str, str]:
        """Return theoretical approximation bounds"""
        return {
            "Clarke-Wright": "No fixed bound, typically 10-15% from optimal",
            "Genetic Algorithm": "No theoretical bound, depends on parameters",
            "Simulated Annealing": "Probabilistic convergence to optimal as T→0",
            "Nearest Neighbor": "At most ⌈log n⌉ times optimal for metric TSP",
            "General VRPTW": "Best known approximation ratio is O(log n)"
        }


def generate_test_instance(n_locations: int = 20, n_trucks: int = 4,
                          area_size: float = 100.0) -> Tuple[List[Location], List[Truck]]:
    """Generate a test instance for the VRP problem"""
    random.seed(42)  # For reproducibility
    
    # Generate random locations
    locations = []
    for i in range(n_locations):
        x = random.uniform(0, area_size)
        y = random.uniform(0, area_size)
        demand = random.randint(5, 15)
        
        # Generate 2-hour time windows between 8 AM and 6 PM
        start_hour = random.uniform(8, 16)  # 8 AM to 4 PM
        end_hour = min(start_hour + 2, 18)  # Cap at 6 PM
        
        locations.append(Location(
            id=i,
            x=x,
            y=y,
            demand=demand,
            time_window_start=start_hour,
            time_window_end=end_hour
        ))
    
    # Create trucks with specified capacities
    capacities = [50, 40, 45, 55][:n_trucks]
    trucks = [Truck(id=i, capacity=cap) for i, cap in enumerate(capacities)]
    
    return locations, trucks


def compare_algorithms(optimizer: VehicleRoutingOptimizer) -> Dict[str, Solution]:
    """Compare different algorithms on the same instance"""
    results = {}
    
    print("Running algorithm comparison...")
    
    # Clarke-Wright Savings
    print("\n1. Clarke-Wright Savings Algorithm")
    cw_solution = optimizer.solve_clarke_wright_savings()
    results['Clarke-Wright'] = cw_solution
    print(f"   Distance: {cw_solution.total_distance:.2f} km")
    print(f"   Time: {cw_solution.computation_time:.3f} seconds")
    print(f"   Feasible: {cw_solution.feasible}")
    
    # Genetic Algorithm
    print("\n2. Genetic Algorithm")
    ga_solution = optimizer.solve_genetic_algorithm(population_size=50, generations=200)
    results['Genetic'] = ga_solution
    print(f"   Distance: {ga_solution.total_distance:.2f} km")
    print(f"   Time: {ga_solution.computation_time:.3f} seconds")
    print(f"   Feasible: {ga_solution.feasible}")
    
    # Simulated Annealing
    print("\n3. Simulated Annealing")
    sa_solution = optimizer.solve_simulated_annealing(iterations=5000)
    results['Simulated Annealing'] = sa_solution
    print(f"   Distance: {sa_solution.total_distance:.2f} km")
    print(f"   Time: {sa_solution.computation_time:.3f} seconds")
    print(f"   Feasible: {sa_solution.feasible}")
    
    return results


# Example usage and demonstration
if __name__ == "__main__":
    # Generate test instance
    print("Generating test instance...")
    locations, trucks = generate_test_instance(n_locations=20, n_trucks=4)
    
    # Create optimizer
    optimizer = VehicleRoutingOptimizer(locations, trucks, avg_speed=30.0)
    
    # Print problem statistics
    total_demand = sum(loc.demand for loc in locations)
    total_capacity = sum(truck.capacity for truck in trucks)
    print(f"\nProblem Statistics:")
    print(f"  Locations: {len(locations)}")
    print(f"  Trucks: {len(trucks)}")
    print(f"  Total demand: {total_demand}")
    print(f"  Total capacity: {total_capacity}")
    print(f"  Utilization: {total_demand/total_capacity:.1%}")
    
    # Prove NP-hardness
    print("\n" + "="*60)
    print("NP-Hardness Proof:")
    print("="*60)
    print(optimizer.prove_np_hardness())
    
    # Compare algorithms
    print("\n" + "="*60)
    print("Algorithm Comparison:")
    print("="*60)
    results = compare_algorithms(optimizer)
    
    # Find best solution
    best_algo = min(results.items(), key=lambda x: x[1].total_distance)
    print(f"\nBest algorithm: {best_algo[0]} with distance {best_algo[1].total_distance:.2f} km")
    
    # Visualize best solution
    print("\nVisualizing best solution...")
    optimizer.visualize_solution(best_algo[1], save_path='vrp_solution.png')
    
    # Print complexity analysis
    print("\n" + "="*60)
    print("Complexity Analysis:")
    print("="*60)
    for algo, complexity in optimizer.get_complexity_analysis().items():
        print(f"\n{algo}:")
        for key, value in complexity.items():
            print(f"  {key}: {value}")
    
    # Print approximation bounds
    print("\n" + "="*60)
    print("Approximation Bounds:")
    print("="*60)
    for algo, bound in optimizer.get_approximation_bounds().items():
        print(f"  {algo}: {bound}")