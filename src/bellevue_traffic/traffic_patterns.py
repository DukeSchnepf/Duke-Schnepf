"""
Traffic pattern generation for different times of day
Implements realistic demand patterns for Bellevue
"""

import numpy as np
from typing import Dict, Tuple, List, Optional
from enum import Enum
from dataclasses import dataclass
import random


class TimeOfDay(Enum):
    """Time periods with different traffic patterns"""
    EARLY_MORNING = "early_morning"  # 5:00-7:00
    MORNING_RUSH = "morning_rush"    # 7:00-9:00
    MIDDAY = "midday"                # 9:00-16:00
    EVENING_RUSH = "evening_rush"    # 16:00-19:00
    EVENING = "evening"              # 19:00-22:00
    NIGHT = "night"                  # 22:00-5:00


class DayOfWeek(Enum):
    """Day of week affects traffic patterns"""
    WEEKDAY = "weekday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


@dataclass
class TrafficDemand:
    """Represents traffic demand parameters"""
    base_flow_rate: float  # vehicles per hour
    truck_percentage: float  # 0-1
    bus_percentage: float  # 0-1
    trip_purposes: Dict[str, float]  # purpose -> percentage


class TrafficPatternGenerator:
    """
    Generates realistic traffic patterns for Bellevue
    """

    # Origin-Destination pairs with their relative importance
    OD_PATTERNS = {
        'residential_to_downtown': 0.25,
        'residential_to_microsoft': 0.20,
        'downtown_to_residential': 0.15,
        'microsoft_to_residential': 0.15,
        'external_to_downtown': 0.10,
        'downtown_to_external': 0.10,
        'internal_downtown': 0.05
    }

    # Bellevue zones
    ZONES = {
        'downtown': [(47.610, -122.202), (47.612, -122.200), (47.608, -122.204)],
        'microsoft_campus': [(47.642, -122.139), (47.644, -122.137), (47.640, -122.141)],
        'residential_north': [(47.630, -122.170), (47.632, -122.168), (47.628, -122.172)],
        'residential_south': [(47.590, -122.190), (47.592, -122.188), (47.588, -122.192)],
        'bellevue_square': [(47.616, -122.204), (47.618, -122.202), (47.614, -122.206)],
        'wilburton': [(47.609, -122.176), (47.611, -122.174), (47.607, -122.178)],
    }

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize pattern generator

        Args:
            seed: Random seed for reproducibility
        """
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)

        self.current_time = 7.0  # Start at 7:00 AM
        self.current_day = DayOfWeek.WEEKDAY

    def get_time_period(self, hour: float) -> TimeOfDay:
        """
        Determine time period based on hour

        Args:
            hour: Hour of day (0-24)

        Returns:
            TimeOfDay enum
        """
        if 5 <= hour < 7:
            return TimeOfDay.EARLY_MORNING
        elif 7 <= hour < 9:
            return TimeOfDay.MORNING_RUSH
        elif 9 <= hour < 16:
            return TimeOfDay.MIDDAY
        elif 16 <= hour < 19:
            return TimeOfDay.EVENING_RUSH
        elif 19 <= hour < 22:
            return TimeOfDay.EVENING
        else:
            return TimeOfDay.NIGHT

    def get_demand_multiplier(self, time_period: TimeOfDay, day: DayOfWeek) -> float:
        """
        Get traffic demand multiplier for time period and day

        Args:
            time_period: Time of day
            day: Day of week

        Returns:
            Multiplier (1.0 = normal, >1.0 = higher demand)
        """
        # Base multipliers by time period
        time_multipliers = {
            TimeOfDay.EARLY_MORNING: 0.3,
            TimeOfDay.MORNING_RUSH: 1.8,
            TimeOfDay.MIDDAY: 0.8,
            TimeOfDay.EVENING_RUSH: 2.0,
            TimeOfDay.EVENING: 0.6,
            TimeOfDay.NIGHT: 0.1
        }

        # Day of week adjustments
        day_multipliers = {
            DayOfWeek.WEEKDAY: 1.0,
            DayOfWeek.SATURDAY: 0.6,
            DayOfWeek.SUNDAY: 0.4
        }

        return time_multipliers[time_period] * day_multipliers[day]

    def get_traffic_demand(self, hour: float, day: DayOfWeek = DayOfWeek.WEEKDAY) -> TrafficDemand:
        """
        Get traffic demand parameters for given time

        Args:
            hour: Hour of day (0-24)
            day: Day of week

        Returns:
            TrafficDemand object
        """
        time_period = self.get_time_period(hour)
        multiplier = self.get_demand_multiplier(time_period, day)

        # Base flow rate (vehicles per hour for entire network)
        base_flow = 2000 * multiplier

        # Truck percentage varies by time
        if time_period in [TimeOfDay.NIGHT, TimeOfDay.EARLY_MORNING]:
            truck_pct = 0.15  # More trucks at night
        elif time_period == TimeOfDay.MIDDAY:
            truck_pct = 0.10
        else:
            truck_pct = 0.05  # Fewer trucks during rush hours

        # Bus percentage
        if day == DayOfWeek.WEEKDAY:
            bus_pct = 0.03
        else:
            bus_pct = 0.01

        # Trip purposes
        if time_period == TimeOfDay.MORNING_RUSH:
            purposes = {
                'commute_to_work': 0.70,
                'school': 0.15,
                'shopping': 0.05,
                'other': 0.10
            }
        elif time_period == TimeOfDay.EVENING_RUSH:
            purposes = {
                'commute_from_work': 0.60,
                'shopping': 0.15,
                'recreation': 0.15,
                'other': 0.10
            }
        elif time_period == TimeOfDay.MIDDAY:
            purposes = {
                'shopping': 0.30,
                'business': 0.25,
                'personal': 0.25,
                'other': 0.20
            }
        else:
            purposes = {
                'other': 0.60,
                'shopping': 0.20,
                'recreation': 0.20
            }

        return TrafficDemand(
            base_flow_rate=base_flow,
            truck_percentage=truck_pct,
            bus_percentage=bus_pct,
            trip_purposes=purposes
        )

    def generate_od_pair(self, hour: float, day: DayOfWeek = DayOfWeek.WEEKDAY) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """
        Generate origin-destination pair based on time and day

        Args:
            hour: Hour of day
            day: Day of week

        Returns:
            Tuple of (origin, destination) coordinates
        """
        time_period = self.get_time_period(hour)

        # Adjust OD patterns based on time
        if time_period == TimeOfDay.MORNING_RUSH:
            # More trips to work areas
            od_weights = {
                'residential_to_downtown': 0.30,
                'residential_to_microsoft': 0.35,
                'external_to_downtown': 0.15,
                'residential_north_to_downtown': 0.10,
                'residential_south_to_downtown': 0.10
            }
        elif time_period == TimeOfDay.EVENING_RUSH:
            # Reverse commute
            od_weights = {
                'downtown_to_residential': 0.30,
                'microsoft_to_residential': 0.35,
                'downtown_to_external': 0.15,
                'downtown_to_residential_north': 0.10,
                'downtown_to_residential_south': 0.10
            }
        elif time_period == TimeOfDay.MIDDAY:
            # More shopping and internal trips
            od_weights = {
                'residential_to_bellevue_square': 0.25,
                'downtown_internal': 0.20,
                'residential_to_downtown': 0.20,
                'downtown_to_residential': 0.20,
                'other': 0.15
            }
        else:
            # Balanced distribution
            od_weights = {
                'residential_to_downtown': 0.25,
                'downtown_to_residential': 0.25,
                'residential_to_bellevue_square': 0.20,
                'downtown_internal': 0.15,
                'other': 0.15
            }

        # Select OD pattern
        pattern = random.choices(
            list(od_weights.keys()),
            weights=list(od_weights.values())
        )[0]

        # Generate specific origin and destination based on pattern
        origin, destination = self._get_od_locations(pattern)

        return origin, destination

    def _get_od_locations(self, pattern: str) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """
        Get specific origin and destination locations for a pattern

        Args:
            pattern: OD pattern name

        Returns:
            (origin, destination) coordinate tuples
        """
        # Map patterns to zones
        pattern_mapping = {
            'residential_to_downtown': ('residential_north', 'downtown'),
            'residential_to_microsoft': ('residential_south', 'microsoft_campus'),
            'downtown_to_residential': ('downtown', 'residential_north'),
            'microsoft_to_residential': ('microsoft_campus', 'residential_south'),
            'residential_to_bellevue_square': ('residential_north', 'bellevue_square'),
            'downtown_internal': ('downtown', 'downtown'),
            'external_to_downtown': ('residential_south', 'downtown'),
            'downtown_to_external': ('downtown', 'residential_south'),
            'residential_north_to_downtown': ('residential_north', 'downtown'),
            'residential_south_to_downtown': ('residential_south', 'downtown'),
            'downtown_to_residential_north': ('downtown', 'residential_north'),
            'downtown_to_residential_south': ('downtown', 'residential_south'),
        }

        # Default to random zones if pattern not found
        if pattern not in pattern_mapping:
            zones = list(self.ZONES.keys())
            origin_zone = random.choice(zones)
            destination_zone = random.choice(zones)
        else:
            origin_zone, destination_zone = pattern_mapping[pattern]

        # Select random point within zones
        origin = random.choice(self.ZONES[origin_zone])
        destination = random.choice(self.ZONES[destination_zone])

        return origin, destination

    def get_spawn_rate(self, hour: float, day: DayOfWeek = DayOfWeek.WEEKDAY) -> float:
        """
        Get vehicle spawn rate (vehicles per minute)

        Args:
            hour: Hour of day
            day: Day of week

        Returns:
            Spawn rate in vehicles per minute
        """
        demand = self.get_traffic_demand(hour, day)
        # Convert hourly rate to per-minute rate
        return demand.base_flow_rate / 60.0

    def get_vehicle_mix(self, hour: float, day: DayOfWeek = DayOfWeek.WEEKDAY) -> Dict[str, float]:
        """
        Get vehicle type distribution

        Args:
            hour: Hour of day
            day: Day of week

        Returns:
            Dictionary of vehicle type -> probability
        """
        demand = self.get_traffic_demand(hour, day)

        car_pct = 1.0 - demand.truck_percentage - demand.bus_percentage
        motorcycle_pct = 0.02  # Small percentage of motorcycles

        # Adjust car percentage to account for motorcycles
        car_pct -= motorcycle_pct

        return {
            'car': car_pct,
            'truck': demand.truck_percentage,
            'bus': demand.bus_percentage,
            'motorcycle': motorcycle_pct
        }

    def simulate_day(self, start_hour: float = 0.0, end_hour: float = 24.0,
                     day: DayOfWeek = DayOfWeek.WEEKDAY) -> List[Dict]:
        """
        Generate traffic events for a full day

        Args:
            start_hour: Starting hour
            end_hour: Ending hour
            day: Day of week

        Returns:
            List of vehicle spawn events
        """
        events = []
        current_time = start_hour

        while current_time < end_hour:
            hour = current_time % 24
            spawn_rate = self.get_spawn_rate(hour, day)
            vehicle_mix = self.get_vehicle_mix(hour, day)

            # Number of vehicles to spawn in this time step (1 minute)
            num_vehicles = int(np.random.poisson(spawn_rate))

            for _ in range(num_vehicles):
                # Determine vehicle type
                vehicle_type = random.choices(
                    list(vehicle_mix.keys()),
                    weights=list(vehicle_mix.values())
                )[0]

                # Generate OD pair
                origin, destination = self.generate_od_pair(hour, day)

                events.append({
                    'time': current_time * 3600,  # Convert to seconds
                    'type': vehicle_type,
                    'origin': origin,
                    'destination': destination
                })

            current_time += 1/60  # Advance by 1 minute

        return events

    def get_hourly_profile(self, day: DayOfWeek = DayOfWeek.WEEKDAY) -> List[float]:
        """
        Get 24-hour traffic volume profile

        Args:
            day: Day of week

        Returns:
            List of 24 hourly volumes (relative to base)
        """
        profile = []
        for hour in range(24):
            time_period = self.get_time_period(hour)
            multiplier = self.get_demand_multiplier(time_period, day)
            profile.append(multiplier)

        return profile
