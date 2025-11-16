"""
Traffic signal system for the simulation
Implements realistic traffic light timing and coordination
"""

import simpy
import numpy as np
from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class SignalState(Enum):
    """Traffic signal states"""
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"


@dataclass
class SignalPhase:
    """
    Represents a single phase of a traffic signal
    """
    name: str
    duration: float  # seconds
    green_approaches: List[str]  # Which approaches get green
    yellow_duration: float = 3.0  # seconds


class TrafficSignal:
    """
    Traffic signal at an intersection
    Manages signal timing and state
    """

    def __init__(
        self,
        signal_id: int,
        node_id: int,
        position: Tuple[float, float],
        phases: List[SignalPhase],
        coordinated: bool = False,
        offset: float = 0.0
    ):
        """
        Initialize traffic signal

        Args:
            signal_id: Unique signal identifier
            node_id: Network node where signal is located
            position: (lat, lon) of signal
            phases: List of signal phases
            coordinated: Whether signal is part of coordinated system
            offset: Time offset for coordination (seconds)
        """
        self.id = signal_id
        self.node_id = node_id
        self.position = position
        self.phases = phases
        self.coordinated = coordinated
        self.offset = offset

        self.current_phase_index = 0
        self.current_state = SignalState.RED
        self.time_in_phase = 0.0
        self.cycle_length = sum(phase.duration + phase.yellow_duration for phase in phases)

        # Queue tracking for adaptive signals
        self.approach_queues = {}  # approach_name -> queue length
        self.vehicles_served = 0
        self.total_delay = 0.0

    def get_current_phase(self) -> SignalPhase:
        """Get the current signal phase"""
        return self.phases[self.current_phase_index]

    def get_state_for_approach(self, approach: str) -> SignalState:
        """
        Get signal state for a specific approach

        Args:
            approach: Approach direction (e.g., 'north', 'south', 'east', 'west')

        Returns:
            Current signal state for that approach
        """
        current_phase = self.get_current_phase()

        if approach in current_phase.green_approaches:
            return self.current_state
        else:
            return SignalState.RED

    def update(self, time_step: float):
        """
        Update signal state

        Args:
            time_step: Time elapsed since last update (seconds)
        """
        self.time_in_phase += time_step
        current_phase = self.get_current_phase()

        # Check if it's time to change state
        if self.current_state == SignalState.GREEN:
            if self.time_in_phase >= current_phase.duration:
                # Switch to yellow
                self.current_state = SignalState.YELLOW
                self.time_in_phase = 0.0

        elif self.current_state == SignalState.YELLOW:
            if self.time_in_phase >= current_phase.yellow_duration:
                # Switch to red and move to next phase
                self.current_state = SignalState.RED
                self.current_phase_index = (self.current_phase_index + 1) % len(self.phases)
                self.time_in_phase = 0.0

        elif self.current_state == SignalState.RED:
            # Brief all-red clearance interval
            if self.time_in_phase >= 1.0:
                self.current_state = SignalState.GREEN
                self.time_in_phase = 0.0

    def is_green_for_approach(self, approach: str) -> bool:
        """Check if signal is green for given approach"""
        return self.get_state_for_approach(approach) == SignalState.GREEN

    def can_vehicle_proceed(self, approach: str, distance_to_signal: float, vehicle_speed: float) -> bool:
        """
        Determine if vehicle can proceed through signal

        Args:
            approach: Approach direction
            distance_to_signal: Distance to signal (meters)
            vehicle_speed: Current vehicle speed (m/s)

        Returns:
            True if vehicle can proceed
        """
        state = self.get_state_for_approach(approach)

        if state == SignalState.GREEN:
            return True
        elif state == SignalState.YELLOW:
            # Can proceed if too close to stop safely
            stopping_distance = (vehicle_speed ** 2) / (2 * 4.5)  # Assuming 4.5 m/s² deceleration
            return distance_to_signal < stopping_distance
        else:
            return False


class SignalController:
    """
    Manages multiple traffic signals
    Handles coordination and adaptive timing
    """

    def __init__(self, env: simpy.Environment):
        """
        Initialize signal controller

        Args:
            env: SimPy environment
        """
        self.env = env
        self.signals: Dict[int, TrafficSignal] = {}

    def add_signal(self, signal: TrafficSignal):
        """Add a signal to the controller"""
        self.signals[signal.node_id] = signal

    def create_standard_signal(
        self,
        signal_id: int,
        node_id: int,
        position: Tuple[float, float],
        major_street_time: float = 60.0,
        minor_street_time: float = 30.0
    ) -> TrafficSignal:
        """
        Create a standard 4-way signal

        Args:
            signal_id: Unique identifier
            node_id: Network node location
            position: (lat, lon)
            major_street_time: Green time for major street (seconds)
            minor_street_time: Green time for minor street (seconds)

        Returns:
            Configured TrafficSignal
        """
        phases = [
            SignalPhase(
                name="NS_Green",
                duration=major_street_time,
                green_approaches=['north', 'south'],
                yellow_duration=3.0
            ),
            SignalPhase(
                name="EW_Green",
                duration=minor_street_time,
                green_approaches=['east', 'west'],
                yellow_duration=3.0
            )
        ]

        signal = TrafficSignal(signal_id, node_id, position, phases)
        self.add_signal(signal)
        return signal

    def create_arterial_signals(
        self,
        nodes: List[int],
        positions: List[Tuple[float, float]],
        green_wave_speed: float = 50 / 3.6,  # m/s (50 km/h)
        spacing: float = 400.0  # meters between signals
    ) -> List[TrafficSignal]:
        """
        Create coordinated signals along an arterial

        Args:
            nodes: List of node IDs where signals should be placed
            positions: List of (lat, lon) positions
            green_wave_speed: Speed for green wave progression
            spacing: Average distance between signals

        Returns:
            List of coordinated signals
        """
        signals = []
        base_green_time = 60.0

        for i, (node_id, position) in enumerate(zip(nodes, positions)):
            # Calculate offset for green wave
            offset = (i * spacing) / green_wave_speed

            phases = [
                SignalPhase(
                    name="Arterial_Green",
                    duration=base_green_time,
                    green_approaches=['north', 'south'],
                    yellow_duration=3.0
                ),
                SignalPhase(
                    name="Cross_Green",
                    duration=30.0,
                    green_approaches=['east', 'west'],
                    yellow_duration=3.0
                )
            ]

            signal = TrafficSignal(
                signal_id=i,
                node_id=node_id,
                position=position,
                phases=phases,
                coordinated=True,
                offset=offset
            )

            self.add_signal(signal)
            signals.append(signal)

        return signals

    def update_all_signals(self, time_step: float):
        """Update all signals in the controller"""
        for signal in self.signals.values():
            signal.update(time_step)

    def get_signal_at_node(self, node_id: int) -> Optional[TrafficSignal]:
        """Get signal at a specific node"""
        return self.signals.get(node_id)

    def optimize_timing(self, traffic_data: Dict):
        """
        Optimize signal timing based on traffic data
        (Placeholder for adaptive control)

        Args:
            traffic_data: Dictionary of traffic metrics
        """
        # This would implement adaptive signal control
        # For now, it's a placeholder
        pass

    def get_statistics(self) -> Dict:
        """Get statistics from all signals"""
        total_vehicles = sum(s.vehicles_served for s in self.signals.values())
        total_delay = sum(s.total_delay for s in self.signals.values())

        return {
            'num_signals': len(self.signals),
            'total_vehicles_served': total_vehicles,
            'total_delay': total_delay,
            'average_delay_per_vehicle': total_delay / max(total_vehicles, 1)
        }


class SignalTiming:
    """
    Utilities for calculating optimal signal timing
    """

    @staticmethod
    def calculate_cycle_length(
        critical_volumes: List[float],
        lost_time_per_phase: float = 4.0,
        target_vc_ratio: float = 0.9
    ) -> float:
        """
        Calculate optimal cycle length using Webster's method

        Args:
            critical_volumes: List of critical lane volumes for each phase
            lost_time_per_phase: Lost time per phase (seconds)
            target_vc_ratio: Target volume-to-capacity ratio

        Returns:
            Optimal cycle length (seconds)
        """
        total_lost_time = len(critical_volumes) * lost_time_per_phase
        sum_critical_ratios = sum(critical_volumes)

        cycle_length = (1.5 * total_lost_time + 5) / (1 - sum_critical_ratios / target_vc_ratio)

        # Constrain to reasonable bounds
        return np.clip(cycle_length, 60, 180)

    @staticmethod
    def split_green_time(
        cycle_length: float,
        phase_volumes: List[float],
        yellow_time: float = 3.0,
        all_red_time: float = 1.0
    ) -> List[float]:
        """
        Split available green time among phases

        Args:
            cycle_length: Total cycle length (seconds)
            phase_volumes: Traffic volumes for each phase
            yellow_time: Yellow time per phase
            all_red_time: All-red clearance time per phase

        Returns:
            List of green times for each phase
        """
        num_phases = len(phase_volumes)
        lost_time = num_phases * (yellow_time + all_red_time)
        available_green = cycle_length - lost_time

        total_volume = sum(phase_volumes)
        if total_volume == 0:
            # Equal split if no volume data
            return [available_green / num_phases] * num_phases

        # Proportional split based on volume
        green_times = [
            (volume / total_volume) * available_green
            for volume in phase_volumes
        ]

        # Ensure minimum green time
        min_green = 7.0
        green_times = [max(g, min_green) for g in green_times]

        return green_times
