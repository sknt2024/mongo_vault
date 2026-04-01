from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog,
    QHBoxLayout, QMessageBox,
    QProgressBar, QSlider
)
from PyQt6.QtCore import Qt
from pymongo import MongoClient

from app.services.restore_service import validate_restore_connection, build_restore_command
from app.utils.logger import format_log
from app.worker import CommandWorker


class RestoreTab(QWidget):
    def __init__(self, log_callback):
        super().__init__()
        self.log_callback = log_callback
        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # ── Mongo Connection URI ───────────────────────────────────────────
        uri_lbl = QLabel("Mongo Connection URI")
        uri_lbl.setObjectName("sectionLabel")
        self.uri = QLineEdit()
        self.uri.setPlaceholderText("mongodb://username:password@host:27017")

        # ── Target Database ──────────────────────────────────────────────
        db_lbl = QLabel("Target Database")
        db_lbl.setObjectName("sectionLabel")
        self.db = QLineEdit()
        self.db.setPlaceholderText("Database name to restore into")

        # ── Backup file ──────────────────────────────────────────────────
        file_lbl = QLabel("Backup Archive")
        file_lbl.setObjectName("sectionLabel")
        self.file = QLineEdit()
        self.file.setPlaceholderText("Select .archive.gz backup file")
        self.file.setReadOnly(True)

        browse_btn = QPushButton("📂  Browse")
        browse_btn.setObjectName("fetchBtn")
        browse_btn.clicked.connect(self.select_file)

        file_row = QHBoxLayout()
        file_row.setSpacing(8)
        file_row.addWidget(self.file, 1)
        file_row.addWidget(browse_btn)

        # ── Parallel Collections ───────────────────────────────────────────
        par_title = QLabel("Parallel Collections")
        par_title.setObjectName("sectionTitle")
        self.parallel_value_label = QLabel("1")
        self.parallel_value_label.setObjectName("parallelValue")

        par_header = QHBoxLayout()
        par_header.addWidget(par_title)
        par_header.addStretch()
        par_header.addWidget(self.parallel_value_label)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(16)
        self.slider.setValue(1)
        self.slider.valueChanged.connect(self._update_parallel_label)

        # ── Progress ────────────────────────────────────────────────────────
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.stats_label = QLabel("Speed: -- | ETA: --")
        self.stats_label.setObjectName("statsLabel")

        # ── Action buttons ─────────────────────────────────────────────────
        self.run_btn = QPushButton("⬆  Run Restore")
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.clicked.connect(self.run_restore)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("ghostBtn")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_restore)

        # ── Assemble ────────────────────────────────────────────────────────
        layout.addWidget(uri_lbl)
        layout.addWidget(self.uri)
        layout.addWidget(db_lbl)
        layout.addWidget(self.db)
        layout.addWidget(file_lbl)
        layout.addLayout(file_row)
        layout.addLayout(par_header)
        layout.addWidget(self.slider)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.stats_label)
        layout.addWidget(self.run_btn)
        layout.addWidget(self.cancel_btn)
        layout.addStretch()

        self.setLayout(layout)

    def _update_parallel_label(self, value):
        self.parallel_value_label.setText(str(value))

    # -----------------------------
    # File Picker
    # -----------------------------

    def select_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Backup Archive",
            "./backups",
            "MongoDB Archives (*.archive.gz);;All Files (*)"
        )
        if file:
            self.file.setText(file)

    # -----------------------------
    # Run Restore (Non-blocking)
    # -----------------------------

    def run_restore(self):
        uri = self.uri.text().strip()
        db_name = self.db.text().strip()
        backup_file = self.file.text().strip()

        # Validate connection
        validation = validate_restore_connection(uri, db_name)
        if not validation.get("success"):
            QMessageBox.warning(self, "Connection Failed", validation.get("error"))
            return

        command, error = build_restore_command(
            backup_file=backup_file,
            uri=uri,
            db_name=db_name,
            drop=True,  # always drop for a clean restore
            parallel=self.slider.value(),
        )

        if error:
            QMessageBox.warning(self, "Error", error)
            return

        self.progress_bar.setValue(0)
        self.stats_label.setText("Speed: -- | ETA: --")
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)

        self.worker = CommandWorker(
            command,
            archive_path=backup_file,
            total_steps=0,
        )

        self.worker.log_signal.connect(self.log_callback)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.stats_signal.connect(self.stats_label.setText)
        self.worker.finished_signal.connect(
            lambda result: self.on_restore_finished(result, uri, db_name)
        )

        self.worker.start()

    def on_restore_finished(self, result, uri, db_name):
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

        if not result.get("success"):
            error = result.get("error", "Unknown error")
            self.log_callback(format_log(f"❌ Restore failed: {error}"))
            return

        self.progress_bar.setValue(100)

        # Query the target DB for the actual collection list
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=3000)
            collections = sorted(client[db_name].list_collection_names())
            client.close()
            count = len(collections)
            names = ", ".join(collections) if collections else "(none)"
            self.log_callback(format_log(
                f"✅ Restore completed — {count} collection(s) in '{db_name}': {names}"
            ))
        except Exception:
            self.log_callback(format_log("✅ Restore completed successfully"))

    def cancel_restore(self):
        if self.worker:
            self.worker.cancel()
            self.log_callback(format_log("🛑 Restore cancelled"))
