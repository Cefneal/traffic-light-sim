"""
Scenario Dialog

Dialogs for creating, opening, and saving scenarios.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QListWidget, QFileDialog, QMessageBox,
    QComboBox, QFormLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ScenarioDialog(QDialog):
    def __init__(self, parent=None, mode="new"):
        super().__init__(parent)
        self.mode = mode
        self._scenario_name = ""
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("New Scenario" if self.mode == "new" else "Open Scenario")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        if self.mode == "new":
            title = QLabel("New Scenario")
            title.setFont(QFont("", 12, QFont.Weight.Bold))
            layout.addWidget(title)

            form = QFormLayout()

            self.name_input = QLineEdit()
            self.name_input.setPlaceholderText("Scenario name...")
            form.addRow("Name:", self.name_input)

            self.desc_input = QTextEdit()
            self.desc_input.setPlaceholderText("Description (optional)...")
            self.desc_input.setMaximumHeight(80)
            form.addRow("Description:", self.desc_input)

            self.network_path = QLineEdit()
            self.network_path.setPlaceholderText("Path to .net.xml...")
            browse_btn = QPushButton("Browse")
            browse_btn.clicked.connect(self._browse_network)
            row = QHBoxLayout()
            row.addWidget(self.network_path)
            row.addWidget(browse_btn)
            form.addRow("Network:", row)

            self.algo_combo = QComboBox()
            self.algo_combo.addItems([
                "Fixed-Time", "Actuated", "Max-Pressure", "Green Wave"
            ])
            form.addRow("TL Algorithm:", self.algo_combo)

            layout.addLayout(form)

        else:
            title = QLabel("Open Scenario")
            title.setFont(QFont("", 12, QFont.Weight.Bold))
            layout.addWidget(title)

            self.scenario_list = QListWidget()
            self.scenario_list.addItems([
                "Demo: Simple Intersection",
                "Demo: City Center (10 intx)",
                "Demo: Green Wave Arterial",
            ])
            self.scenario_list.setCurrentRow(0)
            layout.addWidget(self.scenario_list)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("OK" if self.mode == "new" else "Open")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)

    def _browse_network(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Network File", "", "SUMO Network (*.net.xml)"
        )
        if path:
            self.network_path.setText(path)

    def scenario_name(self) -> str:
        if self.mode == "new":
            return self.name_input.text() or "Unnamed"
        item = self.scenario_list.currentItem()
        return item.text() if item else "Unknown"
