#!/usr/bin/env python3
"""
Example comparing traffic patterns at different times of day
"""

import sys
import os
import matplotlib.pyplot as plt

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bellevue_traffic.simulation import TrafficSimulation
from bellevue_traffic.analytics import TrafficAnalytics
from bellevue_traffic.traffic_patterns import DayOfWeek


def run_simulation(start_hour, duration_hours, label):
    """Run a simulation and return statistics"""
    print(f"\nRunning simulation: {label}")
    print(f"  Start: {start_hour}:00, Duration: {duration_hours}h")

    sim = TrafficSimulation(
        duration=duration_hours * 3600,
        time_step=1.0,
        start_hour=start_hour,
        day_of_week=DayOfWeek.WEEKDAY,
        seed=42
    )

    sim.setup()
    sim.run()

    analytics = TrafficAnalytics(sim)
    stats = analytics.get_comprehensive_statistics()

    return stats


def main():
    """Compare different time periods"""

    print("="*70)
    print("COMPARING TRAFFIC PATTERNS AT DIFFERENT TIMES")
    print("="*70)

    # Define scenarios
    scenarios = [
        (7, 2, "Morning Rush (7-9 AM)"),
        (12, 2, "Midday (12-2 PM)"),
        (16, 2, "Evening Rush (4-6 PM)"),
        (22, 2, "Night (10 PM-12 AM)")
    ]

    results = {}

    # Run simulations
    for start_hour, duration, label in scenarios:
        stats = run_simulation(start_hour, duration, label)
        results[label] = stats

    # Compare results
    print("\n" + "="*70)
    print("COMPARISON SUMMARY")
    print("="*70)

    print(f"\n{'Scenario':<25} {'Vehicles':<12} {'Avg Speed':<15} {'Congestion':<15}")
    print("-" * 70)

    for label, stats in results.items():
        vehicles = stats['general']['vehicles_spawned']
        avg_speed = stats['speeds'].get('mean_avg_speed_kmh', 0)
        congestion = stats['congestion'].get('mean_congestion', 0) * 100

        print(f"{label:<25} {vehicles:<12} {avg_speed:<15.1f} {congestion:<15.1f}%")

    # Create comparison chart
    print("\nGenerating comparison chart...")

    labels = list(results.keys())
    vehicles = [results[l]['general']['vehicles_spawned'] for l in labels]
    avg_speeds = [results[l]['speeds'].get('mean_avg_speed_kmh', 0) for l in labels]
    congestion = [results[l]['congestion'].get('mean_congestion', 0) * 100 for l in labels]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Vehicles spawned
    axes[0].bar(range(len(labels)), vehicles, color='steelblue')
    axes[0].set_xticks(range(len(labels)))
    axes[0].set_xticklabels(labels, rotation=45, ha='right')
    axes[0].set_ylabel('Vehicles')
    axes[0].set_title('Vehicles Spawned')
    axes[0].grid(True, alpha=0.3)

    # Average speed
    axes[1].bar(range(len(labels)), avg_speeds, color='green')
    axes[1].set_xticks(range(len(labels)))
    axes[1].set_xticklabels(labels, rotation=45, ha='right')
    axes[1].set_ylabel('Speed (km/h)')
    axes[1].set_title('Average Speed')
    axes[1].grid(True, alpha=0.3)

    # Congestion
    axes[2].bar(range(len(labels)), congestion, color='red')
    axes[2].set_xticks(range(len(labels)))
    axes[2].set_xticklabels(labels, rotation=45, ha='right')
    axes[2].set_ylabel('Congestion (%)')
    axes[2].set_title('Average Congestion')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('output/time_comparison.png', dpi=300, bbox_inches='tight')
    print("Comparison chart saved to output/time_comparison.png")

    print("\n" + "="*70)
    print("Comparison complete!")
    print("="*70)


if __name__ == '__main__':
    main()
