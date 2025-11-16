#!/usr/bin/env python3
"""
Simple example of running the Bellevue traffic simulation
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bellevue_traffic.simulation import TrafficSimulation
from bellevue_traffic.visualization import TrafficVisualizer
from bellevue_traffic.analytics import TrafficAnalytics
from bellevue_traffic.traffic_patterns import DayOfWeek


def main():
    """Simple simulation example"""

    print("Starting simple Bellevue traffic simulation...")
    print("This will simulate 1 hour of morning rush hour traffic\n")

    # Create simulation
    # Duration: 1 hour (3600 seconds)
    # Start time: 7:00 AM
    # Day: Weekday
    sim = TrafficSimulation(
        duration=3600,  # 1 hour in seconds
        time_step=1.0,  # Update every second
        start_hour=7.0,  # 7:00 AM
        day_of_week=DayOfWeek.WEEKDAY,
        seed=42  # For reproducible results
    )

    # Setup the simulation (loads network, creates signals)
    sim.setup()

    # Run the simulation
    sim.run()

    # Analyze results
    print("\nAnalyzing results...")
    analytics = TrafficAnalytics(sim)
    analytics.print_summary_report()

    # Create visualizations
    print("\nCreating visualizations...")
    visualizer = TrafficVisualizer(sim)
    visualizer.create_all_visualizations()

    print("\nDone! Check the 'output' directory for results.")
    print("Open the HTML files in a web browser to see interactive maps.")


if __name__ == '__main__':
    main()
