"""
Configuration Panel

Sidebar panel for configuring simulation parameters:
traffic light algorithm, vehicle flows, and network info.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QLabel, QComboBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton, QFormLayout,
    QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ConfigPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(250)
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(8)

        # Title
        title = QLabel("Configuration")
        title.setFont(QFont("", 10, QFont.Weight.Bold))
        layout.addWidget(title)

        # TL Algorithm
        tl_group = QGroupBox("Traffic Light")
        tl_form = QFormLayout(tl_group)
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["Fixed-Time", "Actuated", "Max-Pressure", "Green Wave"])
        self.algo_combo.setCurrentIndex(0)
        tl_form.addRow("Algorithm:", self.algo_combo)

        self.cycle_spin = QSpinBox()
        self.cycle_spin.setRange(10, 300)
        self.cycle_spin.setValue(60)
        self.cycle_spin.setSuffix(" s")
        tl_form.addRow("Cycle:", self.cycle_spin)

        self.min_green = QSpinBox()
        self.min_green.setRange(5, 60)
        self.min_green.setValue(10)
        self.min_green.setSuffix(" s")
        tl_form.addRow("Min Green:", self.min_green)

        self.max_green = QSpinBox()
        self.max_green.setRange(10, 120)
        self.max_green.setValue(45)
        self.max_green.setSuffix(" s")
        tl_form.addRow("Max Green:", self.max_green)
        layout.addWidget(tl_group)

        # Vehicles
        veh_group = QGroupBox("Vehicles")
        veh_form = QFormLayout(veh_group)
        self.flow_spin = QSpinBox()
        self.flow_spin.setRange(100, 10000)
        self.flow_spin.setValue(500)
        self.flow_spin.setSingleStep(100)
        self.flow_spin.setSuffix(" veh/h")
        veh_form.addRow("Flow Rate:", self.flow_spin)

        self.veh_type = QComboBox()
        self.veh_type.addItems(["car", "truck", "bus", "mixed"])
        veh_form.addRow("Type:", self.veh_type)
        layout.addWidget(veh_group)

        # Display
        disp_group = QGroupBox("Display")
        disp_form = QFormLayout(disp_group)
        self.heatmap_cb = QCheckBox("Show Heatmap")
        self.heatmap_cb.stateChanged.connect(self._on_heatmap)
        disp_form.addRow(self.heatmap_cb)

        self.labels_cb = QCheckBox("Vehicle Labels")
        disp_form.addRow(self.labels_cb)
        layout.addWidget(disp_group)

        # Apply button
        self.apply_btn = QPushButton("Apply Configuration")
        self.apply_btn.clicked.connect(self._on_apply)
        layout.addWidget(self.apply_btn)

        layout.addStretch()
        scroll.setWidget(content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def get_config(self) -> dict:
        algo_map = {
            0: "fixed", 1: "actuated", 2: "max_pressure", 3: "green_wave"
        }
        return {
            "algorithm": algo_map.get(self.algo_combo.currentIndex(), "fixed"),
            "cycle_time": self.cycle_spin.value(),
            "min_green": self.min_green.value(),
            "max_green": self.max_green.value(),
            "flow_rate": self.flow_spin.value(),
            "vehicle_type": self.veh_type.currentText(),
            "show_heatmap": self.heatmap_cb.isChecked(),
        }

    def _on_heatmap(self, state):
        # Signal to main window
        pass

    def _on_apply(self):
        from app.utils.logger import get_logger
        logger = get_logger("config")
        logger.info(f"Config applied: {self.get_config()}")
