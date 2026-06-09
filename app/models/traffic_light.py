"""
Traffic Light Model

Represents traffic light state, phases, and control logic.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable


class TLState(Enum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"
    RED_YELLOW = "red_yellow"
    OFF = "off"
    FLASHING = "flashing"


class TLAlgorithm(Enum):
    FIXED_TIME = "fixed"
    ACTUATED = "actuated"
    MAX_PRESSURE = "max_pressure"
    GREEN_WAVE = "green_wave"


@dataclass
class TLPhase:
    index: int
    state: str
    duration: float
    next: int = -1


@dataclass
class TrafficLight:
    id: str
    node_id: str
    algorithm: TLAlgorithm = TLAlgorithm.FIXED_TIME
    algorithm_fn: Optional[Callable] = None
    phases: list[TLPhase] = field(default_factory=list)
    current_phase_index: int = 0
    phase_start_time: float = 0.0
    cycle_time: float = 60.0
    # For actuated
    min_green: float = 10.0
    max_green: float = 45.0
    extension: float = 3.0
    gap_out: float = 3.0
    gap_timer: float = 0.0
    # For max pressure
    pressure_interval: float = 10.0
    last_pressure_calc: float = 0.0
    # For green wave
    offset: float = 0.0

    @property
    def current_phase(self) -> Optional[TLPhase]:
        if 0 <= self.current_phase_index < len(self.phases):
            return self.phases[self.current_phase_index]
        return None

    def get_elapsed(self, sim_time: float) -> float:
        return sim_time - self.phase_start_time

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "node_id": self.node_id,
            "algorithm": self.algorithm.value,
            "current_phase": self.current_phase_index,
            "phases": [(p.state, p.duration) for p in self.phases],
        }
