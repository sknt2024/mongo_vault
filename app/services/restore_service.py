import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure


def validate_restore_connection(uri: str, db_name: str):
    """Validate MongoDB connection using pymongo."""
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


def build_restore_command(
    backup_file: str,
    uri: str,
    db_name: str,
    drop: bool = True,
    parallel: int = 1,
):
    """
    Build the mongorestore command list for a native archive (.archive.gz).
    Returns (command, error_string) — error_string is None on success.
    """
    if not backup_file:
        return None, "No backup file selected."

    if not os.path.isfile(backup_file):
        return None, f"Backup file not found: {backup_file}"

    if not backup_file.endswith(".archive.gz"):
        return None, "Invalid backup format — select a .archive.gz file."

    if not uri or not db_name:
        return None, "URI and database name are required."

    # Derive source DB name from the archive filename
    # Convention: {db_name}_backup_{timestamp}.archive.gz
    basename = os.path.basename(backup_file)
    if "_backup_" in basename:
        source_db = basename.split("_backup_")[0]
    else:
        source_db = db_name  # fallback: assume same DB name

    command = [
        "mongorestore",
        "--uri", uri,
        f"--archive={backup_file}",
        "--gzip",
        f"--nsFrom={source_db}.*",
        f"--nsTo={db_name}.*",
        f"--numParallelCollections={parallel}",
    ]

    if drop:
        command.append("--drop")

    return command, None

