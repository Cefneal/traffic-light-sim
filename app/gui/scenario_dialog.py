import json
import os
from pathlib import Path

from app.utils.qt_compat import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QListWidget, QFileDialog, QMessageBox,
    QComboBox, QFormLayout, Qt, QFont,
)


SCENARIO_DIR = Path.home() / ".tls" / "scenarios"


class ScenarioDialog(QDialog):
    def __init__(self, parent=None, mode="new"):
        super().__init__(parent)
        self.mode = mode
        self._scenario_name = ""
        self._scenario_data: dict | None = None
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("New Scenario" if self.mode == "new" else
                            "Open Scenario" if self.mode == "open" else
                            "Save Scenario")
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

            self.route_path = QLineEdit()
            self.route_path.setPlaceholderText("Path to .rou.xml...")
            browse_route = QPushButton("Browse")
            browse_route.clicked.connect(self._browse_route)
            row2 = QHBoxLayout()
            row2.addWidget(self.route_path)
            row2.addWidget(browse_route)
            form.addRow("Routes:", row2)

            layout.addLayout(form)

        elif self.mode == "open":
            title = QLabel("Open Scenario")
            title.setFont(QFont("", 12, QFont.Weight.Bold))
            layout.addWidget(title)

            self.scenario_list = QListWidget()
            self._refresh_scenario_list()
            layout.addWidget(self.scenario_list)

        else:  # save
            title = QLabel("Save Scenario")
            title.setFont(QFont("", 12, QFont.Weight.Bold))
            layout.addWidget(title)

            self.name_input = QLineEdit()
            self.name_input.setPlaceholderText("Scenario name...")
            layout.addWidget(self.name_input)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        ok_label = "OK" if self.mode == "new" else "Open" if self.mode == "open" else "Save"
        ok_btn = QPushButton(ok_label)
        ok_btn.clicked.connect(self._on_ok)
        ok_btn.setDefault(True)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)

    def _refresh_scenario_list(self):
        self.scenario_list.clear()
        if SCENARIO_DIR.exists():
            for f in sorted(SCENARIO_DIR.glob("*.json")):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    name = data.get("name", f.stem)
                    self.scenario_list.addItem(name)
                except Exception:
                    self.scenario_list.addItem(f.stem)

    def _browse_network(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Network File", "", "SUMO Network (*.net.xml)"
        )
        if path:
            self.network_path.setText(path)

    def _browse_route(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Routes File", "", "SUMO Routes (*.rou.xml)"
        )
        if path:
            self.route_path.setText(path)

    def _on_ok(self):
        SCENARIO_DIR.mkdir(parents=True, exist_ok=True)

        if self.mode == "new":
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Warning", "Please enter a scenario name")
                return
            data = {
                "name": name,
                "description": self.desc_input.toPlainText(),
                "network": self.network_path.text(),
                "routes": self.route_path.text(),
                "algorithm": self.algo_combo.currentText(),
            }
            path = SCENARIO_DIR / f"{name}.json"
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            self._scenario_data = data
            self._scenario_name = name
            self.accept()

        elif self.mode == "open":
            item = self.scenario_list.currentItem()
            if not item:
                return
            name = item.text()
            path = SCENARIO_DIR / f"{name}.json"
            if path.exists():
                self._scenario_data = json.loads(path.read_text(encoding="utf-8"))
            self._scenario_name = name
            self.accept()

        else:  # save
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Warning", "Please enter a scenario name")
                return
            dummy = {"name": name, "description": "", "network": "", "routes": "", "algorithm": ""}
            path = SCENARIO_DIR / f"{name}.json"
            path.write_text(json.dumps(dummy, indent=2), encoding="utf-8")
            self._scenario_name = name
            self._scenario_data = dummy
            self.accept()

    def scenario_name(self) -> str:
        return self._scenario_name

    def scenario_data(self) -> dict | None:
        return self._scenario_data
