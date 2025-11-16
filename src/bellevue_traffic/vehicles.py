"""
Vehicle classes for the traffic simulation
Includes cars, buses, and trucks with different behaviors
"""

import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Tuple


class VehicleType(Enum):
    """Types of vehicles in the simulation"""
    CAR = "car"
    BUS = "bus"
    TRUCK = "truck"
    MOTORCYCLE = "motorcycle"


@dataclass
class VehicleStats:
    """Statistics for tracking vehicle performance"""
    total_distance: float = 0.0
    total_time: float = 0.0
    stops: int = 0
    lane_changes: int = 0
    average_speed: float = 0.0
    max_speed: float = 0.0
    time_in_congestion: float = 0.0


class Vehicle:
    """
    Base class for all vehicles in the simulation
    """

    def __init__(
        self,
        vehicle_id: int,
        vehicle_type: VehicleType,
        spawn_time: float,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        route: Optional[List] = None
    ):
        self.id = vehicle_id
        self.type = vehicle_type
        self.spawn_time = spawn_time
        self.origin = origin
        self.destination = destination
        self.route = route or []

        # Current state
        self.position = origin
        self.current_edge = None
        self.current_lane = 0
        self.speed = 0.0
        self.acceleration = 0.0

        # Vehicle characteristics (set by subclasses)
        self.max_speed = 0.0
        self.max_acceleration = 0.0
        self.max_deceleration = 0.0
        self.length = 0.0
        self.width = 0.0

        # Behavior parameters
        self.desired_time_headway = 1.5  # seconds
        self.min_spacing = 2.0  # meters
        self.politeness = 0.5  # 0-1, affects lane changing
        self.aggressiveness = 0.5  # 0-1, affects acceleration

        # Statistics
        self.stats = VehicleStats()

        # State flags
        self.completed = False
        self.waiting_at_signal = False

    def update_position(self, new_position: Tuple[float, float], time_step: float):
        """Update vehicle position and calculate statistics"""
        distance = np.linalg.norm(np.array(new_position) - np.array(self.position))
        self.position = new_position
        self.stats.total_distance += distance
        self.stats.total_time += time_step

        if self.stats.total_time > 0:
            self.stats.average_speed = self.stats.total_distance / self.stats.total_time

        if self.speed > self.stats.max_speed:
            self.stats.max_speed = self.speed

    def calculate_acceleration(
        self,
        leader_distance: Optional[float],
        leader_speed: Optional[float],
        desired_speed: float
    ) -> float:
        """
        Calculate acceleration using Intelligent Driver Model (IDM)

        Args:
            leader_distance: Distance to vehicle ahead (None if no leader)
            leader_speed: Speed of vehicle ahead
            desired_speed: Desired speed on current road

        Returns:
            Calculated acceleration
        """
        # Free-flow acceleration
        accel = self.max_acceleration * (
            1 - (self.speed / desired_speed) ** 4
        )

        # If there's a leader, account for spacing
        if leader_distance is not None and leader_speed is not None:
            desired_spacing = self.min_spacing + max(
                0,
                self.speed * self.desired_time_headway +
                (self.speed * (self.speed - leader_speed)) /
                (2 * np.sqrt(abs(self.max_acceleration * self.max_deceleration)))
            )

            if leader_distance > 0:
                accel -= self.max_acceleration * (desired_spacing / leader_distance) ** 2

        # Apply aggressiveness factor
        accel *= (0.5 + 0.5 * self.aggressiveness)

        return np.clip(accel, -self.max_deceleration, self.max_acceleration)

    def should_change_lane(
        self,
        current_lane_speed: float,
        target_lane_speed: float,
        target_lane_safe: bool
    ) -> bool:
        """
        Determine if vehicle should change lanes using MOBIL model

        Args:
            current_lane_speed: Average speed in current lane
            target_lane_speed: Average speed in target lane
            target_lane_safe: Whether lane change is safe

        Returns:
            True if should change lanes
        """
        if not target_lane_safe:
            return False

        # Advantage threshold (m/s) - adjusted by politeness
        threshold = 0.5 * (1 - self.politeness)

        # Speed advantage of target lane
        advantage = target_lane_speed - current_lane_speed

        # More aggressive drivers change lanes more readily
        advantage *= (0.5 + 0.5 * self.aggressiveness)

        return advantage > threshold

    def __repr__(self):
        return f"{self.type.value.capitalize()}(id={self.id}, speed={self.speed:.1f})"


class Car(Vehicle):
    """Standard passenger car"""

    def __init__(self, vehicle_id: int, spawn_time: float, origin: Tuple[float, float],
                 destination: Tuple[float, float], route: Optional[List] = None):
        super().__init__(vehicle_id, VehicleType.CAR, spawn_time, origin, destination, route)

        # Car-specific characteristics
        self.max_speed = 120 / 3.6  # 120 km/h to m/s
        self.max_acceleration = 2.5  # m/s²
        self.max_deceleration = 4.5  # m/s²
        self.length = 4.5  # meters
        self.width = 2.0  # meters

        # Randomize behavior slightly
        self.aggressiveness = np.clip(np.random.normal(0.5, 0.15), 0.2, 0.8)
        self.politeness = np.clip(np.random.normal(0.5, 0.15), 0.2, 0.8)


class Bus(Vehicle):
    """Public transit bus"""

    def __init__(self, vehicle_id: int, spawn_time: float, origin: Tuple[float, float],
                 destination: Tuple[float, float], route: Optional[List] = None,
                 stops: Optional[List] = None):
        super().__init__(vehicle_id, VehicleType.BUS, spawn_time, origin, destination, route)

        # Bus-specific characteristics
        self.max_speed = 90 / 3.6  # 90 km/h to m/s
        self.max_acceleration = 1.2  # m/s²
        self.max_deceleration = 3.0  # m/s²
        self.length = 12.0  # meters
        self.width = 2.5  # meters

        # Buses are generally less aggressive and more polite
        self.aggressiveness = np.clip(np.random.normal(0.3, 0.1), 0.1, 0.5)
        self.politeness = np.clip(np.random.normal(0.7, 0.1), 0.5, 0.9)

        # Bus-specific attributes
        self.bus_stops = stops or []
        self.current_stop_index = 0
        self.stop_duration = 30  # seconds
        self.passengers = 0


class Truck(Vehicle):
    """Commercial truck"""

    def __init__(self, vehicle_id: int, spawn_time: float, origin: Tuple[float, float],
                 destination: Tuple[float, float], route: Optional[List] = None):
        super().__init__(vehicle_id, VehicleType.TRUCK, spawn_time, origin, destination, route)

        # Truck-specific characteristics
        self.max_speed = 100 / 3.6  # 100 km/h to m/s
        self.max_acceleration = 0.8  # m/s²
        self.max_deceleration = 2.5  # m/s²
        self.length = 15.0  # meters
        self.width = 2.5  # meters

        # Trucks are generally less aggressive
        self.aggressiveness = np.clip(np.random.normal(0.25, 0.1), 0.1, 0.4)
        self.politeness = np.clip(np.random.normal(0.6, 0.1), 0.4, 0.8)

        # Truck-specific attributes
        self.cargo_weight = np.random.uniform(5000, 20000)  # kg


class Motorcycle(Vehicle):
    """Motorcycle - more agile than cars"""

    def __init__(self, vehicle_id: int, spawn_time: float, origin: Tuple[float, float],
                 destination: Tuple[float, float], route: Optional[List] = None):
        super().__init__(vehicle_id, VehicleType.MOTORCYCLE, spawn_time, origin, destination, route)

        # Motorcycle-specific characteristics
        self.max_speed = 140 / 3.6  # 140 km/h to m/s
        self.max_acceleration = 3.5  # m/s²
        self.max_deceleration = 5.0  # m/s²
        self.length = 2.0  # meters
        self.width = 0.8  # meters

        # Motorcycles tend to be more aggressive
        self.aggressiveness = np.clip(np.random.normal(0.7, 0.15), 0.4, 0.95)
        self.politeness = np.clip(np.random.normal(0.4, 0.15), 0.2, 0.7)
