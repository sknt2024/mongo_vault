import os
import datetime
import shutil
from .command_runner import run_command


def backup_database(
    uri: str,
    db_name: str,
    backup_root: str,
    parallel: int = 1,
    include_collections=None,
    exclude_collections=None
):
    """
    Perform MongoDB backup with optional collection filtering.
    Returns result dictionary from run_command().
    """

    if include_collections is None:
        include_collections = []

    if exclude_collections is None:
        exclude_collections = []

    if not uri or not db_name:
        return {"success": False, "error": "URI and DB name required"}

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

    # Include specific collections (if provided)
    if include_collections:
        for col in include_collections:
            command.append(f"--collection={col}")

    # Exclude collections
    if exclude_collections:
        for col in exclude_collections:
            command.append(f"--excludeCollection={col}")

    result = run_command(command)

    if not result.get("success"):
        return result

    # Compress backup
    shutil.make_archive(
        compressed_file.replace(".tar.gz", ""),
        "gztar",
        backup_root,
        timestamp
    )

    shutil.rmtree(backup_dir)

    result["backup_file"] = compressed_file
    result["size_mb"] = round(
        os.path.getsize(compressed_file) / (1024 * 1024),
        2
    )
    result["timestamp"] = timestamp

    return result
