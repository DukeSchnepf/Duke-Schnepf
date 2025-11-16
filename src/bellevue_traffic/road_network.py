"""
Road network module for loading and managing Bellevue road network
Uses OpenStreetMap data via OSMnx
"""

import osmnx as ox
import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Optional
import pickle
import os


class BellevueRoadNetwork:
    """
    Manages the road network for Bellevue, Washington
    Loads and processes OpenStreetMap data
    """

    # Bellevue bounding box (approximate)
    BELLEVUE_BBOX = {
        'north': 47.6398,
        'south': 47.5698,
        'east': -122.1177,
        'west': -122.2177
    }

    # Major corridors to emphasize
    MAJOR_CORRIDORS = [
        'Interstate 405',
        'State Route 520',
        'Bellevue Way',
        'NE 8th Street',
        '148th Avenue NE',
        '156th Avenue NE',
        'Main Street',
        'NE 24th Street',
        'NE 12th Street',
        'Coal Creek Parkway'
    ]

    # Key locations in Bellevue
    KEY_LOCATIONS = {
        'downtown': (47.6101, -122.2015),
        'microsoft_campus': (47.6423, -122.1390),
        'bellevue_square': (47.6162, -122.2040),
        'i405_sr520_interchange': (47.6375, -122.1880),
        'downtown_park': (47.6107, -122.1997),
        'wilburton': (47.6089, -122.1764)
    }

    def __init__(self, cache_dir: str = "data"):
        """
        Initialize the road network

        Args:
            cache_dir: Directory to cache network data
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.graph = None
        self.graph_proj = None  # Projected graph for distance calculations
        self.nodes = {}
        self.edges = {}

        # Traffic properties
        self.speed_limits = {}
        self.lane_counts = {}
        self.road_types = {}

    def load_network(self, use_cache: bool = True) -> nx.MultiDiGraph:
        """
        Load the Bellevue road network from OpenStreetMap

        Args:
            use_cache: Whether to use cached data if available

        Returns:
            NetworkX graph of the road network
        """
        cache_file = os.path.join(self.cache_dir, 'bellevue_network.graphml')

        if use_cache and os.path.exists(cache_file):
            print("Loading network from cache...")
            self.graph = ox.load_graphml(cache_file)
        else:
            print("Downloading network from OpenStreetMap...")
            try:
                # Download network for Bellevue
                self.graph = ox.graph_from_bbox(
                    bbox=self.BELLEVUE_BBOX['north'],
                    south=self.BELLEVUE_BBOX['south'],
                    east=self.BELLEVUE_BBOX['east'],
                    west=self.BELLEVUE_BBOX['west'],
                    network_type='drive',
                    simplify=True
                )

                # Save to cache
                ox.save_graphml(self.graph, cache_file)
                print(f"Network saved to {cache_file}")
            except Exception as e:
                print(f"Error downloading network: {e}")
                print("Creating simplified demo network...")
                self.graph = self._create_demo_network()

        # Create projected version for accurate distance calculations
        self.graph_proj = ox.project_graph(self.graph)

        # Process network attributes
        self._process_network_attributes()

        print(f"Network loaded: {len(self.graph.nodes)} nodes, {len(self.graph.edges)} edges")
        return self.graph

    def _create_demo_network(self) -> nx.MultiDiGraph:
        """
        Create a simplified demo network for testing
        when OSM data is unavailable
        """
        G = nx.MultiDiGraph()

        # Create a grid representing downtown Bellevue
        # Approximately 10x10 blocks
        spacing = 0.003  # degrees (roughly 300m)
        center_lat, center_lon = 47.6101, -122.2015

        nodes = {}
        node_id = 0

        # Create grid nodes
        for i in range(11):
            for j in range(11):
                lat = center_lat - 5 * spacing + i * spacing
                lon = center_lon - 5 * spacing + j * spacing
                nodes[(i, j)] = node_id
                G.add_node(node_id, y=lat, x=lon, osmid=node_id)
                node_id += 1

        # Add edges (streets)
        edge_id = 0
        for i in range(11):
            for j in range(11):
                current = nodes[(i, j)]

                # Add horizontal edges (east-west streets)
                if j < 10:
                    right = nodes[(i, j + 1)]
                    # Bidirectional streets
                    G.add_edge(current, right, osmid=edge_id, length=300,
                               maxspeed=50, lanes=2, highway='secondary')
                    edge_id += 1
                    G.add_edge(right, current, osmid=edge_id, length=300,
                               maxspeed=50, lanes=2, highway='secondary')
                    edge_id += 1

                # Add vertical edges (north-south streets)
                if i < 10:
                    down = nodes[(i + 1, j)]
                    G.add_edge(current, down, osmid=edge_id, length=300,
                               maxspeed=50, lanes=2, highway='secondary')
                    edge_id += 1
                    G.add_edge(down, current, osmid=edge_id, length=300,
                               maxspeed=50, lanes=2, highway='secondary')
                    edge_id += 1

        # Add major arterials (wider, faster roads)
        # I-405 equivalent (vertical on west side)
        for i in range(10):
            u = nodes[(i, 2)]
            v = nodes[(i + 1, 2)]
            for edge_key in G[u][v].keys():
                G[u][v][edge_key]['highway'] = 'motorway'
                G[u][v][edge_key]['maxspeed'] = 100
                G[u][v][edge_key]['lanes'] = 4

        # SR-520 equivalent (horizontal in middle)
        for j in range(10):
            u = nodes[(5, j)]
            v = nodes[(5, j + 1)]
            for edge_key in G[u][v].keys():
                G[u][v][edge_key]['highway'] = 'motorway'
                G[u][v][edge_key]['maxspeed'] = 100
                G[u][v][edge_key]['lanes'] = 3

        print("Created demo network with grid layout")
        return G

    def _process_network_attributes(self):
        """Process and standardize network attributes"""
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            edge_id = (u, v, key)

            # Speed limit (convert to m/s, default based on road type)
            if 'maxspeed' in data:
                try:
                    if isinstance(data['maxspeed'], list):
                        speed_kph = float(data['maxspeed'][0])
                    else:
                        speed_kph = float(data['maxspeed'])
                except (ValueError, TypeError):
                    speed_kph = self._default_speed_for_highway(data.get('highway', 'residential'))
            else:
                speed_kph = self._default_speed_for_highway(data.get('highway', 'residential'))

            self.speed_limits[edge_id] = speed_kph / 3.6  # Convert to m/s

            # Lane count
            if 'lanes' in data:
                try:
                    if isinstance(data['lanes'], list):
                        lanes = int(data['lanes'][0])
                    else:
                        lanes = int(data['lanes'])
                except (ValueError, TypeError):
                    lanes = self._default_lanes_for_highway(data.get('highway', 'residential'))
            else:
                lanes = self._default_lanes_for_highway(data.get('highway', 'residential'))

            self.lane_counts[edge_id] = lanes

            # Road type
            self.road_types[edge_id] = data.get('highway', 'residential')

    def _default_speed_for_highway(self, highway_type: str) -> float:
        """Get default speed limit (km/h) for highway type"""
        speed_map = {
            'motorway': 100,
            'motorway_link': 80,
            'trunk': 90,
            'trunk_link': 70,
            'primary': 80,
            'primary_link': 60,
            'secondary': 60,
            'secondary_link': 50,
            'tertiary': 50,
            'residential': 40,
            'living_street': 20,
            'service': 30
        }
        if isinstance(highway_type, list):
            highway_type = highway_type[0]
        return speed_map.get(highway_type, 50)

    def _default_lanes_for_highway(self, highway_type: str) -> int:
        """Get default lane count for highway type"""
        lane_map = {
            'motorway': 3,
            'motorway_link': 2,
            'trunk': 2,
            'trunk_link': 2,
            'primary': 2,
            'primary_link': 1,
            'secondary': 2,
            'secondary_link': 1,
            'tertiary': 1,
            'residential': 1,
            'living_street': 1,
            'service': 1
        }
        if isinstance(highway_type, list):
            highway_type = highway_type[0]
        return lane_map.get(highway_type, 1)

    def find_route(self, origin: Tuple[float, float], destination: Tuple[float, float]) -> List:
        """
        Find shortest route between two points

        Args:
            origin: (lat, lon) tuple
            destination: (lat, lon) tuple

        Returns:
            List of node IDs representing the route
        """
        if self.graph is None:
            raise ValueError("Network not loaded. Call load_network() first.")

        # Find nearest nodes to origin and destination
        orig_node = ox.distance.nearest_nodes(self.graph, origin[1], origin[0])
        dest_node = ox.distance.nearest_nodes(self.graph, destination[1], destination[0])

        try:
            # Find shortest path
            route = nx.shortest_path(
                self.graph,
                orig_node,
                dest_node,
                weight='length'
            )
            return route
        except nx.NetworkXNoPath:
            print(f"No path found between {origin} and {destination}")
            return []

    def get_edge_info(self, u: int, v: int, key: int = 0) -> Dict:
        """Get information about an edge"""
        edge_id = (u, v, key)
        return {
            'speed_limit': self.speed_limits.get(edge_id, 50 / 3.6),
            'lanes': self.lane_counts.get(edge_id, 1),
            'road_type': self.road_types.get(edge_id, 'residential'),
            'length': self.graph[u][v][key].get('length', 100)
        }

    def get_node_position(self, node_id: int) -> Tuple[float, float]:
        """Get (lat, lon) position of a node"""
        node_data = self.graph.nodes[node_id]
        return (node_data['y'], node_data['x'])

    def is_major_corridor(self, u: int, v: int, key: int = 0) -> bool:
        """Check if edge is part of a major corridor"""
        edge_data = self.graph[u][v][key]
        road_type = edge_data.get('highway', '')

        # Major corridors are motorways and trunks
        if isinstance(road_type, list):
            road_type = road_type[0]

        return road_type in ['motorway', 'motorway_link', 'trunk', 'trunk_link']

    def get_nearby_nodes(self, position: Tuple[float, float], radius: float = 1000) -> List[int]:
        """
        Get nodes within radius (meters) of position

        Args:
            position: (lat, lon) tuple
            radius: Radius in meters

        Returns:
            List of node IDs
        """
        # This is a simplified version - would need proper geospatial calculation
        nearby = []
        for node_id, data in self.graph.nodes(data=True):
            node_pos = (data['y'], data['x'])
            # Rough distance calculation
            dist = np.sqrt(
                ((position[0] - node_pos[0]) * 111000) ** 2 +
                ((position[1] - node_pos[1]) * 111000 * np.cos(np.radians(position[0]))) ** 2
            )
            if dist <= radius:
                nearby.append(node_id)
        return nearby
