"""
Settings Dialog

Application preferences: language, theme, SUMO path, database path.
"""

from app.utils.qt_compat import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFileDialog, QLineEdit, QFormLayout, QGroupBox,
    Qt, QFont,
)

from app.utils.localization import available_languages, t


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        title = QLabel("Application Settings")
        title.setFont(QFont("", 12, QFont.Weight.Bold))
        layout.addWidget(title)

        # General
        gen_group = QGroupBox("General")
        gen_form = QFormLayout(gen_group)

        self.lang_combo = QComboBox()
        for lang in available_languages():
            self.lang_combo.addItem(f"{lang['flag']} {lang['name']}", lang["code"])
        current_lang = self.config.get("app", "language")
        idx = self.lang_combo.findData(current_lang)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        gen_form.addRow("Language:", self.lang_combo)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        current_theme = self.config.get("app", "theme")
        if current_theme == "light":
            self.theme_combo.setCurrentIndex(1)
        gen_form.addRow("Theme:", self.theme_combo)

        layout.addWidget(gen_group)

        # SUMO
        sumo_group = QGroupBox("SUMO")
        sumo_form = QFormLayout(sumo_group)

        self.sumo_path = QLineEdit(self.config.get_sumo_binary())
        browse_sumo = QPushButton("Browse")
        browse_sumo.clicked.connect(self._browse_sumo)
        row = QHBoxLayout()
        row.addWidget(self.sumo_path)
        row.addWidget(browse_sumo)
        sumo_form.addRow("SUMO Binary:", row)

        self.netconvert_path = QLineEdit(self.config.get_netconvert_binary())
        browse_net = QPushButton("Browse")
        browse_net.clicked.connect(self._browse_netconvert)
        row2 = QHBoxLayout()
        row2.addWidget(self.netconvert_path)
        row2.addWidget(browse_net)
        sumo_form.addRow("netconvert:", row2)

        layout.addWidget(sumo_group)

        # Storage
        store_group = QGroupBox("Storage")
        store_form = QFormLayout(store_group)

        self.db_path = QLineEdit(self.config.get_db_path())
        browse_db = QPushButton("Browse")
        browse_db.clicked.connect(self._browse_db)
        row3 = QHBoxLayout()
        row3.addWidget(self.db_path)
        row3.addWidget(browse_db)
        store_form.addRow("Database:", row3)

        layout.addWidget(store_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._on_save)
        save_btn.setDefault(True)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _browse_sumo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Find SUMO Binary")
        if path:
            self.sumo_path.setText(path)

    def _browse_netconvert(self):
        path, _ = QFileDialog.getOpenFileName(self, "Find netconvert Binary")
        if path:
            self.netconvert_path.setText(path)

    def _browse_db(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Database File", "", "SQLite (*.db)"
        )
        if path:
            self.db_path.setText(path)

    def _on_save(self):
        self.config.set("app", "language", self.lang_combo.currentData())
        theme = "light" if self.theme_combo.currentIndex() == 1 else "dark"
        self.config.set("app", "theme", theme)
        self.config.set("sumo", "binary_path", self.sumo_path.text())
        self.config.set("sumo", "netconvert_path", self.netconvert_path.text())
        self.config.set("storage", "database_path", self.db_path.text())
        self.accept()
