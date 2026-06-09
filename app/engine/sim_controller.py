"""
Simulation Controller

Manages the SUMO process lifecycle and simulation loop.
Coordinates TraCI client, TL algorithms, metrics collection, and GUI updates.
"""

from __future__ import annotations
import os
import subprocess
import threading
import time
from typing import Optional, Callable

from app.engine.traci_client import TraCIClient
from app.utils.logger import get_logger


class SimController:
    def __init__(self, config):
        self.config = config
        self.logger = get_logger("sim")
        self.traci = TraCIClient()
        self.sumo_process: Optional[subprocess.Popen] = None
        self._running = False
        self._paused = False
        self._thread: Optional[threading.Thread] = None
        self.sim_speed: float = 1.0
        self.current_time: float = 0.0
        self._listeners: dict[str, list[Callable]] = {
            "step": [],
            "start": [],
            "pause": [],
            "resume": [],
            "stop": [],
            "error": [],
        }

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_paused(self) -> bool:
        return self._paused

    def on(self, event: str, callback: Callable):
        if event in self._listeners:
            self._listeners[event].append(callback)

    def _emit(self, event: str, *args):
        for cb in self._listeners.get(event, []):
            try:
                cb(*args)
            except Exception as e:
                self.logger.error(f"Listener error on {event}: {e}")

    def start(self, sumo_cfg_path: str, port: int = 8813):
        if self._running:
            self.logger.warning("Simulation already running")
            return

        sumo_bin = self.config.get_sumo_binary()
        if not os.path.exists(sumo_cfg_path):
            raise FileNotFoundError(f"SUMO config not found: {sumo_cfg_path}")

        cmd = [
            sumo_bin,
            "-c", sumo_cfg_path,
            "--remote-port", str(port),
            "--step-length", str(self.config.get("simulation", "step_length")),
            "--no-warnings",
        ]

        try:
            self.sumo_process = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            self.traci.connect(port=port)
            self._running = True
            self._paused = False
            self.current_time = 0.0
            self.logger.info("Simulation started")
            self._emit("start")
            self._run_loop()
        except Exception as e:
            self.logger.error(f"Failed to start simulation: {e}")
            self._emit("error", str(e))
            self.stop()

    def _run_loop(self):
        while self._running:
            if not self._paused:
                try:
                    self.traci.simulation_step()
                    self.current_time = self.traci.get_simulation_time()
                    self._emit("step", self.current_time)
                except Exception as e:
                    self.logger.error(f"Simulation step error: {e}")
                    self._emit("error", str(e))
                    self.stop()
                    break
                sleep_time = 1.0 / (30.0 * self.sim_speed)
                time.sleep(max(0.001, sleep_time))
            else:
                time.sleep(0.1)

    def step_single(self):
        if not self._running:
            return
        try:
            self.traci.simulation_step()
            self.current_time = self.traci.get_simulation_time()
            self._emit("step", self.current_time)
        except Exception as e:
            self.logger.error(f"Single step error: {e}")

    def pause(self):
        if self._running and not self._paused:
            self._paused = True
            self._emit("pause")
            self.logger.info("Simulation paused")

    def resume(self):
        if self._running and self._paused:
            self._paused = False
            self._emit("resume")
            self.logger.info("Simulation resumed")

    def set_speed(self, speed: float):
        self.sim_speed = max(0.1, min(10.0, speed))

    def stop(self):
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
