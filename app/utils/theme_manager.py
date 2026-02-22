import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QFile, QTextStream

class ThemeManager:
    def __init__(self):
        self.current_theme = None
        self.dark_qss = ""
        self.light_qss = ""
        self._load_stylesheets()

    def _get_base_path(self):
        """Return the base path where themes are stored – works for dev & frozen."""
        if getattr(sys, 'frozen', False):
            # When bundled, the Resources folder is where data files go
            # sys._MEIPASS points to the base of the bundled environment (often .../Frameworks)
            # We need to go up one level and into Resources
            meipass_path = sys._MEIPASS
            # Navigate from .../Contents/Frameworks to .../Contents/Resources
            resources_path = os.path.join(os.path.dirname(meipass_path), "Resources")
            return resources_path
        else:
            # Development: app/utils/ -> app/themes
            utils_dir = os.path.dirname(os.path.abspath(__file__))
            app_dir = os.path.dirname(utils_dir)
            return os.path.join(app_dir, "themes")

    def _load_stylesheets(self):
        base_path = self._get_base_path()
        # Now always look inside a "themes" subfolder
        dark_path = os.path.join(base_path, "themes", "dark.qss")
        light_path = os.path.join(base_path, "themes", "light.qss")

        # Load dark theme
        dark_file = QFile(dark_path)
        if dark_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(dark_file)
            self.dark_qss = stream.readAll()
            dark_file.close()
            print(f"✅ Loaded dark theme from {dark_path}")
        else:
            print(f"❌ ERROR: Could not open dark.qss at {dark_path}")

        # Load light theme
        light_file = QFile(light_path)
        if light_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(light_file)
            self.light_qss = stream.readAll()
            light_file.close()
            print(f"✅ Loaded light theme from {light_path}")
        else:
            print(f"❌ ERROR: Could not open light.qss at {light_path}")

    def apply_theme(self, theme: str):
        app = QApplication.instance()
        if app is None:
            print("ERROR: No QApplication instance.")
            return

        if theme == "dark":
            app.setStyleSheet(self.dark_qss)
            self.current_theme = "dark"
            print("Applied dark theme")
        elif theme == "light":
            app.setStyleSheet(self.light_qss)
            self.current_theme = "light"
            print("Applied light theme")
        elif theme == "auto":
            import datetime
            hour = datetime.datetime.now().hour
            if hour >= 18 or hour < 6:
                self.apply_theme("dark")
            else:
                self.apply_theme("light")
        else:
            print(f"Unknown theme: {theme}")