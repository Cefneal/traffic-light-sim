"""
TraCI Client

Wrapper around SUMO's TraCI interface for controlling simulation.
Provides methods for vehicles, traffic lights, edges, lanes, and detectors.
"""

from __future__ import annotations
from typing import Optional

from app.models.vehicle import Vehicle
from app.utils.logger import get_logger


class TraCIClient:
    def __init__(self):
        self._connected = False
        self.logger = get_logger("traci")

    @property
    def is_connected(self) -> bool:
        return self._connected

    def get_vehicle_ids(self) -> list[str]:
        if not self._connected:
            return []
        import traci
        return list(traci.vehicle.getIDList())

    def get_vehicle(self, veh_id: str) -> Optional[Vehicle]:
        if not self._connected:
            return None
        import traci
        try:
            pos = traci.vehicle.getPosition(veh_id)
            return Vehicle(
                id=veh_id,
                vehicle_type=traci.vehicle.getTypeID(veh_id),
                x=pos[0],
                y=pos[1],
                speed=traci.vehicle.getSpeed(veh_id),
                angle=traci.vehicle.getAngle(veh_id),
                edge_id=traci.vehicle.getRoadID(veh_id),
                lane_index=traci.vehicle.getLaneIndex(veh_id),
                lane_position=traci.vehicle.getLanePosition(veh_id),
                waiting_time=traci.vehicle.getWaitingTime(veh_id),
            )
        except Exception as e:
            self.logger.warning(f"Failed to get vehicle {veh_id}: {e}")
            return None

    def get_all_vehicles(self) -> list[Vehicle]:
        return [
            v for vid in self.get_vehicle_ids()
            if (v := self.get_vehicle(vid)) is not None
        ]

    def get_edge_vehicle_count(self, edge_id: str) -> int:
        if not self._connected:
            return 0
        import traci
        try:
            return traci.edge.getLastStepVehicleNumber(edge_id)
        except Exception:
            return 0

    def get_edge_mean_speed(self, edge_id: str) -> float:
        if not self._connected:
            return 0.0
        import traci
        try:
            return traci.edge.getLastStepMeanSpeed(edge_id)
        except Exception:
            return 0.0

    def get_edge_waiting_time(self, edge_id: str) -> float:
        if not self._connected:
            return 0.0
        import traci
        try:
            return traci.edge.getWaitingTime(edge_id)
        except Exception:
            return 0.0

    def get_tl_ids(self) -> list[str]:
        if not self._connected:
            return []
        import traci
        return list(traci.trafficlight.getIDList())

    def get_tl_phase(self, tl_id: str) -> int:
        if not self._connected:
            return 0
        import traci
        try:
            return traci.trafficlight.getPhase(tl_id)
        except Exception:
            return 0

    def set_tl_phase(self, tl_id: str, phase: int):
        if not self._connected:
            return
        import traci
        try:
            traci.trafficlight.setPhase(tl_id, phase)
        except Exception as e:
            self.logger.warning(f"Failed to set TL phase {tl_id}: {e}")

    def set_tl_phase_duration(self, tl_id: str, duration: float):
        if not self._connected:
            return
        import traci
        try:
            traci.trafficlight.setPhaseDuration(tl_id, duration)
        except Exception as e:
            self.logger.warning(f"Failed to set TL duration {tl_id}: {e}")

    def get_detector_vehicle_count(self, detector_id: str) -> int:
        if not self._connected:
            return 0
        import traci
        try:
            return traci.inductionloop.getLastStepVehicleNumber(detector_id)
        except Exception:
            return 0

    def get_simulation_time(self) -> float:
        if not self._connected:
            return 0.0
        import traci
        return traci.simulation.getTime()

    def get_remaining_vehicles(self) -> int:
        if not self._connected:
            return 0
        import traci
        return traci.simulation.getMinExpectedNumber()

    def add_vehicle(self, veh_id: str, route_id: str, veh_type: str = "car",
                    depart: str = "now", depart_lane: str = "best",
                    depart_speed: str = "max"):
        if not self._connected:
            return
        import traci
        try:
            traci.vehicle.add(veh_id, route_id, typeID=veh_type,
                            depart=depart, departLane=depart_lane,
                            departSpeed=depart_speed)
        except Exception as e:
            self.logger.warning(f"Failed to add vehicle {veh_id}: {e}")

    def subscribe_edges(self, edge_ids: list[str]):
        if not self._connected:
            return
        import traci
        for eid in edge_ids:
            traci.edge.subscribe(eid, [
                traci.constants.LAST_STEP_VEHICLE_NUMBER,
                traci.constants.LAST_STEP_MEAN_SPEED,
                traci.constants.LAST_STEP_WAITING_TIME,
            ])

    def get_detector_ids(self) -> list[str]:
        if not self._connected:
            return []
        import traci
        return list(traci.inductionloop.getIDList())

    def connect(self, port: int = 8813, num_retries: int = 5):
        import traci
        import time
        for attempt in range(num_retries):
            try:
                traci.init(port)
                traci.simulationStep()
                self._connected = True
                self.logger.info(f"Connected to SUMO on port {port}")
                return
            except Exception as e:
                self.logger.warning(f"Connection attempt {attempt+1} failed: {e}")
                time.sleep(1)
        raise ConnectionError(f"Failed to connect to SUMO after {num_retries} attempts")

    def simulation_step(self):
        if not self._connected:
            return
        import traci
        traci.simulationStep()

    def close(self):
        if self._connected:
            import traci
            try:
                traci.close()
            except Exception:
                pass
            self._connected = False
            self.logger.info("Disconnected from SUMO")
