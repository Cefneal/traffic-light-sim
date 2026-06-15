import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QToolBar, QWidget, QHBoxLayout, QPushButton, QSlider, QLabel,
    QComboBox, QFileDialog,
)
from PyQt6.QtCore import Qt, QTimer


SIM_DIR = Path(__file__).resolve().parent.parent.parent / "sim"

DEFAULT_MAPS: list[dict[str, str]] = [
    {"name": "Pamulang", "cfg": str(SIM_DIR / "pamulang" / "test.sumocfg")},
    {"name": "Silicon Valley", "cfg": str(SIM_DIR / "silicon_valley" / "test.sumocfg")},
    {"name": "Tokyo", "cfg": str(SIM_DIR / "tokyo" / "test.sumocfg")},
]


class ControlsToolbar(QToolBar):
    def __init__(self):
        super().__init__("Simulation Controls")
        self.setMovable(False)
        self.sim_controller = None
        self.on_sim_start = None
        self._recent: list[str] = []
        self._setup_ui()

        self._timer = QTimer()
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._update_status)
        self._timer.start()

    def _setup_ui(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 2, 5, 2)

        # Play / Pause / Stop / Step
        self.play_btn = QPushButton("▶ Play")
        self.play_btn.setFixedWidth(80)
        self.play_btn.clicked.connect(self._on_play)
        layout.addWidget(self.play_btn)

        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setFixedWidth(80)
        self.pause_btn.clicked.connect(self._on_pause)
        self.pause_btn.setEnabled(False)
        layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setFixedWidth(80)
        self.stop_btn.clicked.connect(self._on_stop)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)

        self.step_btn = QPushButton("⏭ Step")
        self.step_btn.setFixedWidth(70)
        self.step_btn.clicked.connect(self._on_step)
        self.step_btn.setEnabled(False)
        layout.addWidget(self.step_btn)

        layout.addSpacing(10)

        # Map selector
        layout.addWidget(QLabel("Map:"))
        self.map_combo = QComboBox()
        self.map_combo.setMinimumWidth(140)
        self.map_combo.addItem("-- Select Map --", "")
        for m in DEFAULT_MAPS:
            self.map_combo.addItem(m["name"], m["cfg"])
        self.map_combo.currentIndexChanged.connect(self._on_map_selected)
        layout.addWidget(self.map_combo)

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._on_browse)
        layout.addWidget(self.browse_btn)

        layout.addSpacing(10)

        # Speed slider
        layout.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(10)
        self.speed_slider.setFixedWidth(100)
        self.speed_slider.valueChanged.connect(self._on_speed_change)
        layout.addWidget(self.speed_slider)

        self.speed_label = QLabel("1.0x")
        self.speed_label.setFixedWidth(40)
        layout.addWidget(self.speed_label)

        layout.addSpacing(10)

        self.status_label = QLabel("Time: 0s | Vehicles: 0")
        layout.addWidget(self.status_label)

        layout.addStretch()
        self.addWidget(container)

    def set_sim_controller(self, controller):
        self.sim_controller = controller

    def add_custom_map(self, name: str, path: str):
        existing = self.map_combo.findText(name)
        if existing >= 0:
            self.map_combo.setItemData(existing, path)
        else:
            self.map_combo.addItem(name, path)
        self.map_combo.setCurrentIndex(self.map_combo.count() - 1)

    def _on_map_selected(self, idx: int):
        if not self._timer.isActive():
            return

    def get_selected_cfg(self) -> str | None:
        data = self.map_combo.currentData()
        if data and os.path.exists(data):
            return str(data)
        return None

    def _on_browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open SUMO Config",
            str(SIM_DIR) if SIM_DIR.exists() else "",
            "SUMO Config (*.sumocfg)",
        )
        if path:
            name = Path(path).parent.name
            self.add_custom_map(f"{name} (custom)", path)

    def _on_play(self):
        if not self.sim_controller:
            return

        if self.sim_controller.is_paused:
            self.sim_controller.resume()
            self._set_buttons_running()
            return

        cfg_path = self.get_selected_cfg()
        if not cfg_path:
            self._on_browse()
            cfg_path = self.get_selected_cfg()
            if not cfg_path:
                return

        try:
            self.sim_controller.start(cfg_path)
            if self.on_sim_start and self.sim_controller.is_running:
                self.on_sim_start(cfg_path)
            if self.sim_controller.is_running:
                self._set_buttons_running()
        except Exception as e:
            from app.utils.logger import get_logger
            get_logger("controls").error(f"Start failed: {e}")

    def _set_buttons_running(self):
        self.play_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.step_btn.setEnabled(True)

    def _on_pause(self):
        if self.sim_controller:
            self.sim_controller.pause()
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)

    def _on_stop(self):
        if self.sim_controller:
            self.sim_controller.stop()
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.step_btn.setEnabled(False)
        self.status_label.setText("Time: 0s | Vehicles: 0")

    def _on_step(self):
        if self.sim_controller:
            self.sim_controller.step_single()

    def _on_speed_change(self, value: int):
        speed = value / 10.0
        self.speed_label.setText(f"{speed:.1f}x")
        if self.sim_controller:
            self.sim_controller.set_speed(speed)

    def _update_status(self):
        if self.sim_controller and self.sim_controller.is_running:
            snapshot = self.sim_controller.get_step_snapshot()
            t = snapshot.time
            remaining = snapshot.remaining_vehicles
            self.status_label.setText(
                f"Time: {t:.0f}s | Vehicles: {remaining} | Speed: {self.speed_label.text()}"
            )
