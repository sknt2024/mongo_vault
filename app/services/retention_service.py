import os

def apply_retention_policy(directory: str, keep_last: int = 5):
    backups = sorted(
        [f for f in os.listdir(directory) if f.endswith(".tar.gz")],
        reverse=True
    )

    for old_file in backups[keep_last:]:
        os.remove(os.path.join(directory, old_file))
