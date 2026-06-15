from __future__ import annotations

from typing import Any, Optional

from app.models.vehicle import Vehicle
from app.utils.logger import get_logger


class TraCIClient:
    def __init__(self) -> None:
        self._connected = False
        self.logger = get_logger("traci")

        self._subscribed_edges: set[str] = set()
        self._subscribed_vehicles: set[str] = set()

        self._edge_subscription_vars: list[int] = []
        self._vehicle_subscription_vars: list[int] = []
        self._tl_subscribed: set[str] = set()

        self._cached_tl_ids: list[str] = []

    @property
    def is_connected(self) -> bool:
        return self._connected

    def connect(self, port: int = 8813, num_retries: int = 5) -> None:
        import traci
        import time
        self._init_subscription_vars()
        for attempt in range(num_retries):
            try:
                try:
                    traci.close()
                except Exception:
                    pass
                traci.init(port)
                traci.simulationStep()
                self._connected = True
                self.logger.info(f"Connected to SUMO on port {port}")
                return
            except Exception as e:
                self.logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                time.sleep(1)
        raise ConnectionError(f"Failed to connect to SUMO after {num_retries} attempts")

    def _init_subscription_vars(self) -> None:
        import traci
        LAST_STEP_WAITING_TIME = 0x12
        self._edge_subscription_vars = [
            traci.constants.LAST_STEP_VEHICLE_NUMBER,
            traci.constants.LAST_STEP_MEAN_SPEED,
            LAST_STEP_WAITING_TIME,
        ]
        self._vehicle_subscription_vars = [
            traci.constants.VAR_POSITION,
            traci.constants.VAR_SPEED,
            traci.constants.VAR_ANGLE,
            traci.constants.VAR_ROAD_ID,
            traci.constants.VAR_LANE_INDEX,
            traci.constants.VAR_LANEPOSITION,
            traci.constants.VAR_WAITING_TIME,
            traci.constants.VAR_TYPE,
            traci.constants.VAR_FUELCONSUMPTION,
            traci.constants.VAR_CO2EMISSION,
        ]

    def simulation_step(self) -> None:
        if not self._connected:
            return
        import traci
        traci.simulationStep()

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

    # ── Vehicles ──────────────────────────────────────────────

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

    def add_vehicle(
        self,
        veh_id: str,
        route_id: str,
        veh_type: str = "car",
        depart: str = "now",
        depart_lane: str = "best",
        depart_speed: str = "max",
    ) -> None:
        if not self._connected:
            return
        import traci
        try:
            traci.vehicle.add(
                veh_id, route_id,
                typeID=veh_type,
                depart=depart,
                departLane=depart_lane,
                departSpeed=depart_speed,
            )
        except Exception as e:
            self.logger.warning(f"Failed to add vehicle {veh_id}: {e}")

    # ── Cached / Subscription-based reads ─────────────────────
    # Call subscribe_*() BEFORE simulation_step(), then read with
    # get_*_cached() AFTER the step.  No extra TraCI calls.

    def subscribe_edges(self, edge_ids: list[str]) -> None:
        if not self._connected:
            return
        if not self._edge_subscription_vars:
            self._init_subscription_vars()
        import traci
        new_edges = [eid for eid in edge_ids if eid not in self._subscribed_edges]
        for eid in new_edges:
            traci.edge.subscribe(eid, self._edge_subscription_vars)
            self._subscribed_edges.add(eid)

    def subscribe_vehicles(self, vehicle_ids: list[str]) -> None:
        if not self._connected:
            return
        if not self._vehicle_subscription_vars:
            self._init_subscription_vars()
        import traci
        new_vids = [vid for vid in vehicle_ids if vid not in self._subscribed_vehicles]
        for vid in new_vids:
            traci.vehicle.subscribe(vid, self._vehicle_subscription_vars)
            self._subscribed_vehicles.add(vid)

    def get_vehicle_cached(self, veh_id: str) -> Optional[Vehicle]:
        import traci
        try:
            results = traci.vehicle.getSubscriptionResults(veh_id)
            if not results:
                return None
            pos = results.get(traci.constants.VAR_POSITION)
            if pos is None:
                return None
            return Vehicle(
                id=veh_id,
                vehicle_type=results.get(traci.constants.VAR_TYPE, "car"),
                x=pos[0],
                y=pos[1],
                speed=results.get(traci.constants.VAR_SPEED, 0.0),
                angle=results.get(traci.constants.VAR_ANGLE, 0.0),
                edge_id=results.get(traci.constants.VAR_ROAD_ID, ""),
                lane_index=results.get(traci.constants.VAR_LANE_INDEX, 0),
                lane_position=results.get(traci.constants.VAR_LANEPOSITION, 0.0),
                waiting_time=results.get(traci.constants.VAR_WAITING_TIME, 0.0),
                fuel=results.get(traci.constants.VAR_FUELCONSUMPTION, 0.0),
                co2=results.get(traci.constants.VAR_CO2EMISSION, 0.0),
            )
        except Exception:
            return None

    def get_all_vehicles_cached(self) -> list[Vehicle]:
        import traci
        try:
            all_ids = traci.vehicle.getIDList()
        except Exception:
            return []
        result: list[Vehicle] = []
        uncached_ids: list[str] = []
        for vid in all_ids:
            v = self.get_vehicle_cached(vid)
            if v is not None:
                result.append(v)
            else:
                uncached_ids.append(vid)
        for vid in uncached_ids:
            v = self.get_vehicle(vid)
            if v is not None:
                result.append(v)
        return result

    def get_edge_data_cached(self, edge_id: str) -> Optional[dict[str, float]]:
        import traci
        try:
            results = traci.edge.getSubscriptionResults(edge_id)
            if not results:
                return None
            return {
                "vehicle_count": results.get(traci.constants.LAST_STEP_VEHICLE_NUMBER, 0),
                "mean_speed": results.get(traci.constants.LAST_STEP_MEAN_SPEED, 0.0),
                "waiting_time": results.get(traci.constants.LAST_STEP_WAITING_TIME, 0.0),
            }
        except Exception:
            return None

    def get_all_edge_data_cached(self) -> dict[str, dict[str, float]]:
        result: dict[str, dict[str, float]] = {}
        for eid in self._subscribed_edges:
            data = self.get_edge_data_cached(eid)
            if data:
                result[eid] = data
        return result

    def clear_subscriptions(self) -> None:
        self._subscribed_edges.clear()
        self._subscribed_vehicles.clear()
        self._tl_subscribed.clear()

    # ── Traffic Lights ────────────────────────────────────────

    def get_tl_ids(self) -> list[str]:
        if self._cached_tl_ids:
            return self._cached_tl_ids
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

    def get_tl_state(self, tl_id: str) -> str:
        if not self._connected:
            return ""
        import traci
        try:
            return traci.trafficlight.getRedYellowGreenState(tl_id)
        except Exception:
            return ""

    def get_tl_junction_id(self, tl_id: str) -> str:
        return ""

    # ── TL Subscriptions (zero socket calls for GUI reads) ────

    def subscribe_tl(self, tl_id: str) -> None:
        if not self._connected:
            return
        import traci
        try:
            traci.trafficlight.subscribe(
                tl_id, [traci.constants.TL_RED_YELLOW_GREEN_STATE],
            )
            self._tl_subscribed.add(tl_id)
        except Exception as e:
            self.logger.warning(f"Failed to subscribe TL {tl_id}: {e}")

    def subscribe_all_tls(self, tl_ids: list[str]) -> None:
        for tid in tl_ids:
            self.subscribe_tl(tid)

    def cache_tl_data(self) -> None:
        import traci
        try:
            self._cached_tl_ids = list(traci.trafficlight.getIDList())
        except Exception as e:
            self.logger.warning(f"Failed to cache TL data: {e}")

    def get_cached_tl_state(self, tl_id: str) -> str:
        import traci
        try:
            results = traci.trafficlight.getSubscriptionResults(tl_id)
            if results:
                return results.get(traci.constants.TL_RED_YELLOW_GREEN_STATE, "")
        except Exception:
            pass
        return ""

    def get_tl_program(self, tl_id: str) -> list[dict[str, Any]]:
        if not self._connected:
            return []
        import traci
        try:
            logic = traci.trafficlight.getCompleteRedYellowGreenDefinition(tl_id)
            phases = []
            for log in logic:
                for p in log.phases:
                    phases.append({
                        "index": p.index,
                        "state": p.state,
                        "duration": p.duration,
                        "next": p.next,
                    })
            return phases
        except Exception:
            return []

    def set_tl_phase(self, tl_id: str, phase: int) -> None:
        if not self._connected:
            return
        import traci
        try:
            traci.trafficlight.setPhase(tl_id, phase)
        except Exception as e:
            self.logger.warning(f"set_tl_phase {tl_id}: {e}")

    def set_tl_phase_duration(self, tl_id: str, duration: float) -> None:
        if not self._connected:
            return
        import traci
        try:
            traci.trafficlight.setPhaseDuration(tl_id, duration)
        except Exception as e:
            self.logger.warning(f"set_tl_phase_duration {tl_id}: {e}")

    def get_controlled_links(self, tl_id: str) -> list[tuple[str, str, str]]:
        if not self._connected:
            return []
        import traci
        try:
            result: list[tuple[str, str, str]] = []
            links = traci.trafficlight.getControlledLinks(tl_id)
            for phase_links in links:
                for link in phase_links:
                    if link:
                        from_lane, via, to_lane = link[0], "", ""
                        parts = from_lane.split("_")
                        edge_id = parts[0] if parts else ""
                        result.append((edge_id, from_lane, to_lane))
            return result
        except Exception:
            return []

    # ── Edges ─────────────────────────────────────────────────

    def get_edge_ids(self) -> list[str]:
        if not self._connected:
            return []
        import traci
        return list(traci.edge.getIDList())

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

    # ── Fuel & Emissions ──────────────────────────────────────

    def get_fuel_consumption(self, veh_id: str) -> float:
        if not self._connected:
            return 0.0
        import traci
        try:
            return traci.vehicle.getFuelConsumption(veh_id)
        except Exception:
            return 0.0

    def get_co2_emission(self, veh_id: str) -> float:
        if not self._connected:
            return 0.0
        import traci
        try:
            return traci.vehicle.getCO2Emission(veh_id)
        except Exception:
            return 0.0

    def cleanup_subscribed_vehicles(self, active_ids: list[str]) -> None:
        active_set = set(active_ids)
        stale = self._subscribed_vehicles - active_set
        if stale:
            import traci
            for vid in stale:
                try:
                    traci.vehicle.unsubscribe(vid)
                except Exception:
                    pass
            self._subscribed_vehicles -= stale

    def get_total_fuel_consumption(self) -> float:
        if not self._connected:
            return 0.0
        import traci
        try:
            total = 0.0
            for vid in traci.vehicle.getIDList():
                results = traci.vehicle.getSubscriptionResults(vid)
                if results:
                    total += results.get(traci.constants.VAR_FUELCONSUMPTION, 0.0)
                else:
                    total += traci.vehicle.getFuelConsumption(vid)
            return total
        except Exception:
            return 0.0

    def get_total_co2_emission(self) -> float:
        if not self._connected:
            return 0.0
        import traci
        try:
            total = 0.0
            for vid in traci.vehicle.getIDList():
                results = traci.vehicle.getSubscriptionResults(vid)
                if results:
                    total += results.get(traci.constants.VAR_CO2EMISSION, 0.0)
                else:
                    total += traci.vehicle.getCO2Emission(vid)
            return total
        except Exception:
            return 0.0

    # ── Lanes ─────────────────────────────────────────────────

    def get_lane_ids(self) -> list[str]:
        if not self._connected:
            return []
        import traci
        return list(traci.lane.getIDList())

    def get_lane_vehicle_count(self, lane_id: str) -> int:
        if not self._connected:
            return 0
        import traci
        try:
            return traci.lane.getLastStepVehicleNumber(lane_id)
        except Exception:
            return 0

    def get_lane_mean_speed(self, lane_id: str) -> float:
        if not self._connected:
            return 0.0
        import traci
        try:
            return traci.lane.getLastStepMeanSpeed(lane_id)
        except Exception:
            return 0.0

    def get_lane_waiting_time(self, lane_id: str) -> float:
        if not self._connected:
            return 0.0
        import traci
        try:
            return traci.lane.getWaitingTime(lane_id)
        except Exception:
            return 0.0

    def get_lane_occupancy(self, lane_id: str) -> float:
        if not self._connected:
            return 0.0
        import traci
        try:
            return traci.lane.getLastStepOccupancy(lane_id)
        except Exception:
            return 0.0

    # ── Detectors ─────────────────────────────────────────────

    def get_detector_ids(self) -> list[str]:
        if not self._connected:
            return []
        import traci
        return list(traci.inductionloop.getIDList())

    def get_detector_vehicle_count(self, detector_id: str) -> int:
        if not self._connected:
            return 0
        import traci
        try:
            return traci.inductionloop.getLastStepVehicleNumber(detector_id)
        except Exception:
            return 0

    # ── Connection lifecycle ──────────────────────────────────

    def close(self) -> None:
        if self._connected:
            import traci
            try:
                traci.close()
            except Exception:
                pass
            self._connected = False
            self._subscribed_edges.clear()
            self._subscribed_vehicles.clear()
            self._cached_tl_ids.clear()
            self.logger.info("Disconnected from SUMO")
