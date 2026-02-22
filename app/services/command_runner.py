import subprocess
from typing import Dict, Any


def run_command(command, log_file=None) -> Dict[str, Any]:
    """
    Executes mongodump/mongorestore command
    Parses duplicate key errors & index conflicts
    Returns structured result
    """

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    output = result.stdout + result.stderr

    if log_file:
        with open(log_file, "w") as f:
            f.write(output)

    duplicate_count = 0
    index_conflicts = 0
    duplicate_per_collection = {}

    for line in output.splitlines():

        if "E11000 duplicate key error" in line:
            duplicate_count += 1

            if "collection:" in line:
                try:
                    col_part = line.split("collection:")[1].strip()
                    col_name = col_part.split(" ")[0]
                    duplicate_per_collection[col_name] = (
                        duplicate_per_collection.get(col_name, 0) + 1
                    )
                except Exception:
                    pass

        if "IndexOptionsConflict" in line:
            index_conflicts += 1

    return {
        "success": result.returncode == 0,
        "return_code": result.returncode,
        "output": output,
        "duplicate_count": duplicate_count,
        "index_conflicts": index_conflicts,
        "duplicate_per_collection": duplicate_per_collection
    }
