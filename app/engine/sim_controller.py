from __future__ import annotations

import os
import subprocess
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from app.engine.tl_algorithms import AlgorithmFn, get_controller
from app.engine.traci_client import TraCIClient
from app.metrics.collector import MetricsCollector
from app.models.traffic_light import TLPhase, TrafficLight
from app.models.vehicle import Vehicle
from app.utils.logger import get_logger


@dataclass
class StepSnapshot:
    time: float = 0.0
    vehicles: tuple = ()
    tl_states: dict = field(default_factory=dict)
    edge_data: dict = field(default_factory=dict)
    vehicle_count: int = 0
    remaining_vehicles: int = 0
    avg_speed: float = 0.0
    avg_wait: float = 0.0
    queue: int = 0
    fuel: float = 0.0
    co2: float = 0.0


class SimController:
    def __init__(self, config) -> None:
        self.config = config
        self.logger = get_logger("sim")
        self.traci = TraCIClient()
        self.sumo_process: Optional[subprocess.Popen] = None
        self._running = False
        self._paused = False
        self._thread: Optional[threading.Thread] = None
        self.sim_speed: float = 1.0
        self.current_time: float = 0.0

        self._algorithm_name: str = "fixed"
        self._algorithm_fn: AlgorithmFn = get_controller("fixed")
        self._algorithm_config: dict[str, Any] = {}
        self._traffic_lights: dict[str, TrafficLight] = {}

        self.collector = MetricsCollector(max_samples=7200)

        self._step_snapshot = StepSnapshot()
        self._step_lock = threading.Lock()

        self._listeners: dict[str, list[Callable]] = {
            "step": [],
            "start": [],
            "pause": [],
            "resume": [],
            "stop": [],
            "error": [],
        }

    # ── Properties ────────────────────────────────────────────

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_paused(self) -> bool:
        return self._paused

    @property
    def algorithm(self) -> str:
        return self._algorithm_name

    # ── Event system ──────────────────────────────────────────

    def on(self, event: str, callback: Callable) -> None:
        if event in self._listeners:
            self._listeners[event].append(callback)

    def off(self, event: str, callback: Callable) -> None:
        if event in self._listeners:
            self._listeners[event] = [cb for cb in self._listeners[event] if cb is not callback]

    def _emit(self, event: str, *args: Any) -> None:
        for cb in self._listeners.get(event, []):
            try:
                cb(*args)
            except Exception as e:
                self.logger.error(f"Listener error on {event}: {e}")

    # ── Algorithm config ──────────────────────────────────────

    def set_algorithm(self, name: str, config: Optional[dict] = None) -> None:
        self._algorithm_name = name
        self._algorithm_fn = get_controller(name)
        if config:
            self._algorithm_config = config
        self.logger.info(f"Algorithm set to {name} with {config}")

    def get_step_snapshot(self) -> StepSnapshot:
        with self._step_lock:
            return self._step_snapshot

    # ── Traffic light building ────────────────────────────────

    def _build_traffic_lights(self) -> None:
        import traci

        self._traffic_lights.clear()
        tl_ids = self.traci.get_tl_ids()

        for tid in tl_ids:
            try:
                logic_list = traci.trafficlight.getCompleteRedYellowGreenDefinition(tid)
                phases: list[TLPhase] = []
                node_id = ""

                for log in logic_list:
                    for i, p in enumerate(log.phases):
                        phases.append(TLPhase(
                            index=i,
                            state=p.state,
                            duration=p.duration,
                            next=p.next if isinstance(p.next, int) else (p.next[0] if p.next else -1),
                        ))

                tl = TrafficLight(
                    id=tid,
                    node_id=node_id,
                    phases=phases,
                    current_phase_index=0,
                    phase_start_time=self.current_time,
                )

                cfg = self._algorithm_config
                if "cycle_time" in cfg:
                    tl.cycle_time = cfg["cycle_time"]
                if "min_green" in cfg:
                    tl.min_green = cfg["min_green"]
                if "max_green" in cfg:
                    tl.max_green = cfg["max_green"]

                self._traffic_lights[tid] = tl
            except Exception as e:
                self.logger.warning(f"Failed to build TL {tid}: {e}")

        self.traci.subscribe_all_tls(list(self._traffic_lights.keys()))
        self.traci.cache_tl_data()
        self.logger.info(f"Built {len(self._traffic_lights)} traffic lights")

    # ── Simulation lifecycle ──────────────────────────────────

    def start(self, sumo_cfg_path: str, port: int = 8813) -> None:
        if self._running:
            self.logger.warning("Simulation already running")
            return

        if not sumo_cfg_path or not os.path.exists(sumo_cfg_path):
            self.logger.error(f"Config file not found: {sumo_cfg_path}")
            self._emit("error", f"Config file not found: {sumo_cfg_path}")
            return

        sumo_bin = self.config.get_sumo_binary()
        if not sumo_bin:
            self.logger.error("SUMO binary not found. Install SUMO or set TLS_SUMO_PATH")
            self._emit("error", "SUMO binary not found. Install SUMO or set TLS_SUMO_PATH")
            return

        cmd = [
            sumo_bin,
            "-c", sumo_cfg_path,
            "--remote-port", str(port),
            "--step-length", str(self.config.get("simulation", "step_length")),
            "--no-warnings",
        ]

        try:
            self.sumo_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            time.sleep(1.5)
            if self.sumo_process.poll() is not None:
                _, stderr = self.sumo_process.communicate()
                error_msg = stderr.decode().strip() if stderr else "Unknown error"
                self.logger.error(f"SUMO failed to start:\n{error_msg}")
                self._emit("error", f"SUMO failed to start:\n{error_msg}")
                self.sumo_process = None
                return

            self.traci.connect(port=port)
            self._running = True
            self._paused = False
            self.current_time = 0.0
            self.collector.clear()

            self._build_traffic_lights()

            try:
                all_edge_ids = self.traci.get_edge_ids()
                self.traci.subscribe_edges(all_edge_ids)
                self.logger.info(f"Subscribed to {len(all_edge_ids)} edges")
            except Exception as e:
                self.logger.warning(f"Edge subscription failed: {e}")

            self.logger.info(f"Simulation started | algorithm={self._algorithm_name}")
            self._emit("start")
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
        except Exception as e:
            self.logger.error(f"Failed to start simulation: {e}")
            self._emit("error", str(e))
            self.stop()

    def _run_loop(self) -> None:
        import traci

        step_length = float(self.config.get("simulation", "step_length") or 1.0)
        target_fps = 30.0

        while self._running:
            if not self._paused:
                step_start = time.perf_counter()
                try:
                    self.traci.simulation_step()
                    self.current_time = self.traci.get_simulation_time()

                    try:
                        veh_ids = self.traci.get_vehicle_ids()
                    except Exception:
                        veh_ids = []
                    try:
                        self.traci.subscribe_vehicles(veh_ids)
                    except Exception:
                        pass
                    try:
                        self.traci.cleanup_subscribed_vehicles(veh_ids)
                    except Exception:
                        pass

                    # ── Metrics & TL state (cached reads) ──────
                    vehs = self.traci.get_all_vehicles_cached()
                    if not vehs:
                        vehs = self.traci.get_all_vehicles()

                    avg_speed = sum(v.speed for v in vehs) / len(vehs) if vehs else 0.0
                    avg_wait = sum(v.waiting_time for v in vehs) / len(vehs) if vehs else 0.0
                    queue = sum(1 for v in vehs if v.speed < 0.1) if vehs else 0

                    total_fuel = self.traci.get_total_fuel_consumption()
                    total_co2 = self.traci.get_total_co2_emission()

                    self.collector.record(
                        time_step=self.current_time,
                        speed=avg_speed,
                        waiting_time=avg_wait,
                        throughput=len(vehs),
                        queue_length=queue,
                        fuel=total_fuel,
                        co2=total_co2,
                    )

                    # ── TL algorithm dispatch ──────────────────
                    for tl in self._traffic_lights.values():
                        try:
                            self._algorithm_fn(tl, traci, self.current_time, step_length)
                        except Exception as e:
                            self.logger.warning(f"TL algo {tl.id}: {e}")

                    # ── Build shared snapshot for GUI thread ───
                    tl_states: dict[str, str] = {}
                    for tid in self._traffic_lights:
                        state = self.traci.get_cached_tl_state(tid)
                        if state:
                            tl_states[tid] = state

                    edge_data = self.traci.get_all_edge_data_cached()

                    remaining = self.traci.get_remaining_vehicles()
                    snapshot = StepSnapshot(
                        time=self.current_time,
                        vehicles=tuple(vehs),
                        tl_states=tl_states,
                        edge_data=edge_data,
                        vehicle_count=len(vehs),
                        remaining_vehicles=remaining,
                        avg_speed=avg_speed,
                        avg_wait=avg_wait,
                        queue=queue,
                        fuel=total_fuel,
                        co2=total_co2,
                    )
                    with self._step_lock:
                        self._step_snapshot = snapshot

                    # ── Emit step ───────────────────────────────
                    self._emit("step", {
                        "time": self.current_time,
                        "vehicles": len(vehs),
                        "avg_speed": avg_speed,
                        "avg_wait": avg_wait,
                        "queue": queue,
                        "fuel": total_fuel,
                        "co2": total_co2,
                    })

                except Exception as e:
                    self.logger.error(f"Simulation step error: {e}")
                    self._emit("error", str(e))
                    self.stop()
                    break

                elapsed = time.perf_counter() - step_start
                target_interval = 1.0 / (target_fps * self.sim_speed)
                time.sleep(max(0.001, target_interval - elapsed))
            else:
                time.sleep(0.1)

    def step_single(self) -> None:
        if not self._running:
            return
        import traci
        step_length = float(self.config.get("simulation", "step_length") or 1.0)
        try:
            self.traci.simulation_step()
            self.current_time = self.traci.get_simulation_time()
            for tl in self._traffic_lights.values():
                try:
                    self._algorithm_fn(tl, traci, self.current_time, step_length)
                except Exception as e:
                    self.logger.warning(f"TL algo {tl.id}: {e}")
            self._emit("step", {"time": self.current_time})
        except Exception as e:
            self.logger.error(f"Single step error: {e}")

    # ── Controls ──────────────────────────────────────────────

    def pause(self) -> None:
        if self._running and not self._paused:
            self._paused = True
            self._emit("pause")
            self.logger.info("Simulation paused")

    def resume(self) -> None:
        if self._running and self._paused:
            self._paused = False
            self._emit("resume")
            self.logger.info("Simulation resumed")

    def set_speed(self, speed: float) -> None:
        self.sim_speed = max(0.1, min(10.0, speed))

    def stop(self) -> None:
        self._running = False
        self._paused = False
        try:
            self.traci.close()
        except Exception:
            pass
        if self.sumo_process and self.sumo_process.poll() is None:
            self.sumo_process.terminate()
            try:
                self.sumo_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.sumo_process.kill()
        self.sumo_process = None
        self._emit("stop")
        self.logger.info("Simulation stopped")
