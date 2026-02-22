import os
import datetime
import shutil
from .command_runner import run_command


def backup_database(
    uri: str,
    db_name: str,
    backup_root: str,
    parallel: int = 1,
    exclude_collections=None
):
    if exclude_collections is None:
        exclude_collections = []

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_dir = os.path.join(backup_root, timestamp)
    compressed_file = os.path.join(
        backup_root,
        f"{db_name}_backup_{timestamp}.tar.gz"
    )

    os.makedirs(backup_dir, exist_ok=True)

    command = [
        "mongodump",
        "--uri", uri,
        "--db", db_name,
        "--out", backup_dir,
        f"--numParallelCollections={parallel}"
    ]

    for col in exclude_collections:
        command.append(f"--excludeCollection={col}")

    result = run_command(command)

    if not result["success"]:
        return result

    shutil.make_archive(
        compressed_file.replace(".tar.gz", ""),
        "gztar",
        backup_root,
        timestamp
    )

    shutil.rmtree(backup_dir)

    result["backup_file"] = compressed_file
    result["size_mb"] = round(os.path.getsize(compressed_file) / (1024 * 1024), 2)

    return result
