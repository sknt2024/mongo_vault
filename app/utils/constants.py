import sys
from pathlib import Path

APP_NAME = "MongoVault"


def get_version():
    try:
        # If running from PyInstaller bundle
        if getattr(sys, "frozen", False):
            base_path = Path(sys._MEIPASS)
        else:
            # Go from app/utils/constants.py → project root
            base_path = Path(__file__).resolve().parents[2]

        version_file = base_path / "version.txt"

        print("Looking for version at:", version_file)  # DEBUG

        if version_file.exists():
            return version_file.read_text().strip()

    except Exception as e:
        print("Version load error:", e)

    return "0.0.0"


APP_VERSION = get_version()

DEFAULT_BACKUP_DIR = "./backups"
