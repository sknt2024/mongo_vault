import os
import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from .command_runner import run_command

def validate_connection(uri: str, db_name: str):
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client[db_name].command("ping")
        client.close()
        return {"success": True}
    except ConnectionFailure as e:
        return {"success": False, "error": f"Connection failed: {e}"}
    except OperationFailure as e:
        return {"success": False, "error": f"Auth failed: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def backup_database(
    uri: str,
    db_name: str,
    backup_root: str,
    parallel: int = 1,
    include_collections=None,
    exclude_collections=None
):
    """
    Perform MongoDB backup using native archive mode.
    Returns structured result.
    """

    if include_collections is None:
        include_collections = []

    if exclude_collections is None:
        exclude_collections = []

    if not uri or not db_name:
        return {"success": False, "error": "URI and DB name required"}

    # Ensure backup directory exists
    os.makedirs(backup_root, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    archive_file = os.path.join(
        backup_root,
        f"{db_name}_backup_{timestamp}.archive.gz"
    )

    # 🔥 Use Mongo native archive mode (BEST PRACTICE)
    command = [
        "mongodump",
        "--uri", uri,
        "--db", db_name,
        f"--archive={archive_file}",
        "--gzip",
        f"--numParallelCollections={parallel}"
    ]

    # Include specific collections
    for col in include_collections:
        command.append(f"--collection={col}")

    # Exclude collections
    for col in exclude_collections:
        command.append(f"--excludeCollection={col}")

    result = run_command(command)

    # 🔥 Check mongodump execution
    if not result.get("success"):
        return result

    # 🔥 Validate archive file exists
    if not os.path.exists(archive_file):
        return {
            "success": False,
            "error": "Backup archive was not created."
        }

    size_bytes = os.path.getsize(archive_file)

    # 🔥 Validate archive not empty
    if size_bytes == 0:
        return {
            "success": False,
            "error": "Backup archive is empty (0 bytes)."
        }

    size_mb = round(size_bytes / (1024 * 1024), 2)

    return {
        "success": True,
        "backup_file": archive_file,
        "size_mb": size_mb,
        "timestamp": timestamp,
        "duplicate_count": result.get("duplicate_count", 0),
        "index_conflicts": result.get("index_conflicts", 0),
    }

def apply_retention_policy(backup_root: str, keep_last: int = 5):
    """
    Delete old backups, keeping only the `keep_last` most recent archives.
    """
    if not os.path.isdir(backup_root):
        return

    archives = sorted(
        [
            os.path.join(backup_root, f)
            for f in os.listdir(backup_root)
            if f.endswith(".archive.gz")
        ],
        key=os.path.getmtime,
        reverse=True  # newest first
    )

    for old_archive in archives[keep_last:]:
        try:
            os.remove(old_archive)
        except OSError:
            pass