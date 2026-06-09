"""
Controls Toolbar

Play, pause, stop, step buttons and speed slider for simulation control.
"""

from PyQt6.QtWidgets import (
    QToolBar, QWidget, QHBoxLayout, QPushButton, QSlider, QLabel,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon


class ControlsToolbar(QToolBar):
    def __init__(self):
        super().__init__("Simulation Controls")
        self.setMovable(False)
        self.sim_controller = None
        self._setup_ui()

        self._timer = QTimer()
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._update_status)
        self._timer.start()

    def _setup_ui(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 2, 5, 2)

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

        layout.addSpacing(20)

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

        layout.addSpacing(20)

        self.status_label = QLabel("Time: 0s | Vehicles: 0 | FPS: 0")
        layout.addWidget(self.status_label)

        layout.addStretch()
        self.addWidget(container)

    def set_sim_controller(self, controller):
        self.sim_controller = controller

    def _on_play(self):
        if self.sim_controller:
            if self.sim_controller.is_paused:
                self.sim_controller.resume()
            else:
                from PyQt6.QtWidgets import QFileDialog
                path, _ = QFileDialog.getOpenFileName(
                    self, "Open SUMO Config", "", "SUMO Config (*.sumocfg)"
                )
                if path:
                    self.sim_controller.start(path)
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
        self.status_label.setText("Time: 0s | Vehicles: 0 | FPS: 0")

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
            t = self.sim_controller.current_time
            try:
                remaining = self.sim_controller.traci.get_remaining_vehicles()
            except Exception:
                remaining = 0
            self.status_label.setText(
                f"Time: {t:.0f}s | Vehicles: {remaining} | "
                f"Speed: {self.speed_label.text()}"
            )
