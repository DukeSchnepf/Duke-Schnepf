#!/usr/bin/env python3
"""
Bellevue Traffic Simulation - Main Entry Point

This script runs a realistic traffic simulation for Bellevue, Washington
"""

import argparse
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bellevue_traffic.simulation import TrafficSimulation
from bellevue_traffic.visualization import TrafficVisualizer
from bellevue_traffic.analytics import TrafficAnalytics
from bellevue_traffic.traffic_patterns import DayOfWeek


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Bellevue Traffic Simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run 1-hour morning rush simulation
  python main.py --duration 1 --start-hour 7 --day weekday

  # Run 2-hour evening rush simulation
  python main.py --duration 2 --start-hour 16 --day weekday

  # Run weekend simulation
  python main.py --duration 3 --start-hour 12 --day saturday

  # Quick 30-minute test
  python main.py --duration 0.5 --start-hour 8
        """
    )

    parser.add_argument(
        '--duration',
        type=float,
        default=1.0,
        help='Simulation duration in hours (default: 1.0)'
    )

    parser.add_argument(
        '--start-hour',
        type=float,
        default=7.0,
        help='Starting hour of day, 0-24 (default: 7.0 = 7:00 AM)'
    )

    parser.add_argument(
        '--day',
        type=str,
        choices=['weekday', 'saturday', 'sunday'],
        default='weekday',
        help='Day of week (default: weekday)'
    )

    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='Random seed for reproducibility (default: None)'
    )

    parser.add_argument(
        '--no-viz',
        action='store_true',
        help='Skip visualization generation'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Output directory for results (default: output)'
    )

    parser.add_argument(
        '--time-step',
        type=float,
        default=1.0,
        help='Simulation time step in seconds (default: 1.0)'
    )

    parser.add_argument(
        '--cache',
        action='store_true',
        default=True,
        help='Use cached network data (default: True)'
    )

    return parser.parse_args()


def main():
    """Main simulation function"""
    # Parse arguments
    args = parse_arguments()

    # Convert duration to seconds
    duration_seconds = args.duration * 3600

    # Convert day string to enum
    day_map = {
        'weekday': DayOfWeek.WEEKDAY,
        'saturday': DayOfWeek.SATURDAY,
        'sunday': DayOfWeek.SUNDAY
    }
    day_of_week = day_map[args.day]

    print("="*70)
    print(" "*15 + "BELLEVUE TRAFFIC SIMULATION")
    print("="*70)
    print(f"\nConfiguration:")
    print(f"  Duration:        {args.duration} hours")
    print(f"  Start Time:      {int(args.start_hour):02d}:{int((args.start_hour % 1) * 60):02d}")
    print(f"  Day:             {args.day}")
    print(f"  Time Step:       {args.time_step} seconds")
    print(f"  Output Dir:      {args.output_dir}")
    if args.seed:
        print(f"  Random Seed:     {args.seed}")
    print()

    # Create simulation
    sim = TrafficSimulation(
        duration=duration_seconds,
        time_step=args.time_step,
        start_hour=args.start_hour,
        day_of_week=day_of_week,
        seed=args.seed
    )

    # Setup and run
    try:
        sim.setup()
        sim.run()
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user")
        return
    except Exception as e:
        print(f"\n\nError during simulation: {e}")
        import traceback
        traceback.print_exc()
        return

    # Create analytics
    print("\nGenerating analytics...")
    analytics = TrafficAnalytics(sim)
    analytics.print_summary_report()

    # Export statistics
    analytics.export_to_csv("traffic_statistics.csv")

    # Identify bottlenecks
    print("\nTOP 10 TRAFFIC BOTTLENECKS")
    print("-" * 70)
    bottlenecks = analytics.identify_bottlenecks(top_n=10)
    for i, bn in enumerate(bottlenecks, 1):
        print(f"{i}. Edge {bn['from_node']} -> {bn['to_node']}")
        print(f"   Congestion: {bn['congestion']*100:.1f}%, "
              f"Vehicles: {bn['vehicles']}, "
              f"Type: {bn['road_type']}")

    # Generate visualizations
    if not args.no_viz:
        print("\nGenerating visualizations...")
        viz = TrafficVisualizer(sim, output_dir=args.output_dir)
        viz.create_all_visualizations()

        print(f"\nVisualization files available in '{args.output_dir}/' directory")
        print("Open the HTML files in a web browser to view interactive maps")

    print("\n" + "="*70)
    print("Simulation complete!")
    print("="*70)


if __name__ == '__main__':
    main()
