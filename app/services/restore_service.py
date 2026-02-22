import tempfile
import tarfile
import os
import shutil
import datetime
from .command_runner import run_command


def restore_database(
    backup_file: str,
    uri: str,
    db_name: str,
    drop: bool = False,
    parallel: int = 1
):
    if not os.path.isfile(backup_file):
        return {"success": False, "error": "Backup file not found"}

    if not backup_file.endswith(".tar.gz"):
        return {"success": False, "error": "Invalid backup format"}

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"{backup_file.replace('.tar.gz','')}_restore_{timestamp}.log"

    temp_dir = tempfile.mkdtemp(prefix="mongo_restore_")

    try:
        with tarfile.open(backup_file, "r:gz") as tar:
            tar.extractall(temp_dir)

        dirs = [
            os.path.join(temp_dir, d)
            for d in os.listdir(temp_dir)
            if os.path.isdir(os.path.join(temp_dir, d))
        ]

        if not dirs:
            shutil.rmtree(temp_dir)
            return {"success": False, "error": "Invalid backup structure"}

        timestamp_dir = dirs[0]

        command = [
            "mongorestore",
            "--uri", uri,
            "--dir", timestamp_dir,
            f"--numParallelCollections={parallel}"
        ]

        if drop:
            command.append("--drop")

        result = run_command(command, log_file)

        result["log_file"] = log_file

        return result

    finally:
        shutil.rmtree(temp_dir)
