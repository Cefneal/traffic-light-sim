"""
Vehicle Model

Represents a single vehicle in the simulation.
Data is synced from SUMO via TraCI each simulation step.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


VEHICLE_TYPES = {
    "car": {"length": 4.5, "width": 1.8, "max_speed": 50.0, "color": "#3498db"},
    "truck": {"length": 10.0, "width": 2.5, "max_speed": 30.0, "color": "#e67e22"},
    "bus": {"length": 12.0, "width": 2.5, "max_speed": 25.0, "color": "#f1c40f"},
    "emergency": {"length": 5.0, "width": 1.9, "max_speed": 60.0, "color": "#e74c3c"},
    "motorcycle": {"length": 2.0, "width": 0.8, "max_speed": 60.0, "color": "#2ecc71"},
}

COLORS = {
    "car": (52, 152, 219),
    "truck": (230, 126, 34),
    "bus": (241, 196, 15),
    "emergency": (231, 76, 60),
    "motorcycle": (46, 204, 113),
}


@dataclass
class Vehicle:
    id: str
    vehicle_type: str = "car"
    x: float = 0.0
    y: float = 0.0
    speed: float = 0.0
    angle: float = 0.0
    edge_id: str = ""
    lane_index: int = 0
    lane_position: float = 0.0
    waiting_time: float = 0.0
    route: list[str] = field(default_factory=list)
    color: tuple[int, int, int] = (52, 152, 219)

    def __post_init__(self):
        if self.color == (52, 152, 219):
            self.color = COLORS.get(self.vehicle_type, (52, 152, 219))

    @property
    def speed_kmh(self) -> float:
        return self.speed * 3.6

    @property
    def is_moving(self) -> bool:
        return self.speed > 0.1

    @property
    def is_waiting(self) -> bool:
        return self.waiting_time > 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.vehicle_type,
            "x": self.x,
            "y": self.y,
            "speed": self.speed,
            "edge": self.edge_id,
            "lane": self.lane_index,
        }
