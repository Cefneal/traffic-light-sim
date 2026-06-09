"""
Road Network Model

Represents a graph of intersections (nodes) and road segments (edges).
Parsed from SUMO .net.xml files.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Node:
    id: str
    x: float
    y: float
    node_type: str = "priority"
    traffic_light_id: Optional[str] = None

    @property
    def is_signalized(self) -> bool:
        return self.traffic_light_id is not None


@dataclass
class Lane:
    id: str
    index: int
    speed: float
    length: float
    shape: list[tuple[float, float]] = field(default_factory=list)

    @property
    def max_speed_kmh(self) -> float:
        return self.speed * 3.6


@dataclass
class Edge:
    id: str
    from_node: str
    to_node: str
    name: str = ""
    length: float = 0.0
    max_speed: float = 13.89
    lane_count: int = 1
    lanes: list[Lane] = field(default_factory=list)

    @property
    def max_speed_kmh(self) -> float:
        return self.max_speed * 3.6


@dataclass
class TrafficLightLogic:
    id: str
    node_id: str
    phases: list[dict] = field(default_factory=list)
    current_phase_index: int = 0

    @property
    def current_phase(self) -> Optional[dict]:
        if 0 <= self.current_phase_index < len(self.phases):
            return self.phases[self.current_phase_index]
        return None


class RoadNetwork:
    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, Edge] = {}
        self.traffic_lights: dict[str, TrafficLightLogic] = {}
        self.bounds: tuple[float, float, float, float] = (0, 0, 0, 0)

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge):
        self.edges[edge.id] = edge

    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)

    def get_edge(self, edge_id: str) -> Optional[Edge]:
        return self.edges.get(edge_id)

    def get_outgoing_edges(self, node_id: str) -> list[Edge]:
        return [e for e in self.edges.values() if e.from_node == node_id]

    def get_incoming_edges(self, node_id: str) -> list[Edge]:
        return [e for e in self.edges.values() if e.to_node == node_id]

    def get_signalized_nodes(self) -> list[Node]:
        return [n for n in self.nodes.values() if n.is_signalized]

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    @property
    def tl_count(self) -> int:
        return len(self.traffic_lights)

    def summary(self) -> dict:
        return {
            "nodes": self.node_count,
            "edges": self.edge_count,
            "traffic_lights": self.tl_count,
            "bounds": self.bounds,
        }
