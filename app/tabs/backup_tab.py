from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from app.services.backup_service import backup_database
from app.utils.logger import format_log
from app.utils.constants import DEFAULT_BACKUP_DIR


# ==========================
# Background Worker
# ==========================
class BackupWorker(QThread):
    finished_signal = pyqtSignal(dict)

    def __init__(self, uri, db, parallel, exclude_collections):
        super().__init__()
        self.uri = uri
        self.db = db
        self.parallel = parallel
        self.exclude_collections = exclude_collections

    def run(self):
        result = backup_database(
            uri=self.uri,
            db_name=self.db,
            backup_root=DEFAULT_BACKUP_DIR,
            parallel=self.parallel,
            exclude_collections=self.exclude_collections,
        )
        self.finished_signal.emit(result)


# ==========================
# Backup Tab
# ==========================
class BackupTab(QWidget):
    def __init__(self, log_callback):
        super().__init__()
        self.log_callback = log_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Mongo URI
        self.uri = QLineEdit()
        self.uri.setPlaceholderText("Mongo URI")

        # Database
        self.db = QLineEdit()
        self.db.setPlaceholderText("Database Name")

        # Exclude Collections
        self.exclude_input = QLineEdit()
        self.exclude_input.setPlaceholderText(
            "Exclude Collections (comma-separated, optional)"
        )

        # Parallel Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(16)
        self.slider.setValue(1)

        self.run_btn = QPushButton("Run Backup")
        self.run_btn.clicked.connect(self.run_backup)

        layout.addWidget(QLabel("Mongo URI"))
        layout.addWidget(self.uri)

        layout.addWidget(QLabel("Database"))
        layout.addWidget(self.db)

        layout.addWidget(QLabel("Exclude Collections (Optional)"))
        layout.addWidget(self.exclude_input)

        layout.addWidget(QLabel("Parallel Collections"))
        layout.addWidget(self.slider)

        layout.addWidget(self.run_btn)

        self.setLayout(layout)

    def run_backup(self):
        uri = self.uri.text().strip()
        db = self.db.text().strip()

        if not uri or not db:
            QMessageBox.warning(self, "Error", "URI and Database are required")
            return

        # Parse exclude collections
        exclude_text = self.exclude_input.text().strip()
        exclude_collections = []

        if exclude_text:
            exclude_collections = [
                col.strip()
                for col in exclude_text.split(",")
                if col.strip()
            ]

        self.log_callback(format_log("Starting backup..."))

        if exclude_collections:
            self.log_callback(
                format_log(
                    f"Excluding collections: {', '.join(exclude_collections)}"
                )
            )

        self.run_btn.setEnabled(False)

        self.worker = BackupWorker(
            uri,
            db,
            self.slider.value(),
            exclude_collections,
        )

        self.worker.finished_signal.connect(self.on_backup_finished)
        self.worker.start()

    def on_backup_finished(self, result):
        self.run_btn.setEnabled(True)

        if result["success"]:
            self.log_callback(
                format_log(
                    f"Backup created: {result['backup_file']} "
                    f"({result['size_mb']} MB)"
                )
            )
        else:
            self.log_callback(format_log("Backup failed"))
