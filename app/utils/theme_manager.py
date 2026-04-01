import os
from PyQt6.QtWidgets import QApplication


class ThemeManager:
    def __init__(self):
        self.app = QApplication.instance()
        self.current_theme = "dark"

        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.settings_file = os.path.join(self.base_dir, "theme.txt")

    def get_theme_path(self, theme_name: str):
        return os.path.join(self.base_dir, "themes", f"{theme_name}.qss")

    def apply_theme(self, theme_name: str):
        theme_path = self.get_theme_path(theme_name)

        if not os.path.exists(theme_path):
            print(f"❌ Could not open theme: {theme_path}")
            return

        with open(theme_path, "r") as f:
            self.app.setStyleSheet(f.read())

        self.current_theme = theme_name
        self.save_theme()
        print(f"✅ Applied {theme_name} theme")

    def toggle_theme(self):
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(new_theme)

    def save_theme(self):
        with open(self.settings_file, "w") as f:
            f.write(self.current_theme)

    def load_saved_theme(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as f:
                saved = f.read().strip()
                if saved in ["dark", "light"]:
                    self.current_theme = saved
        self.apply_theme(self.current_theme)