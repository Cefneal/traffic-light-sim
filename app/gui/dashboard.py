"""
Dashboard Panel

Real-time charts showing simulation metrics using pyqtgraph.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
import pyqtgraph as pg

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
            "time": [],
        }
        self._setup_ui()
        self._timer = QTimer()
        self._timer.setInterval(500)
        self._timer.timeout.connect(self._update_charts)
        self._timer.start()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        title = QLabel("Dashboard")
        title.setFont(QFont("", 10, QFont.Weight.Bold))
        layout.addWidget(title)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Speed chart
        self.speed_plot = pg.PlotWidget(title="Avg Speed")
        self.speed_plot.setLabel("left", "Speed", "m/s")
        self.speed_plot.setLabel("bottom", "Time", "s")
        self.speed_curve = self.speed_plot.plot(pen=pg.mkPen("#3498db", width=2))
        self.tabs.addTab(self.speed_plot, "Speed")

        # Wait time
        self.wait_plot = pg.PlotWidget(title="Avg Wait Time")
        self.wait_plot.setLabel("left", "Wait Time", "s")
        self.wait_plot.setLabel("bottom", "Time", "s")
        self.wait_curve = self.wait_plot.plot(pen=pg.mkPen("#e74c3c", width=2))
        self.tabs.addTab(self.wait_plot, "Wait")

        # Throughput
        self.throughput_plot = pg.PlotWidget(title="Throughput")
        self.throughput_plot.setLabel("left", "Vehicles")
        self.throughput_plot.setLabel("bottom", "Time", "s")
        self.throughput_curve = self.throughput_plot.plot(
            pen=pg.mkPen("#2ecc71", width=2)
        )
        self.tabs.addTab(self.throughput_plot, "Throughput")

        # Queue
        self.queue_plot = pg.PlotWidget(title="Queue Length")
        self.queue_plot.setLabel("left", "Queue")
        self.queue_plot.setLabel("bottom", "Time", "s")
        self.queue_curve = self.queue_plot.plot(pen=pg.mkPen("#f39c12", width=2))
        self.tabs.addTab(self.queue_plot, "Queue")

    def set_sim_controller(self, controller):
        self.sim_controller = controller

    def add_data_point(self, sim_time: float, speed: float, wait: float,
                       throughput: int, queue: float):
        self._data["time"].append(sim_time)
        self._data["speed"].append(speed)
        self._data["wait_time"].append(wait)
        self._data["throughput"].append(throughput)
        self._data["queue"].append(queue)

        max_points = 500
        for key in self._data:
            if len(self._data[key]) > max_points:
                self._data[key] = self._data[key][-max_points:]

    def _update_charts(self):
        if not self._data["time"]:
            return

        t = self._data["time"]
        self.speed_curve.setData(t, self._data["speed"])
        self.wait_curve.setData(t, self._data["wait_time"])
        self.throughput_curve.setData(t, self._data["throughput"])
        self.queue_curve.setData(t, self._data["queue"])

    def reset(self):
        for key in self._data:
            self._data[key] = []
        self._update_charts()

    def export_csv(self, path: str):
        import csv
        try:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["time", "speed", "wait_time", "throughput", "queue"])
                for i in range(len(self._data["time"])):
                    writer.writerow([
                        self._data["time"][i],
                        self._data["speed"][i],
                        self._data["wait_time"][i],
                        self._data["throughput"][i],
                        self._data["queue"][i],
                    ])
            self.logger.info(f"Exported CSV: {path}")
        except Exception as e:
            self.logger.error(f"Export CSV failed: {e}")

    def export_json(self, path: str):
        import json
        try:
            data = {
                "time": self._data["time"],
                "speed": self._data["speed"],
                "wait_time": self._data["wait_time"],
                "throughput": self._data["throughput"],
                "queue": self._data["queue"],
            }
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            self.logger.info(f"Exported JSON: {path}")
        except Exception as e:
            self.logger.error(f"Export JSON failed: {e}")
