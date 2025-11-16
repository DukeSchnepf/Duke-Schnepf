"""
Analytics module for traffic simulation
Provides detailed analysis and metrics
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

from .simulation import TrafficSimulation
from .vehicles import Vehicle


class TrafficAnalytics:
    """
    Analyzes traffic simulation results
    Provides detailed metrics and insights
    """

    def __init__(self, simulation: TrafficSimulation):
        """
        Initialize analytics

        Args:
            simulation: TrafficSimulation instance
        """
        self.simulation = simulation

    def get_comprehensive_statistics(self) -> Dict:
        """
        Get comprehensive traffic statistics

        Returns:
            Dictionary of detailed statistics
        """
        stats = {
            'general': self._get_general_stats(),
            'travel_times': self._get_travel_time_stats(),
            'speeds': self._get_speed_stats(),
            'congestion': self._get_congestion_stats(),
            'vehicle_types': self._get_vehicle_type_stats(),
            'network_performance': self._get_network_performance_stats()
        }

        return stats

    def _get_general_stats(self) -> Dict:
        """Get general simulation statistics"""
        sim_stats = self.simulation.get_statistics()

        return {
            'simulation_duration_hours': self.simulation.duration / 3600,
            'start_hour': self.simulation.start_hour,
            'day_of_week': self.simulation.day_of_week.value,
            'vehicles_spawned': sim_stats['vehicles_spawned'],
            'vehicles_completed': sim_stats['vehicles_completed'],
            'vehicles_active': len(self.simulation.vehicles),
            'completion_rate': sim_stats['vehicles_completed'] / max(sim_stats['vehicles_spawned'], 1)
        }

    def _get_travel_time_stats(self) -> Dict:
        """Get travel time statistics"""
        completed = self.simulation.completed_vehicles

        if not completed:
            return {
                'count': 0,
                'mean': 0,
                'median': 0,
                'std': 0,
                'min': 0,
                'max': 0,
                'percentile_25': 0,
                'percentile_75': 0,
                'percentile_95': 0
            }

        travel_times = np.array([v.stats.total_time for v in completed])

        return {
            'count': len(travel_times),
            'mean_seconds': float(np.mean(travel_times)),
            'mean_minutes': float(np.mean(travel_times) / 60),
            'median_seconds': float(np.median(travel_times)),
            'median_minutes': float(np.median(travel_times) / 60),
            'std_seconds': float(np.std(travel_times)),
            'min_seconds': float(np.min(travel_times)),
            'max_seconds': float(np.max(travel_times)),
            'percentile_25': float(np.percentile(travel_times, 25)),
            'percentile_75': float(np.percentile(travel_times, 75)),
            'percentile_95': float(np.percentile(travel_times, 95))
        }

    def _get_speed_stats(self) -> Dict:
        """Get speed statistics"""
        completed = self.simulation.completed_vehicles

        if not completed:
            return {
                'count': 0,
                'mean_kmh': 0,
                'median_kmh': 0,
                'max_kmh': 0
            }

        avg_speeds = np.array([v.stats.average_speed * 3.6 for v in completed])  # Convert to km/h
        max_speeds = np.array([v.stats.max_speed * 3.6 for v in completed])

        return {
            'count': len(avg_speeds),
            'mean_avg_speed_kmh': float(np.mean(avg_speeds)),
            'median_avg_speed_kmh': float(np.median(avg_speeds)),
            'std_avg_speed_kmh': float(np.std(avg_speeds)),
            'mean_max_speed_kmh': float(np.mean(max_speeds)),
            'median_max_speed_kmh': float(np.median(max_speeds)),
            'overall_max_speed_kmh': float(np.max(max_speeds))
        }

    def _get_congestion_stats(self) -> Dict:
        """Get congestion statistics"""
        edges = list(self.simulation.network.graph.edges(keys=True))

        if not edges:
            return {
                'total_edges': 0,
                'mean_congestion': 0,
                'highly_congested_edges': 0
            }

        congestion_levels = []
        for edge in edges:
            congestion = self.simulation.get_congestion_level(edge)
            congestion_levels.append(congestion)

        congestion_array = np.array(congestion_levels)

        # Count edges by congestion level
        low = np.sum(congestion_array < 0.3)
        moderate = np.sum((congestion_array >= 0.3) & (congestion_array < 0.6))
        high = np.sum((congestion_array >= 0.6) & (congestion_array < 0.8))
        severe = np.sum(congestion_array >= 0.8)

        return {
            'total_edges': len(edges),
            'mean_congestion': float(np.mean(congestion_array)),
            'median_congestion': float(np.median(congestion_array)),
            'max_congestion': float(np.max(congestion_array)),
            'low_congestion_edges': int(low),
            'moderate_congestion_edges': int(moderate),
            'high_congestion_edges': int(high),
            'severe_congestion_edges': int(severe),
            'percent_congested': float(100 * np.sum(congestion_array >= 0.6) / len(congestion_array))
        }

    def _get_vehicle_type_stats(self) -> Dict:
        """Get statistics by vehicle type"""
        completed = self.simulation.completed_vehicles

        if not completed:
            return {}

        type_stats = defaultdict(lambda: {
            'count': 0,
            'avg_travel_time': [],
            'avg_speed': [],
            'avg_distance': []
        })

        for vehicle in completed:
            vtype = vehicle.type.value
            type_stats[vtype]['count'] += 1
            type_stats[vtype]['avg_travel_time'].append(vehicle.stats.total_time)
            type_stats[vtype]['avg_speed'].append(vehicle.stats.average_speed * 3.6)  # km/h
            type_stats[vtype]['avg_distance'].append(vehicle.stats.total_distance / 1000)  # km

        # Calculate averages
        result = {}
        for vtype, data in type_stats.items():
            result[vtype] = {
                'count': data['count'],
                'avg_travel_time_minutes': float(np.mean(data['avg_travel_time']) / 60) if data['avg_travel_time'] else 0,
                'avg_speed_kmh': float(np.mean(data['avg_speed'])) if data['avg_speed'] else 0,
                'avg_distance_km': float(np.mean(data['avg_distance'])) if data['avg_distance'] else 0
            }

        return result

    def _get_network_performance_stats(self) -> Dict:
        """Get network-wide performance statistics"""
        network = self.simulation.network

        # Calculate total network length
        total_length = 0
        for u, v, key, data in network.graph.edges(keys=True, data=True):
            total_length += data.get('length', 0)

        # Calculate total vehicle-kilometers traveled
        total_vkt = sum(v.stats.total_distance for v in self.simulation.completed_vehicles) / 1000

        # Calculate total vehicle-hours
        total_vht = sum(v.stats.total_time for v in self.simulation.completed_vehicles) / 3600

        # Average network speed
        avg_network_speed = (total_vkt / total_vht) if total_vht > 0 else 0

        return {
            'total_network_length_km': total_length / 1000,
            'total_nodes': len(network.graph.nodes()),
            'total_edges': len(network.graph.edges()),
            'total_vehicle_kilometers': float(total_vkt),
            'total_vehicle_hours': float(total_vht),
            'avg_network_speed_kmh': float(avg_network_speed),
            'num_traffic_signals': len(self.simulation.signal_controller.signals)
        }

    def get_time_series_data(self) -> pd.DataFrame:
        """
        Get time series data from snapshots

        Returns:
            DataFrame with time series metrics
        """
        snapshots = self.simulation.get_snapshots()

        if not snapshots:
            return pd.DataFrame()

        data = []
        for snapshot in snapshots:
            time = snapshot['time']
            vehicles = snapshot['vehicles']

            # Calculate metrics for this snapshot
            num_vehicles = len(vehicles)
            if vehicles:
                avg_speed = np.mean([v['speed'] * 3.6 for v in vehicles])  # km/h
                num_waiting = sum(1 for v in vehicles if v.get('waiting', False))
            else:
                avg_speed = 0
                num_waiting = 0

            data.append({
                'time_seconds': time,
                'time_minutes': time / 60,
                'active_vehicles': num_vehicles,
                'avg_speed_kmh': avg_speed,
                'vehicles_waiting': num_waiting,
                'percent_waiting': (num_waiting / num_vehicles * 100) if num_vehicles > 0 else 0
            })

        return pd.DataFrame(data)

    def export_to_csv(self, filename: str = "traffic_analysis.csv"):
        """
        Export analysis to CSV

        Args:
            filename: Output filename
        """
        # Get comprehensive statistics
        stats = self.get_comprehensive_statistics()

        # Flatten nested dictionary
        flat_stats = {}
        for category, metrics in stats.items():
            if isinstance(metrics, dict):
                for key, value in metrics.items():
                    flat_stats[f"{category}_{key}"] = value
            else:
                flat_stats[category] = metrics

        # Create DataFrame
        df = pd.DataFrame([flat_stats])

        # Save to CSV
        filepath = f"output/{filename}"
        df.to_csv(filepath, index=False)
        print(f"Analysis exported to {filepath}")

        return filepath

    def print_summary_report(self):
        """Print a comprehensive summary report"""
        stats = self.get_comprehensive_statistics()

        print("\n" + "="*70)
        print(" "*20 + "TRAFFIC ANALYSIS REPORT")
        print("="*70)

        # General Statistics
        print("\nGENERAL STATISTICS")
        print("-" * 70)
        gen = stats['general']
        print(f"Simulation Duration:     {gen['simulation_duration_hours']:.2f} hours")
        print(f"Start Time:              {gen['start_hour']:.0f}:00")
        print(f"Day of Week:             {gen['day_of_week']}")
        print(f"Vehicles Spawned:        {gen['vehicles_spawned']}")
        print(f"Vehicles Completed:      {gen['vehicles_completed']}")
        print(f"Completion Rate:         {gen['completion_rate']*100:.1f}%")

        # Travel Time Statistics
        print("\nTRAVEL TIME STATISTICS")
        print("-" * 70)
        tt = stats['travel_times']
        if tt['count'] > 0:
            print(f"Number of Trips:         {tt['count']}")
            print(f"Mean Travel Time:        {tt['mean_minutes']:.2f} minutes")
            print(f"Median Travel Time:      {tt['median_minutes']:.2f} minutes")
            print(f"95th Percentile:         {tt['percentile_95']/60:.2f} minutes")
            print(f"Min Travel Time:         {tt['min_seconds']/60:.2f} minutes")
            print(f"Max Travel Time:         {tt['max_seconds']/60:.2f} minutes")

        # Speed Statistics
        print("\nSPEED STATISTICS")
        print("-" * 70)
        spd = stats['speeds']
        if spd['count'] > 0:
            print(f"Mean Average Speed:      {spd['mean_avg_speed_kmh']:.2f} km/h")
            print(f"Median Average Speed:    {spd['median_avg_speed_kmh']:.2f} km/h")
            print(f"Overall Max Speed:       {spd['overall_max_speed_kmh']:.2f} km/h")

        # Congestion Statistics
        print("\nCONGESTION STATISTICS")
        print("-" * 70)
        cong = stats['congestion']
        print(f"Total Road Segments:     {cong['total_edges']}")
        print(f"Mean Congestion Level:   {cong['mean_congestion']*100:.1f}%")
        print(f"Low Congestion:          {cong['low_congestion_edges']} segments ({cong['low_congestion_edges']/cong['total_edges']*100:.1f}%)")
        print(f"Moderate Congestion:     {cong['moderate_congestion_edges']} segments ({cong['moderate_congestion_edges']/cong['total_edges']*100:.1f}%)")
        print(f"High Congestion:         {cong['high_congestion_edges']} segments ({cong['high_congestion_edges']/cong['total_edges']*100:.1f}%)")
        print(f"Severe Congestion:       {cong['severe_congestion_edges']} segments ({cong['severe_congestion_edges']/cong['total_edges']*100:.1f}%)")

        # Vehicle Type Statistics
        print("\nVEHICLE TYPE BREAKDOWN")
        print("-" * 70)
        for vtype, vdata in stats['vehicle_types'].items():
            print(f"\n{vtype.upper()}:")
            print(f"  Count:                 {vdata['count']}")
            print(f"  Avg Travel Time:       {vdata['avg_travel_time_minutes']:.2f} minutes")
            print(f"  Avg Speed:             {vdata['avg_speed_kmh']:.2f} km/h")
            print(f"  Avg Distance:          {vdata['avg_distance_km']:.2f} km")

        # Network Performance
        print("\nNETWORK PERFORMANCE")
        print("-" * 70)
        net = stats['network_performance']
        print(f"Network Length:          {net['total_network_length_km']:.2f} km")
        print(f"Number of Intersections: {net['total_nodes']}")
        print(f"Traffic Signals:         {net['num_traffic_signals']}")
        print(f"Total Vehicle-km:        {net['total_vehicle_kilometers']:.2f} km")
        print(f"Total Vehicle-hours:     {net['total_vehicle_hours']:.2f} hours")
        print(f"Avg Network Speed:       {net['avg_network_speed_kmh']:.2f} km/h")

        print("\n" + "="*70)

    def identify_bottlenecks(self, top_n: int = 10) -> List[Tuple]:
        """
        Identify the most congested road segments

        Args:
            top_n: Number of top bottlenecks to return

        Returns:
            List of (edge, congestion_level, vehicles) tuples
        """
        edges = list(self.simulation.network.graph.edges(keys=True))
        bottlenecks = []

        for edge in edges:
            congestion = self.simulation.get_congestion_level(edge)
            num_vehicles = len(self.simulation.edge_vehicles.get(edge, []))

            u, v, key = edge
            edge_info = self.simulation.network.get_edge_info(u, v, key)

            bottlenecks.append({
                'edge': edge,
                'from_node': u,
                'to_node': v,
                'congestion': congestion,
                'vehicles': num_vehicles,
                'road_type': edge_info['road_type'],
                'length_m': edge_info['length']
            })

        # Sort by congestion level
        bottlenecks.sort(key=lambda x: x['congestion'], reverse=True)

        return bottlenecks[:top_n]
