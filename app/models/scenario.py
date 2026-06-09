"""
Scenario Model

Configuration for a simulation scenario.
Can be saved/loaded from SQLite (via storage) or generated as SUMO XML.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Any


@dataclass
class VehicleFlow:
    edge_id: str
    vehs_per_hour: int = 500
    vehicle_type: str = "car"
    depart_lane: str = "best"
    depart_speed: str = "max"
    begin: float = 0.0
    end: float = 3600.0


@dataclass
class TLConfig:
    algorithm: str = "fixed"
    cycle_time: float = 60.0
    params: dict = field(default_factory=dict)


@dataclass
class Scenario:
    id: int = 0
    name: str = "New Scenario"
    description: str = ""
    network_path: str = ""
    route_path: str = ""
    additional_path: str = ""
    tl_algorithm: str = "fixed"
    tl_config: dict = field(default_factory=dict)
    vehicle_flows: list[VehicleFlow] = field(default_factory=list)
    duration: float = 3600.0
    step_length: float = 1.0
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "network_path": self.network_path,
            "route_path": self.route_path,
            "additional_path": self.additional_path,
            "tl_algorithm": self.tl_algorithm,
            "tl_config": self.tl_config,
            "vehicle_flows": [
                {
                    "edge": f.edge_id,
                    "vehs_per_hour": f.vehs_per_hour,
                    "type": f.vehicle_type,
                }
                for f in self.vehicle_flows
            ],
            "duration": self.duration,
        }

    def generate_sumo_config(self) -> str:
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            "<configuration>",
            f'    <input>',
            f'        <net-file value="{self.network_path}"/>',
            f'        <route-files value="{self.route_path}"/>',
        ]
        if self.additional_path:
            lines.append(f'        <additional-files value="{self.additional_path}"/>')
        lines += [
            f'    </input>',
            f'    <time>',
            f'        <begin value="0"/>',
            f'        <end value="{self.duration}"/>',
            f'        <step-length value="{self.step_length}"/>',
            f'    </time>',
            "</configuration>",
        ]
        return "\n".join(lines)

    @staticmethod
    def from_dict(data: dict) -> Scenario:
        flows = [
            VehicleFlow(edge=f["edge"], vehs_per_hour=f.get("vehs_per_hour", 500))
            for f in data.get("vehicle_flows", [])
        ]
        return Scenario(
            id=data.get("id", 0),
            name=data.get("name", "New Scenario"),
            description=data.get("description", ""),
            network_path=data.get("network_path", ""),
            route_path=data.get("route_path", ""),
            additional_path=data.get("additional_path", ""),
            tl_algorithm=data.get("tl_algorithm", "fixed"),
            tl_config=data.get("tl_config", {}),
            vehicle_flows=flows,
            duration=data.get("duration", 3600.0),
        )
