import os

APP_NAME = "MongoVault"

def get_version():
    version_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "version.txt"
    )
    try:
        with open(version_file, "r") as f:
            return f.read().strip()
    except Exception:
        return "0.0.0"

APP_VERSION = get_version()

DEFAULT_BACKUP_DIR = "./backups"
