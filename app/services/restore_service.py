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
    parallel: int = 1,
    include_collections=None,
    exclude_collections=None
):
    """
    Restore MongoDB backup with optional include/exclude collection filtering.
    """

    if include_collections is None:
        include_collections = []

    if exclude_collections is None:
        exclude_collections = []

    if not os.path.isfile(backup_file):
        return {"success": False, "error": "Backup file not found"}

    if not backup_file.endswith(".tar.gz"):
        return {"success": False, "error": "Invalid backup format (.tar.gz required)"}

    if not uri or not db_name:
        return {"success": False, "error": "URI and DB name required"}

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"{backup_file.replace('.tar.gz','')}_restore_{timestamp}.log"

    temp_dir = tempfile.mkdtemp(prefix="mongo_restore_")

    try:
        # Extract backup
        with tarfile.open(backup_file, "r:gz") as tar:
            tar.extractall(temp_dir)

        # Find extracted timestamp directory
        dirs = [
            os.path.join(temp_dir, d)
            for d in os.listdir(temp_dir)
            if os.path.isdir(os.path.join(temp_dir, d))
        ]

        if not dirs:
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

        # Include specific collections
        if include_collections:
            for col in include_collections:
                command.append(f"--nsInclude={db_name}.{col}")

        # Exclude specific collections
        if exclude_collections:
            for col in exclude_collections:
                command.append(f"--nsExclude={db_name}.{col}")

        result = run_command(command, log_file)

        result["log_file"] = log_file
        result["timestamp"] = timestamp

        return result

    finally:
        shutil.rmtree(temp_dir)
