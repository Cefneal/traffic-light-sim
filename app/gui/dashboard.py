import csv
import json
from pathlib import Path

from app.utils.qt_compat import QWidget, QVBoxLayout, QLabel, QTabWidget, QTimer, QFont
import pyqtgraph as pg

from app.metrics.storage import MetricsStorage
from app.utils.logger import get_logger


class DashboardPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.logger = get_logger("dashboard")
        self.sim_controller = None
        self._data = {
            "speed": [],
            "wait_time": [],
            "throughput": [],
            "queue": [],
            "fuel": [],
            "co2": [],
            "time": [],
        }
        self._storage = MetricsStorage()
        self._setup_ui()
        self._timer = QTimer()
        self._timer.setInterval(500)
        self._timer.timeout.connect(self._update_charts)
        self._timer.start()

    def set_sim_controller(self, controller):
        self.sim_controller = controller
        if controller:
            controller.on("stop", self._on_sim_stop)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        title = QLabel("Dashboard")
        title.setFont(QFont("", 10, QFont.Weight.Bold))
        layout.addWidget(title)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.speed_plot = pg.PlotWidget(title="Avg Speed")
        self.speed_plot.setLabel("left", "Speed", "m/s")
        self.speed_plot.setLabel("bottom", "Time", "s")
        self.speed_curve = self.speed_plot.plot(pen=pg.mkPen("#3498db", width=2))
        self.tabs.addTab(self.speed_plot, "Speed")

        self.wait_plot = pg.PlotWidget(title="Avg Wait Time")
        self.wait_plot.setLabel("left", "Wait Time", "s")
        self.wait_plot.setLabel("bottom", "Time", "s")
        self.wait_curve = self.wait_plot.plot(pen=pg.mkPen("#e74c3c", width=2))
        self.tabs.addTab(self.wait_plot, "Wait")

        self.throughput_plot = pg.PlotWidget(title="Throughput")
        self.throughput_plot.setLabel("left", "Vehicles")
        self.throughput_plot.setLabel("bottom", "Time", "s")
        self.throughput_curve = self.throughput_plot.plot(
            pen=pg.mkPen("#2ecc71", width=2)
        )
        self.tabs.addTab(self.throughput_plot, "Throughput")

        self.queue_plot = pg.PlotWidget(title="Queue Length")
        self.queue_plot.setLabel("left", "Queue")
        self.queue_plot.setLabel("bottom", "Time", "s")
        self.queue_curve = self.queue_plot.plot(pen=pg.mkPen("#f39c12", width=2))
        self.tabs.addTab(self.queue_plot, "Queue")

        self.fuel_plot = pg.PlotWidget(title="Fuel Consumption")
        self.fuel_plot.setLabel("left", "Fuel", "ml")
        self.fuel_plot.setLabel("bottom", "Time", "s")
        self.fuel_curve = self.fuel_plot.plot(pen=pg.mkPen("#8e44ad", width=2))
        self.tabs.addTab(self.fuel_plot, "Fuel")

        self.co2_plot = pg.PlotWidget(title="CO₂ Emission")
        self.co2_plot.setLabel("left", "CO₂", "mg/s")
        self.co2_plot.setLabel("bottom", "Time", "s")
        self.co2_curve = self.co2_plot.plot(pen=pg.mkPen("#2c3e50", width=2))
        self.tabs.addTab(self.co2_plot, "CO₂")

    def add_data_point(self, sim_time: float, speed: float, wait: float,
                       throughput: int, queue: float, fuel: float = 0.0,
                       co2: float = 0.0):
        self._data["time"].append(sim_time)
        self._data["speed"].append(speed)
        self._data["wait_time"].append(wait)
        self._data["throughput"].append(throughput)
        self._data["queue"].append(queue)
        self._data["fuel"].append(fuel)
        self._data["co2"].append(co2)

        max_points = 500
        for key in self._data:
            if len(self._data[key]) > max_points:
                self._data[key] = self._data[key][-max_points:]

    def _update_charts(self):
        if not self._data["time"]:
            return
        try:
            t = self._data["time"]
            self.speed_curve.setData(t, self._data["speed"])
            self.wait_curve.setData(t, self._data["wait_time"])
            self.throughput_curve.setData(t, self._data["throughput"])
            self.queue_curve.setData(t, self._data["queue"])
            self.fuel_curve.setData(t, self._data["fuel"])
            self.co2_curve.setData(t, self._data["co2"])
        except RuntimeError:
            pass

    def cleanup(self):
        self._timer.stop()
        self.sim_controller = None

    def _on_sim_stop(self):
        if self._data["time"]:
            try:
                algorithm = (self.sim_controller.algorithm
                            if self.sim_controller else "unknown")
                run_id = self._storage.create_run(algorithm, 0)
                samples = []
                for i in range(len(self._data["time"])):
                    samples.append({
                        "time": self._data["time"][i],
                        "speed": self._data["speed"][i],
                        "waiting_time": self._data["wait_time"][i],
                        "throughput": self._data["throughput"][i],
                        "queue_length": self._data["queue"][i],
                        "fuel": self._data["fuel"][i],
                        "co2": self._data["co2"][i],
                    })
                self._storage.save_samples(run_id, samples)
                self._storage.end_run(run_id, len(self._data["time"]))
                self.logger.info(f"Saved run {run_id} ({len(samples)} samples)")
            except Exception as e:
                self.logger.error(f"Failed to save metrics: {e}")

    def reset(self):
        for key in self._data:
            self._data[key] = []
        self._update_charts()

    def export_csv(self, path: str):
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "time", "speed", "wait_time", "throughput",
                    "queue", "fuel", "co2",
                ])
                for i in range(len(self._data["time"])):
                    writer.writerow([
                        self._data["time"][i],
                        self._data["speed"][i],
                        self._data["wait_time"][i],
                        self._data["throughput"][i],
                        self._data["queue"][i],
                        self._data["fuel"][i],
                        self._data["co2"][i],
                    ])
            self.logger.info(f"Exported CSV: {path}")
        except Exception as e:
            self.logger.error(f"Export CSV failed: {e}")

    def export_json(self, path: str):
        try:
            data = {
                "time": self._data["time"],
                "speed": self._data["speed"],
                "wait_time": self._data["wait_time"],
                "throughput": self._data["throughput"],
                "queue": self._data["queue"],
                "fuel": self._data["fuel"],
                "co2": self._data["co2"],
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.logger.info(f"Exported JSON: {path}")
        except Exception as e:
            self.logger.error(f"Export JSON failed: {e}")
