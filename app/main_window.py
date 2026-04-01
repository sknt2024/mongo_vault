from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QTextEdit,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QSplitter,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtCore import Qt
import os
import datetime

from app.tabs.backup_tab import BackupTab
from app.tabs.restore_tab import RestoreTab
from app.utils.constants import APP_NAME, APP_VERSION
from app.utils.theme_manager import ThemeManager


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(420, 820)
        self.setMinimumWidth(360)

        self.theme_manager = ThemeManager()
        self._log_visible = True
        self._last_log_width = 220  # remembered height of log panel

        self.init_ui()
        self.theme_manager.load_saved_theme()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 10, 16, 10)
        main_layout.setSpacing(8)

        # ── Top Bar ────────────────────────────────────────────────────────
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        app_icon = QLabel("≡")
        app_icon.setObjectName("appIcon")

        app_title = QLabel(APP_NAME)
        app_title.setObjectName("appTitle")

        self.theme_toggle_btn = QPushButton("☽ Theme")
        self.theme_toggle_btn.setObjectName("iconBtn")
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)

        self.log_toggle_btn = QPushButton("</> Logs")
        self.log_toggle_btn.setObjectName("iconBtn")
        self.log_toggle_btn.setCheckable(True)
        self.log_toggle_btn.setChecked(True)
        self.log_toggle_btn.clicked.connect(self.toggle_log_panel)

        title_row = QHBoxLayout()
        title_row.setSpacing(6)
        title_row.addWidget(app_icon)
        title_row.addWidget(app_title)

        top_bar.addLayout(title_row)
        top_bar.addStretch()
        top_bar.addWidget(self.log_toggle_btn)
        top_bar.addWidget(self.theme_toggle_btn)

        # ── Vertical splitter (tabs on top, logs at bottom) ────────────────
        self.splitter = QSplitter(Qt.Orientation.Vertical)

        # TOP — Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(BackupTab(self.append_log), "Backup")
        self.tabs.addTab(RestoreTab(self.append_log), "Restore")

        # BOTTOM — Log panel
        self.log_panel = QWidget()
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(8, 4, 8, 4)
        log_layout.setSpacing(4)

        log_header = QHBoxLayout()
        log_header.setSpacing(6)

        log_label = QLabel("Logs")
        log_label.setObjectName("sectionTitle")

        self.export_log_btn = QPushButton("⬇  Export")
        self.export_log_btn.clicked.connect(self.export_logs)

        self.clear_log_btn = QPushButton("✕  Clear")
        self.clear_log_btn.clicked.connect(self.clear_logs)

        log_header.addWidget(log_label)
        log_header.addStretch()
        log_header.addWidget(self.export_log_btn)
        log_header.addWidget(self.clear_log_btn)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        log_layout.addLayout(log_header)
        log_layout.addWidget(self.log_output)
        self.log_panel.setLayout(log_layout)

        self.splitter.addWidget(self.tabs)
        self.splitter.addWidget(self.log_panel)
        # Tabs 70%, logs 30%
        self.splitter.setStretchFactor(0, 7)
        self.splitter.setStretchFactor(1, 3)

        # ── Final layout ───────────────────────────────────────────────────
        main_layout.addLayout(top_bar)
        main_layout.addWidget(self.splitter)
        self.setLayout(main_layout)

    # ── Logging ────────────────────────────────────────────────────────────

    def append_log(self, text: str):
        self.log_output.append(text)

    def clear_logs(self):
        self.log_output.clear()

    # ── Log panel toggle ───────────────────────────────────────────────────

    def toggle_log_panel(self):
        sizes = self.splitter.sizes()  # [tabs_height, logs_height]
        if self._log_visible:
            self._last_log_width = sizes[1] or self._last_log_width
            self.splitter.setSizes([sizes[0] + sizes[1], 0])
            self.log_toggle_btn.setText("[ ] Logs")
            self._log_visible = False
        else:
            total = sizes[0] + sizes[1]
            top = max(0, total - self._last_log_width)
            self.splitter.setSizes([top, self._last_log_width])
            self.log_toggle_btn.setText("</> Logs")
            self._log_visible = True

    # ── Export logs ────────────────────────────────────────────────────────

    def export_logs(self):
        content = self.log_output.toPlainText().strip()
        if not content:
            QMessageBox.information(self, "Nothing to Export", "The log is empty.")
            return

        os.makedirs("./logs", exist_ok=True)
        default_name = (
            f"./logs/mongovault_log_"
            f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        )

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs",
            default_name,
            "Text Files (*.txt);;All Files (*)"
        )

        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self.append_log(f"[Export] Log saved → {path}")
        except OSError as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    # ── Theme toggle ───────────────────────────────────────────────────────

    def toggle_theme(self):
        self.theme_manager.toggle_theme()