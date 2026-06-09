"""
Main Application Window

Top-level window with menu, toolbar, map viewer sidebar, and status bar.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QMenuBar, QStatusBar, QMessageBox, QFileDialog,
)
from PyQt6.QtCore import Qt

from app.gui.map_viewer import MapViewer
from app.gui.dashboard import DashboardPanel
from app.gui.controls import ControlsToolbar
from app.gui.config_panel import ConfigPanel
from app.gui.scenario_dialog import ScenarioDialog
from app.gui.settings_dialog import SettingsDialog
from app.utils.logger import get_logger


class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.logger = get_logger()
        self.sim_controller = None
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(self.config.get("app", "name"))
        self.resize(1280, 800)

        self._create_menu_bar()
        self._create_central_widget()
        self._create_status_bar()

    def _create_menu_bar(self):
        menu_bar = self.menuBar()

        # File
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("Import OSM...", self._on_import_osm)
        file_menu.addSeparator()
        file_menu.addAction("Export CSV", self._on_export_csv)
        file_menu.addAction("Export JSON", self._on_export_json)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        # Scenario
        sc_menu = menu_bar.addMenu("Scenario")
        sc_menu.addAction("New", self._on_new_scenario)
        sc_menu.addAction("Open", self._on_open_scenario)
        sc_menu.addAction("Save", self._on_save_scenario)

        # Help
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("About", self._on_about)

    def _create_central_widget(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.controls = ControlsToolbar()
        layout.addWidget(self.controls)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.map_viewer = MapViewer()
        splitter.addWidget(self.map_viewer)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(2, 2, 2, 2)

        self.config_panel = ConfigPanel()
        right_layout.addWidget(self.config_panel)

        self.dashboard = DashboardPanel()
        right_layout.addWidget(self.dashboard)

        splitter.addWidget(right_panel)
        splitter.setSizes([800, 300])
        layout.addWidget(splitter)

    def _create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._status_label = self.status_bar.currentMessage()
        self.status_bar.showMessage("Ready")

    def set_status(self, message: str):
        self.status_bar.showMessage(message)

    def set_sim_controller(self, controller):
        self.sim_controller = controller
        self.controls.set_sim_controller(controller)
        self.map_viewer.set_sim_controller(controller)
        self.dashboard.set_sim_controller(controller)

    def _on_import_osm(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import OSM File", "", "OSM Files (*.osm)"
        )
        if path:
            self.set_status(f"Importing {path}...")
            from app.engine.osm_importer import OSMImporter
            importer = OSMImporter(self.config)
            try:
                net_path = importer.import_osm(path)
                info = importer.parse_network_info(net_path)
                self.map_viewer.load_network(net_path)
                self.set_status(
                    f"Loaded: {info['nodes']} nodes, {info['edges']} edges, "
                    f"{info['traffic_lights']} TLs"
                )
            except Exception as e:
                QMessageBox.critical(self, "Import Error", str(e))
                self.set_status("Import failed")

    def _on_export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "", "CSV Files (*.csv)"
        )
        if path and self.dashboard:
            self.dashboard.export_csv(path)

    def _on_export_json(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export JSON", "", "JSON Files (*.json)"
        )
        if path and self.dashboard:
            self.dashboard.export_json(path)

    def _on_new_scenario(self):
        dialog = ScenarioDialog(self)
        if dialog.exec():
            self.set_status(f"Scenario: {dialog.scenario_name()}")

    def _on_open_scenario(self):
        dialog = ScenarioDialog(self, mode="open")
        if dialog.exec():
            self.set_status(f"Opened scenario")

    def _on_save_scenario(self):
        self.set_status("Scenario saved")

    def _on_about(self):
        QMessageBox.about(
            self,
            "About TLS",
            "Traffic Light Simulation v1.0.0\n\n"
            "Desktop GUI untuk simulasi lalu lintas skala kota\n"
            "Berbasis SUMO engine + Python PyQt6\n\n"
            "Open source under GPL v2"
        )
