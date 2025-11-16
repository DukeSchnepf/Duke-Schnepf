"""
Visualization module for traffic simulation
Creates interactive maps and charts
"""

import folium
from folium import plugins
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List, Tuple, Optional
import os

from .simulation import TrafficSimulation
from .road_network import BellevueRoadNetwork


class TrafficVisualizer:
    """
    Creates visualizations for traffic simulation results
    """

    def __init__(self, simulation: TrafficSimulation, output_dir: str = "output"):
        """
        Initialize visualizer

        Args:
            simulation: TrafficSimulation instance
            output_dir: Directory for output files
        """
        self.simulation = simulation
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Set style for matplotlib
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)

    def create_network_map(self, filename: str = "network_map.html",
                          show_signals: bool = True,
                          show_congestion: bool = True) -> str:
        """
        Create interactive map of road network

        Args:
            filename: Output filename
            show_signals: Whether to show traffic signals
            show_congestion: Whether to show congestion levels

        Returns:
            Path to created HTML file
        """
        network = self.simulation.network

        # Get center of network
        lats = [data['y'] for _, data in network.graph.nodes(data=True)]
        lons = [data['x'] for _, data in network.graph.nodes(data=True)]
        center_lat = np.mean(lats)
        center_lon = np.mean(lons)

        # Create map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=13,
            tiles='OpenStreetMap'
        )

        # Add road network
        if show_congestion:
            self._add_roads_with_congestion(m)
        else:
            self._add_roads_simple(m)

        # Add traffic signals
        if show_signals:
            self._add_traffic_signals(m)

        # Add legend
        self._add_legend(m)

        # Save map
        filepath = os.path.join(self.output_dir, filename)
        m.save(filepath)
        print(f"Network map saved to {filepath}")

        return filepath

    def _add_roads_simple(self, m: folium.Map):
        """Add roads to map without congestion coloring"""
        network = self.simulation.network

        for u, v, key, data in network.graph.edges(keys=True, data=True):
            u_pos = network.get_node_position(u)
            v_pos = network.get_node_position(v)

            # Color by road type
            road_type = data.get('highway', 'residential')
            if isinstance(road_type, list):
                road_type = road_type[0]

            if road_type in ['motorway', 'motorway_link']:
                color = 'red'
                weight = 4
            elif road_type in ['trunk', 'trunk_link', 'primary', 'primary_link']:
                color = 'orange'
                weight = 3
            elif road_type in ['secondary', 'secondary_link']:
                color = 'blue'
                weight = 2
            else:
                color = 'gray'
                weight = 1

            folium.PolyLine(
                locations=[u_pos, v_pos],
                color=color,
                weight=weight,
                opacity=0.6
            ).add_to(m)

    def _add_roads_with_congestion(self, m: folium.Map):
        """Add roads to map with congestion coloring"""
        network = self.simulation.network
        edge_speeds = self.simulation.get_edge_speeds()

        for u, v, key, data in network.graph.edges(keys=True, data=True):
            edge = (u, v, key)
            u_pos = network.get_node_position(u)
            v_pos = network.get_node_position(v)

            # Get congestion level
            congestion = self.simulation.get_congestion_level(edge)

            # Color based on congestion (green = free flow, red = congested)
            if congestion < 0.3:
                color = 'green'
            elif congestion < 0.6:
                color = 'yellow'
            elif congestion < 0.8:
                color = 'orange'
            else:
                color = 'red'

            # Road type affects weight
            road_type = data.get('highway', 'residential')
            if isinstance(road_type, list):
                road_type = road_type[0]

            if road_type in ['motorway', 'motorway_link']:
                weight = 4
            elif road_type in ['trunk', 'trunk_link', 'primary', 'primary_link']:
                weight = 3
            else:
                weight = 2

            folium.PolyLine(
                locations=[u_pos, v_pos],
                color=color,
                weight=weight,
                opacity=0.7,
                popup=f"Congestion: {congestion:.2f}"
            ).add_to(m)

    def _add_traffic_signals(self, m: folium.Map):
        """Add traffic signal markers to map"""
        for signal in self.simulation.signal_controller.signals.values():
            folium.CircleMarker(
                location=signal.position,
                radius=5,
                color='black',
                fill=True,
                fillColor='yellow',
                fillOpacity=0.8,
                popup=f"Signal {signal.id}<br>Cycle: {signal.cycle_length:.0f}s"
            ).add_to(m)

    def _add_legend(self, m: folium.Map):
        """Add legend to map"""
        legend_html = '''
        <div style="position: fixed;
                    bottom: 50px; right: 50px; width: 200px; height: 180px;
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:14px; padding: 10px">
        <p style="margin-bottom: 5px;"><strong>Congestion Level</strong></p>
        <p style="margin: 3px;"><span style="color: green;">●</span> Low (0-30%)</p>
        <p style="margin: 3px;"><span style="color: yellow;">●</span> Moderate (30-60%)</p>
        <p style="margin: 3px;"><span style="color: orange;">●</span> High (60-80%)</p>
        <p style="margin: 3px;"><span style="color: red;">●</span> Severe (80-100%)</p>
        <p style="margin-top: 10px;"><span style="color: yellow;">●</span> Traffic Signal</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))

    def create_vehicle_animation(self, filename: str = "vehicle_animation.html",
                                 snapshot_indices: Optional[List[int]] = None) -> str:
        """
        Create animated visualization of vehicle movement

        Args:
            filename: Output filename
            snapshot_indices: Which snapshots to include (None = all)

        Returns:
            Path to created HTML file
        """
        snapshots = self.simulation.get_snapshots()

        if not snapshots:
            print("No snapshots available for animation")
            return None

        if snapshot_indices is not None:
            snapshots = [snapshots[i] for i in snapshot_indices if i < len(snapshots)]

        network = self.simulation.network

        # Get center of network
        lats = [data['y'] for _, data in network.graph.nodes(data=True)]
        lons = [data['x'] for _, data in network.graph.nodes(data=True)]
        center_lat = np.mean(lats)
        center_lon = np.mean(lons)

        # Create map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=13,
            tiles='OpenStreetMap'
        )

        # Add base road network
        self._add_roads_simple(m)

        # Create feature groups for each snapshot
        for i, snapshot in enumerate(snapshots):
            feature_group = folium.FeatureGroup(name=f"Time: {snapshot['time']:.0f}s")

            for vehicle_data in snapshot['vehicles']:
                # Vehicle color by type
                vehicle_type = vehicle_data['type']
                if vehicle_type == 'car':
                    color = 'blue'
                    icon = 'car'
                elif vehicle_type == 'truck':
                    color = 'brown'
                    icon = 'truck'
                elif vehicle_type == 'bus':
                    color = 'green'
                    icon = 'bus'
                else:
                    color = 'purple'
                    icon = 'motorcycle'

                # Vehicle position
                pos = vehicle_data['position']

                folium.CircleMarker(
                    location=pos,
                    radius=3,
                    color=color,
                    fill=True,
                    fillOpacity=0.7,
                    popup=f"Vehicle {vehicle_data['id']}<br>Speed: {vehicle_data['speed']*3.6:.1f} km/h"
                ).add_to(feature_group)

            feature_group.add_to(m)

        # Add layer control for animation
        folium.LayerControl().add_to(m)

        # Save map
        filepath = os.path.join(self.output_dir, filename)
        m.save(filepath)
        print(f"Vehicle animation saved to {filepath}")

        return filepath

    def plot_traffic_statistics(self, filename: str = "statistics.png"):
        """
        Create plots of traffic statistics

        Args:
            filename: Output filename

        Returns:
            Path to created image file
        """
        stats = self.simulation.get_statistics()

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Plot 1: Vehicles over time
        snapshots = self.simulation.get_snapshots()
        times = [s['time']/60 for s in snapshots]  # Convert to minutes
        vehicle_counts = [len(s['vehicles']) for s in snapshots]

        axes[0, 0].plot(times, vehicle_counts, 'b-', linewidth=2)
        axes[0, 0].set_xlabel('Time (minutes)')
        axes[0, 0].set_ylabel('Active Vehicles')
        axes[0, 0].set_title('Active Vehicles Over Time')
        axes[0, 0].grid(True, alpha=0.3)

        # Plot 2: Speed distribution
        if self.simulation.completed_vehicles:
            speeds = [v.stats.max_speed * 3.6 for v in self.simulation.completed_vehicles]  # km/h
            axes[0, 1].hist(speeds, bins=30, color='green', alpha=0.7, edgecolor='black')
            axes[0, 1].set_xlabel('Max Speed (km/h)')
            axes[0, 1].set_ylabel('Number of Vehicles')
            axes[0, 1].set_title('Maximum Speed Distribution')
            axes[0, 1].grid(True, alpha=0.3)

        # Plot 3: Travel time distribution
        if self.simulation.completed_vehicles:
            travel_times = [v.stats.total_time/60 for v in self.simulation.completed_vehicles]  # minutes
            axes[1, 0].hist(travel_times, bins=30, color='orange', alpha=0.7, edgecolor='black')
            axes[1, 0].set_xlabel('Travel Time (minutes)')
            axes[1, 0].set_ylabel('Number of Vehicles')
            axes[1, 0].set_title('Travel Time Distribution')
            axes[1, 0].grid(True, alpha=0.3)

        # Plot 4: Summary statistics
        axes[1, 1].axis('off')
        summary_text = f"""
        SIMULATION SUMMARY
        ==================

        Duration: {self.simulation.duration/3600:.2f} hours

        Vehicles Spawned: {stats['vehicles_spawned']}
        Vehicles Completed: {stats['vehicles_completed']}

        Average Travel Time: {stats.get('avg_travel_time', 0)/60:.2f} min
        Average Distance: {stats.get('avg_distance', 0)/1000:.2f} km
        Average Speed: {stats.get('avg_speed', 0)*3.6:.2f} km/h

        Traffic Signals: {stats.get('num_signals', 0)}
        """
        axes[1, 1].text(0.1, 0.5, summary_text, fontsize=12, family='monospace',
                       verticalalignment='center')

        plt.tight_layout()

        # Save figure
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Statistics plot saved to {filepath}")
        return filepath

    def create_heatmap(self, filename: str = "congestion_heatmap.html") -> str:
        """
        Create heatmap of traffic density

        Args:
            filename: Output filename

        Returns:
            Path to created HTML file
        """
        network = self.simulation.network

        # Get center of network
        lats = [data['y'] for _, data in network.graph.nodes(data=True)]
        lons = [data['x'] for _, data in network.graph.nodes(data=True)]
        center_lat = np.mean(lats)
        center_lon = np.mean(lons)

        # Create map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=13,
            tiles='OpenStreetMap'
        )

        # Collect heat data from edges
        heat_data = []

        for edge, vehicles in self.simulation.edge_vehicles.items():
            if vehicles:
                u, v, key = edge
                u_pos = network.get_node_position(u)
                v_pos = network.get_node_position(v)

                # Add points along edge weighted by number of vehicles
                num_vehicles = len(vehicles)

                # Add multiple points for higher density
                for i in range(min(num_vehicles, 10)):
                    # Interpolate position along edge
                    t = (i + 1) / 11
                    lat = u_pos[0] + t * (v_pos[0] - u_pos[0])
                    lon = u_pos[1] + t * (v_pos[1] - u_pos[1])
                    heat_data.append([lat, lon, num_vehicles])

        # Add heatmap layer
        if heat_data:
            plugins.HeatMap(heat_data, radius=15, blur=25, max_zoom=13).add_to(m)

        # Save map
        filepath = os.path.join(self.output_dir, filename)
        m.save(filepath)
        print(f"Congestion heatmap saved to {filepath}")

        return filepath

    def create_all_visualizations(self):
        """Create all standard visualizations"""
        print("\nGenerating visualizations...")

        self.create_network_map("network_map.html")
        self.plot_traffic_statistics("statistics.png")
        self.create_heatmap("congestion_heatmap.html")

        # Create animation with subset of snapshots
        snapshots = self.simulation.get_snapshots()
        if len(snapshots) > 10:
            # Sample snapshots for animation
            indices = np.linspace(0, len(snapshots)-1, 10, dtype=int)
            self.create_vehicle_animation("vehicle_animation.html", list(indices))
        else:
            self.create_vehicle_animation("vehicle_animation.html")

        print(f"\nAll visualizations saved to {self.output_dir}/")
        print("Files created:")
        print("  - network_map.html")
        print("  - statistics.png")
        print("  - congestion_heatmap.html")
        print("  - vehicle_animation.html")
