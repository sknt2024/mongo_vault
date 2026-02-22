from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QTextEdit,
    QLabel,
    QPushButton,
    QHBoxLayout,
)

from app.tabs.backup_tab import BackupTab
from app.tabs.restore_tab import RestoreTab
from app.utils.constants import APP_NAME, APP_VERSION
from app.utils.theme_manager import ThemeManager


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(900, 600)

        self.theme_manager = ThemeManager()

        self.init_ui()

        # Auto detect theme on startup
        self.theme_manager.apply_theme("auto")

    def init_ui(self):
        layout = QVBoxLayout()

        # Top Bar
        top_bar = QHBoxLayout()
        self.theme_toggle_btn = QPushButton("Toggle Theme")
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)

        top_bar.addWidget(QLabel("MongoVault"))
        top_bar.addStretch()
        top_bar.addWidget(self.theme_toggle_btn)

        # Tabs
        self.tabs = QTabWidget()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        self.tabs.addTab(BackupTab(self.append_log), "Backup")
        self.tabs.addTab(RestoreTab(self.append_log), "Restore")

        layout.addLayout(top_bar)
        layout.addWidget(self.tabs)
        layout.addWidget(QLabel("Logs"))
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def append_log(self, text):
        self.log_output.append(text)

    def toggle_theme(self):
        if self.theme_manager.current_theme == "dark":
            self.theme_manager.apply_theme("light")
        else:
            self.theme_manager.apply_theme("dark")
