import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette
from PyQt6.QtCore import Qt


class ThemeManager:
    def __init__(self):
        self.current_theme = "auto"

    def detect_system_theme(self):
        """
        Detect macOS system theme automatically
        """
        palette = QApplication.palette()
        color = palette.color(QPalette.ColorRole.Window)
        return "dark" if color.value() < 128 else "light"

    def apply_theme(self, theme_name: str):
        """
        Apply selected theme (light/dark/auto)
        """
        if theme_name == "auto":
            theme_name = self.detect_system_theme()

        base_dir = os.path.dirname(__file__)
        theme_path = os.path.join(
            base_dir,
            "..",
            "themes",
            f"{theme_name}.qss"
        )

        theme_path = os.path.abspath(theme_path)

        if os.path.exists(theme_path):
            with open(theme_path, "r") as f:
                style = f.read()
                QApplication.instance().setStyleSheet(style)

        self.current_theme = theme_name
