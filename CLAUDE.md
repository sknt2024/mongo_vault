# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

MongoVault is a macOS desktop GUI application (PyQt6) that wraps MongoDB's CLI tools (`mongodump`/`mongorestore`) with a non-blocking interface, real-time log streaming, progress tracking, and theme support.

## Development Commands

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run in development
python3 run.py

# Build macOS .app bundle
./build_mongo_vault.sh
# Output: dist/MongoVault.app
```

External dependency required: `brew install mongodb-database-tools` (provides `mongodump`/`mongorestore`).

There are no configured test or lint commands.

## Architecture

Layered architecture with strict separation of concerns:

```
UI Layer (PyQt6):     app/tabs/ + app/widgets/ + app/main_window.py
                              ↓
Service Layer:        app/services/ (business logic, command building, MongoDB queries)
                              ↓
Worker Thread:        app/worker.py (CommandWorker extends QThread)
                              ↓
CLI Subprocess:       mongodump / mongorestore
```

**Key design decisions:**
- All long-running operations run in `CommandWorker` (QThread) — never call blocking I/O from the UI thread.
- Inter-component communication uses Qt signals exclusively (`log_signal`, `progress_signal`, `stats_signal`, `finished_signal`).
- Archives use mongodump's native `--archive=<file>` mode with gzip compression (`.archive.gz`).
- Progress is estimated by combining line counting ("writing"/"restoring" in output) + tracking archive file size growth.

## Key Files and Their Roles

| File | Role |
|------|------|
| `run.py` | Entry point — creates QApplication and shows MainWindow |
| `app/main_window.py` | Root widget: top bar, splitter (tabs 70% / log panel 30%), theme toggle, log export |
| `app/worker.py` | `CommandWorker(QThread)` — runs subprocess, streams logs, tracks progress/speed/ETA, collapses duplicate key errors |
| `app/tabs/backup_tab.py` | Backup UI: URI input, collection fetch/select grid, parallel slider, progress bar, Run/Cancel |
| `app/tabs/restore_tab.py` | Restore UI: file picker, target DB input, parallel slider, progress bar, Run/Cancel |
| `app/services/backup_service.py` | Builds and validates mongodump command, applies retention policy (keeps last 5) |
| `app/services/restore_service.py` | Builds mongorestore command with `--nsFrom`/`--nsTo` DB name remapping |
| `app/services/mongo_service.py` | `get_collections(uri, db_name)` via PyMongo |
| `app/services/command_runner.py` | Subprocess execution + E11000/IndexOptionsConflict error parsing |
| `app/widgets/collection_card.py` | Selectable `CollectionCard(QFrame)` widget with toggle signal |
| `app/utils/theme_manager.py` | Loads QSS from `app/themes/`, persists choice to `app/theme.txt` |
| `app/utils/constants.py` | `APP_VERSION` (reads `version.txt`, handles PyInstaller bundle paths) |

## Backup Archive Naming Convention

Archives are named `<db_name>_<timestamp>.archive.gz`. The restore service parses this filename to extract the source DB name for namespace remapping. Changes to the naming convention require updates in `restore_service.py:build_restore_command()`.

## Theme System

QSS stylesheets in `app/themes/dark.qss` and `light.qss`. Dark theme uses `#111C2D` background with `#00A848` green accents. Theme choice persists in `app/theme.txt` (committed to repo — gitignore if this causes noise).

## Version Management

Version is read from `version.txt` at runtime. Releases are managed by Release Please (`.release-please-config.json`) — do not manually bump `version.txt`.
