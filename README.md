# Bellevue Traffic Simulation

A comprehensive, realistic traffic simulation for Bellevue, Washington, built with Python. This simulation models traffic flow on real road networks using OpenStreetMap data, featuring realistic vehicle behavior, traffic signals, and time-of-day traffic patterns.

## Features

### Core Capabilities

- **Real Road Network**: Uses OpenStreetMap data via OSMnx to model Bellevue's actual road network
- **Multiple Vehicle Types**: Cars, trucks, buses, and motorcycles with distinct behaviors
- **Realistic Traffic Patterns**: Models morning rush, evening rush, midday, and off-peak traffic
- **Traffic Signals**: Coordinated traffic signal system with configurable timing
- **Congestion Modeling**: Realistic traffic flow and congestion based on vehicle density
- **Interactive Visualizations**: Maps, charts, and animations of traffic patterns

### Major Corridors Modeled

- Interstate 405 (I-405)
- State Route 520 (SR-520)
- Bellevue Way
- NE 8th Street
- Downtown Bellevue grid

### Key Locations

- Downtown Bellevue
- Microsoft Campus area
- Bellevue Square shopping district
- I-405/SR-520 interchange
- Residential areas

## Installation

### Requirements

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Duke-Schnepf
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Simple Example

Run a basic 1-hour morning rush simulation:

```bash
python example_simple.py
```

This will:
- Simulate 1 hour of traffic starting at 7:00 AM
- Generate visualizations in the `output/` directory
- Print detailed statistics

### Main Simulation

For more control, use the main script:

```bash
# Morning rush hour (7-9 AM)
python main.py --duration 2 --start-hour 7 --day weekday

# Evening rush hour (4-6 PM)
python main.py --duration 2 --start-hour 16 --day weekday

# Weekend midday traffic
python main.py --duration 3 --start-hour 12 --day saturday

# Quick 30-minute test
python main.py --duration 0.5 --start-hour 8
```

### Command Line Options

```bash
python main.py --help
```

Options:
- `--duration HOURS`: Simulation duration in hours (default: 1.0)
- `--start-hour HOUR`: Starting hour (0-24, default: 7.0)
- `--day {weekday,saturday,sunday}`: Day of week (default: weekday)
- `--seed SEED`: Random seed for reproducibility
- `--no-viz`: Skip visualization generation
- `--output-dir DIR`: Output directory (default: output)
- `--time-step SECONDS`: Simulation time step (default: 1.0)

## Examples

### Compare Different Time Periods

```bash
python example_comparison.py
```

This compares traffic patterns across:
- Morning rush (7-9 AM)
- Midday (12-2 PM)
- Evening rush (4-6 PM)
- Night (10 PM-12 AM)

### Custom Simulation

```python
from bellevue_traffic.simulation import TrafficSimulation
from bellevue_traffic.traffic_patterns import DayOfWeek

# Create simulation
sim = TrafficSimulation(
    duration=7200,  # 2 hours
    start_hour=7.0,  # 7 AM
    day_of_week=DayOfWeek.WEEKDAY,
    seed=42
)

# Run
sim.setup()
sim.run()

# Get statistics
stats = sim.get_statistics()
print(f"Completed trips: {stats['vehicles_completed']}")
```

## Project Structure

```
Duke-Schnepf/
├── src/bellevue_traffic/
│   ├── __init__.py
│   ├── vehicles.py           # Vehicle classes and behavior models
│   ├── road_network.py       # Road network loading and management
│   ├── traffic_signals.py    # Traffic signal system
│   ├── traffic_patterns.py   # Traffic demand patterns
│   ├── simulation.py         # Main simulation engine
│   ├── visualization.py      # Visualization tools
│   └── analytics.py          # Analytics and statistics
├── data/                     # Cached network data
├── output/                   # Generated visualizations and results
├── main.py                   # Main entry point
├── example_simple.py         # Simple example
├── example_comparison.py     # Time comparison example
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Output Files

After running a simulation, check the `output/` directory for:

### Interactive Maps (HTML)

- **network_map.html**: Road network with congestion coloring
  - Green: Free flow
  - Yellow: Moderate congestion
  - Orange: High congestion
  - Red: Severe congestion

- **congestion_heatmap.html**: Heat map of traffic density

- **vehicle_animation.html**: Animated vehicle movement over time

### Charts and Statistics (PNG)

- **statistics.png**: Comprehensive statistics dashboard
  - Active vehicles over time
  - Speed distribution
  - Travel time distribution
  - Summary statistics

### Data Files (CSV)

- **traffic_statistics.csv**: Detailed simulation metrics

## Simulation Components

### Vehicle Models

Four vehicle types with realistic characteristics:

1. **Cars**: Standard passenger vehicles
   - Max speed: 120 km/h
   - Moderate acceleration
   - Variable aggressiveness

2. **Trucks**: Heavy commercial vehicles
   - Max speed: 100 km/h
   - Slower acceleration
   - Conservative driving

3. **Buses**: Public transit
   - Max speed: 90 km/h
   - Stop at designated locations
   - Polite driving behavior

4. **Motorcycles**: Agile two-wheelers
   - Max speed: 140 km/h
   - Quick acceleration
   - More aggressive lane changing

### Traffic Flow Model

Uses the **Intelligent Driver Model (IDM)** for car-following behavior:
- Maintains safe following distance
- Smooth acceleration/deceleration
- Realistic response to traffic signals

### Lane Changing

Implements **MOBIL** (Minimizing Overall Braking Induced by Lane changes):
- Evaluates lane change benefit
- Considers safety gaps
- Accounts for politeness factor

### Traffic Patterns

Realistic time-of-day variations:

| Time Period | Hours | Multiplier | Description |
|-------------|-------|------------|-------------|
| Early Morning | 5-7 AM | 0.3× | Light traffic |
| Morning Rush | 7-9 AM | 1.8× | Heavy commute traffic |
| Midday | 9 AM-4 PM | 0.8× | Moderate traffic |
| Evening Rush | 4-7 PM | 2.0× | Peak congestion |
| Evening | 7-10 PM | 0.6× | Declining traffic |
| Night | 10 PM-5 AM | 0.1× | Minimal traffic |

### Traffic Signals

- Coordinated signal timing along major arterials
- Green wave progression
- Adaptive to traffic conditions
- Realistic yellow and all-red clearance intervals

## Customization

### Modify Traffic Patterns

Edit `src/bellevue_traffic/traffic_patterns.py`:

```python
# Change rush hour intensity
MORNING_RUSH_MULTIPLIER = 2.5  # More intense

# Adjust vehicle mix
truck_percentage = 0.15  # More trucks
```

### Add Custom Zones

```python
ZONES = {
    'custom_zone': [(47.620, -122.180), ...],
    ...
}
```

### Adjust Signal Timing

```python
# Create custom signal
signal = controller.create_standard_signal(
    signal_id=1,
    node_id=node,
    position=(lat, lon),
    major_street_time=90.0,  # Longer green
    minor_street_time=20.0
)
```

## Performance Tips

1. **Use cached network data**: First run downloads from OpenStreetMap and caches data
2. **Adjust time step**: Larger time steps (2-5 seconds) run faster with less accuracy
3. **Reduce duration**: Test with shorter simulations (0.5-1 hour)
4. **Limit visualization**: Use `--no-viz` flag for faster runs
5. **Snapshot interval**: Increase `snapshot_interval` in simulation.py

## Technical Details

### Dependencies

- **SimPy**: Discrete-event simulation framework
- **OSMnx**: OpenStreetMap data retrieval
- **NetworkX**: Graph algorithms
- **Folium**: Interactive maps
- **Matplotlib/Seaborn**: Statistical visualizations
- **NumPy/Pandas**: Data processing

### Simulation Architecture

1. **Event-driven**: Uses SimPy for efficient discrete-event simulation
2. **Modular design**: Separate components for vehicles, network, signals, patterns
3. **Realistic physics**: IDM car-following, MOBIL lane-changing
4. **Scalable**: Handles hundreds to thousands of vehicles

## Troubleshooting

### Network Download Issues

If OpenStreetMap download fails:
- Check internet connection
- The simulation will automatically use a demo grid network
- Cached data in `data/` directory will be reused on subsequent runs

### Memory Issues

For long simulations:
- Reduce duration
- Increase snapshot interval
- Use `--no-viz` to skip visualization

### Import Errors

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt --upgrade
```

## Contributing

This is a modular, extensible codebase. Areas for enhancement:

- [ ] Add more realistic lane-changing logic
- [ ] Implement route choice based on congestion
- [ ] Add incident/accident modeling
- [ ] Include parking and land use
- [ ] Add weather effects
- [ ] Calibrate with real traffic data

## License

This project is provided as-is for educational and research purposes.

## Acknowledgments

- OpenStreetMap contributors for road network data
- SimPy team for the simulation framework
- OSMnx developers for geospatial tools

## Contact

For questions, issues, or contributions, please open an issue on GitHub.

---

**Enjoy exploring Bellevue's traffic patterns!** 🚗🚌🚛
