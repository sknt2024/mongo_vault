import sys
from pathlib import Path

APP_NAME = "MongoVault"

def get_version():
    try:
        if getattr(sys, "frozen", False):
            # Running inside PyInstaller bundle
            base_path = Path(sys._MEIPASS)
        else:
            # Running in dev mode
            base_path = Path(__file__).resolve().parents[2]

        version_file = base_path / "version.txt"

        if version_file.exists():
            return version_file.read_text().strip()

    except Exception as e:
        print("Version load error:", e)

    return "0.0.0"

APP_VERSION = get_version()
DEFAULT_BACKUP_DIR = "./backups"