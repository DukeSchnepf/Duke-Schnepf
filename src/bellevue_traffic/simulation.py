"""
Main traffic simulation engine
Coordinates all components and runs the simulation
"""

import simpy
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import random

from .vehicles import Vehicle, Car, Bus, Truck, Motorcycle, VehicleType
from .road_network import BellevueRoadNetwork
from .traffic_signals import TrafficSignal, SignalController
from .traffic_patterns import TrafficPatternGenerator, DayOfWeek


class TrafficSimulation:
    """
    Main traffic simulation class
    Manages the entire simulation using SimPy
    """

    def __init__(
        self,
        duration: float = 3600.0,  # seconds (default 1 hour)
        time_step: float = 1.0,  # seconds
        start_hour: float = 7.0,  # 7 AM
        day_of_week: DayOfWeek = DayOfWeek.WEEKDAY,
        seed: Optional[int] = None
    ):
        """
        Initialize traffic simulation

        Args:
            duration: Simulation duration in seconds
            time_step: Simulation time step in seconds
            start_hour: Starting hour of day (0-24)
            day_of_week: Day of week for traffic patterns
            seed: Random seed for reproducibility
        """
        self.env = simpy.Environment()
        self.duration = duration
        self.time_step = time_step
        self.start_hour = start_hour
        self.day_of_week = day_of_week

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        # Components
        self.network = BellevueRoadNetwork()
        self.signal_controller = SignalController(self.env)
        self.pattern_generator = TrafficPatternGenerator(seed=seed)

        # Vehicle tracking
        self.vehicles: Dict[int, Vehicle] = {}
        self.next_vehicle_id = 0
        self.completed_vehicles: List[Vehicle] = []

        # Edge occupancy (for traffic flow)
        self.edge_vehicles: Dict[Tuple, List[Vehicle]] = defaultdict(list)

        # Simulation statistics
        self.stats = {
            'vehicles_spawned': 0,
            'vehicles_completed': 0,
            'total_travel_time': 0.0,
            'total_distance': 0.0,
            'total_stops': 0,
            'congestion_events': 0
        }

        # Snapshot storage for visualization
        self.snapshots = []
        self.snapshot_interval = 30.0  # seconds

    def setup(self):
        """Setup simulation components"""
        print("Setting up simulation...")

        # Load road network
        print("Loading road network...")
        self.network.load_network(use_cache=True)

        # Setup traffic signals at major intersections
        print("Setting up traffic signals...")
        self._setup_signals()

        print("Setup complete!")

    def _setup_signals(self):
        """Setup traffic signals at key intersections"""
        # Get nodes for signal placement
        # For demo network, place signals at grid intersections
        # For real network, would identify major intersections

        signal_nodes = []

        # Sample some nodes for signals (every 3rd node in demo network)
        for i, node_id in enumerate(self.network.graph.nodes()):
            if i % 5 == 0:  # Place signals at some intersections
                signal_nodes.append(node_id)

        # Create signals
        for i, node_id in enumerate(signal_nodes[:20]):  # Limit to 20 signals
            position = self.network.get_node_position(node_id)

            # Vary timing based on location
            if i % 2 == 0:
                # Major intersection
                signal = self.signal_controller.create_standard_signal(
                    signal_id=i,
                    node_id=node_id,
                    position=position,
                    major_street_time=60.0,
                    minor_street_time=30.0
                )
            else:
                # Minor intersection
                signal = self.signal_controller.create_standard_signal(
                    signal_id=i,
                    node_id=node_id,
                    position=position,
                    major_street_time=45.0,
                    minor_street_time=25.0
                )

        print(f"Created {len(self.signal_controller.signals)} traffic signals")

    def run(self):
        """Run the simulation"""
        print(f"Starting simulation (duration: {self.duration}s, {self.duration/3600:.1f}h)...")

        # Start processes
        self.env.process(self._vehicle_generator())
        self.env.process(self._update_signals())
        self.env.process(self._update_vehicles())
        self.env.process(self._record_snapshots())

        # Run simulation
        self.env.run(until=self.duration)

        print("Simulation complete!")
        self._print_statistics()

    def _vehicle_generator(self):
        """Process that generates vehicles based on traffic patterns"""
        while True:
            # Calculate current hour
            current_hour = (self.start_hour + self.env.now / 3600) % 24

            # Get spawn rate for current time
            spawn_rate = self.pattern_generator.get_spawn_rate(current_hour, self.day_of_week)
            vehicle_mix = self.pattern_generator.get_vehicle_mix(current_hour, self.day_of_week)

            # Time until next vehicle (exponential distribution)
            inter_arrival_time = np.random.exponential(60.0 / spawn_rate)

            yield self.env.timeout(inter_arrival_time)

            # Determine vehicle type
            vehicle_type = random.choices(
                list(vehicle_mix.keys()),
                weights=list(vehicle_mix.values())
            )[0]

            # Generate origin-destination
            origin, destination = self.pattern_generator.generate_od_pair(current_hour, self.day_of_week)

            # Create vehicle
            self._spawn_vehicle(vehicle_type, origin, destination)

    def _spawn_vehicle(self, vehicle_type: str, origin: Tuple[float, float],
                       destination: Tuple[float, float]):
        """
        Spawn a new vehicle

        Args:
            vehicle_type: Type of vehicle ('car', 'bus', 'truck', 'motorcycle')
            origin: Origin coordinates (lat, lon)
            destination: Destination coordinates (lat, lon)
        """
        vehicle_id = self.next_vehicle_id
        self.next_vehicle_id += 1

        # Find route
        route = self.network.find_route(origin, destination)

        if not route or len(route) < 2:
            return  # Skip if no valid route

        # Create vehicle based on type
        if vehicle_type == 'car':
            vehicle = Car(vehicle_id, self.env.now, origin, destination, route)
        elif vehicle_type == 'bus':
            vehicle = Bus(vehicle_id, self.env.now, origin, destination, route)
        elif vehicle_type == 'truck':
            vehicle = Truck(vehicle_id, self.env.now, origin, destination, route)
        elif vehicle_type == 'motorcycle':
            vehicle = Motorcycle(vehicle_id, self.env.now, origin, destination, route)
        else:
            vehicle = Car(vehicle_id, self.env.now, origin, destination, route)

        # Set initial edge
        if len(route) >= 2:
            vehicle.current_edge = (route[0], route[1], 0)
            self.edge_vehicles[vehicle.current_edge].append(vehicle)

        self.vehicles[vehicle_id] = vehicle
        self.stats['vehicles_spawned'] += 1

    def _update_signals(self):
        """Process that updates all traffic signals"""
        while True:
            yield self.env.timeout(self.time_step)
            self.signal_controller.update_all_signals(self.time_step)

    def _update_vehicles(self):
        """Process that updates all vehicle positions and states"""
        while True:
            yield self.env.timeout(self.time_step)

            # Update each vehicle
            vehicles_to_remove = []

            for vehicle_id, vehicle in list(self.vehicles.items()):
                # Check if vehicle has completed route
                if vehicle.completed:
                    vehicles_to_remove.append(vehicle_id)
                    continue

                # Update vehicle movement
                self._update_vehicle_position(vehicle)

            # Remove completed vehicles
            for vehicle_id in vehicles_to_remove:
                vehicle = self.vehicles.pop(vehicle_id)
                self.completed_vehicles.append(vehicle)
                self.stats['vehicles_completed'] += 1
                self.stats['total_travel_time'] += vehicle.stats.total_time
                self.stats['total_distance'] += vehicle.stats.total_distance
                self.stats['total_stops'] += vehicle.stats.stops

    def _update_vehicle_position(self, vehicle: Vehicle):
        """
        Update a single vehicle's position

        Args:
            vehicle: Vehicle to update
        """
        if not vehicle.route or len(vehicle.route) < 2:
            vehicle.completed = True
            return

        # Current edge
        current_edge = vehicle.current_edge
        if current_edge is None:
            vehicle.completed = True
            return

        u, v, key = current_edge

        # Get edge info
        edge_info = self.network.get_edge_info(u, v, key)
        speed_limit = edge_info['speed_limit']
        edge_length = edge_info['length']

        # Check for traffic signal at next node
        signal = self.signal_controller.get_signal_at_node(v)
        can_proceed = True

        if signal is not None:
            # Simplified: assume approaching from 'north'
            approach = 'north'
            # Distance to signal (simplified)
            distance_to_signal = edge_length * 0.5  # Rough estimate

            can_proceed = signal.can_vehicle_proceed(approach, distance_to_signal, vehicle.speed)

        # Find leader vehicle on same edge
        leader_distance = None
        leader_speed = None

        edge_vehicles = self.edge_vehicles[current_edge]
        vehicle_index = edge_vehicles.index(vehicle) if vehicle in edge_vehicles else -1

        if vehicle_index > 0:
            leader = edge_vehicles[vehicle_index - 1]
            # Simplified spacing calculation
            leader_distance = 50.0  # Placeholder
            leader_speed = leader.speed

        # Calculate desired speed
        if not can_proceed:
            desired_speed = 0.0
            vehicle.waiting_at_signal = True
        else:
            desired_speed = speed_limit
            vehicle.waiting_at_signal = False

        # Calculate acceleration
        acceleration = vehicle.calculate_acceleration(leader_distance, leader_speed, desired_speed)

        # Update speed
        new_speed = max(0.0, vehicle.speed + acceleration * self.time_step)
        vehicle.speed = new_speed
        vehicle.acceleration = acceleration

        # Update position (simplified - just move along route)
        distance_traveled = vehicle.speed * self.time_step

        # Check if reached next node
        if distance_traveled >= edge_length * 0.5:  # Simplified threshold
            # Move to next edge
            current_route_index = vehicle.route.index(v) if v in vehicle.route else -1

            if current_route_index >= 0 and current_route_index < len(vehicle.route) - 1:
                next_node = vehicle.route[current_route_index + 1]

                # Remove from current edge
                if vehicle in self.edge_vehicles[current_edge]:
                    self.edge_vehicles[current_edge].remove(vehicle)

                # Move to next edge
                new_edge = (v, next_node, 0)
                vehicle.current_edge = new_edge
                self.edge_vehicles[new_edge].append(vehicle)

                # Update position
                new_pos = self.network.get_node_position(v)
                vehicle.update_position(new_pos, self.time_step)
            else:
                # Reached destination
                vehicle.completed = True
                if vehicle in self.edge_vehicles[current_edge]:
                    self.edge_vehicles[current_edge].remove(vehicle)
        else:
            # Update stats without changing edge
            vehicle.stats.total_time += self.time_step

    def _record_snapshots(self):
        """Process that records periodic snapshots for visualization"""
        while True:
            yield self.env.timeout(self.snapshot_interval)

            snapshot = {
                'time': self.env.now,
                'vehicles': []
            }

            for vehicle in self.vehicles.values():
                snapshot['vehicles'].append({
                    'id': vehicle.id,
                    'type': vehicle.type.value,
                    'position': vehicle.position,
                    'speed': vehicle.speed,
                    'waiting': vehicle.waiting_at_signal
                })

            self.snapshots.append(snapshot)

    def _print_statistics(self):
        """Print simulation statistics"""
        print("\n" + "="*50)
        print("SIMULATION STATISTICS")
        print("="*50)
        print(f"Duration: {self.duration/3600:.2f} hours")
        print(f"Vehicles spawned: {self.stats['vehicles_spawned']}")
        print(f"Vehicles completed: {self.stats['vehicles_completed']}")

        if self.stats['vehicles_completed'] > 0:
            avg_travel_time = self.stats['total_travel_time'] / self.stats['vehicles_completed']
            avg_distance = self.stats['total_distance'] / self.stats['vehicles_completed']
            avg_speed = avg_distance / avg_travel_time if avg_travel_time > 0 else 0

            print(f"Average travel time: {avg_travel_time:.1f} seconds ({avg_travel_time/60:.1f} minutes)")
            print(f"Average distance: {avg_distance:.1f} meters ({avg_distance/1000:.2f} km)")
            print(f"Average speed: {avg_speed*3.6:.1f} km/h")

        print(f"Active vehicles: {len(self.vehicles)}")
        print(f"Snapshots recorded: {len(self.snapshots)}")
        print("="*50)

    def get_statistics(self) -> Dict:
        """
        Get detailed statistics

        Returns:
            Dictionary of statistics
        """
        stats = self.stats.copy()

        if stats['vehicles_completed'] > 0:
            stats['avg_travel_time'] = stats['total_travel_time'] / stats['vehicles_completed']
            stats['avg_distance'] = stats['total_distance'] / stats['vehicles_completed']
            stats['avg_speed'] = stats['avg_distance'] / stats['avg_travel_time'] if stats['avg_travel_time'] > 0 else 0
        else:
            stats['avg_travel_time'] = 0
            stats['avg_distance'] = 0
            stats['avg_speed'] = 0

        # Add signal statistics
        signal_stats = self.signal_controller.get_statistics()
        stats.update(signal_stats)

        return stats

    def get_snapshots(self) -> List[Dict]:
        """Get recorded snapshots for visualization"""
        return self.snapshots

    def get_edge_speeds(self) -> Dict[Tuple, float]:
        """
        Get average speed on each edge

        Returns:
            Dictionary of edge -> average speed (m/s)
        """
        edge_speeds = {}

        for edge, vehicles in self.edge_vehicles.items():
            if vehicles:
                avg_speed = np.mean([v.speed for v in vehicles])
                edge_speeds[edge] = avg_speed
            else:
                edge_info = self.network.get_edge_info(edge[0], edge[1], edge[2])
                edge_speeds[edge] = edge_info['speed_limit']

        return edge_speeds

    def get_congestion_level(self, edge: Tuple[int, int, int]) -> float:
        """
        Get congestion level for an edge (0-1)

        Args:
            edge: Edge tuple (u, v, key)

        Returns:
            Congestion level (0 = free flow, 1 = gridlock)
        """
        edge_info = self.network.get_edge_info(edge[0], edge[1], edge[2])
        speed_limit = edge_info['speed_limit']
        num_lanes = edge_info['lanes']
        edge_length = edge_info['length']

        # Capacity (simplified): vehicles that fit on edge
        capacity = (edge_length / 7.0) * num_lanes  # Assume 7m per vehicle

        # Current occupancy
        occupancy = len(self.edge_vehicles[edge])

        # Congestion based on occupancy
        if capacity > 0:
            density_ratio = occupancy / capacity
        else:
            density_ratio = 0

        # Also consider speed
        if edge in self.edge_vehicles and self.edge_vehicles[edge]:
            avg_speed = np.mean([v.speed for v in self.edge_vehicles[edge]])
            speed_ratio = 1.0 - (avg_speed / speed_limit) if speed_limit > 0 else 0
        else:
            speed_ratio = 0

        # Combine density and speed
        congestion = 0.6 * density_ratio + 0.4 * speed_ratio

        return min(1.0, congestion)
