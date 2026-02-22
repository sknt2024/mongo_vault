from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtCore import QThread, pyqtSignal

from app.services.restore_service import restore_database
from app.utils.logger import format_log


# ==========================
# Background Worker
# ==========================
class RestoreWorker(QThread):
    finished_signal = pyqtSignal(dict)

    def __init__(self, backup_file, uri, db, drop):
        super().__init__()
        self.backup_file = backup_file
        self.uri = uri
        self.db = db
        self.drop = drop

    def run(self):
        result = restore_database(
            backup_file=self.backup_file,
            uri=self.uri,
            db_name=self.db,
            drop=self.drop,
            parallel=1,
        )
        self.finished_signal.emit(result)


# ==========================
# Restore Tab
# ==========================
class RestoreTab(QWidget):
    def __init__(self, log_callback):
        super().__init__()
        self.log_callback = log_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.uri = QLineEdit()
        self.uri.setPlaceholderText("Mongo URI")

        self.file = QLineEdit()
        self.db = QLineEdit()
        self.db.setPlaceholderText("Target Database")

        self.drop_checkbox = QCheckBox("Drop Existing Collections")

        browse_btn = QPushButton("Select Backup File")
        browse_btn.clicked.connect(self.select_file)

        run_btn = QPushButton("Run Restore")
        run_btn.clicked.connect(self.run_restore)
        self.run_btn = run_btn

        layout.addWidget(QLabel("Mongo URI"))
        layout.addWidget(self.uri)
        layout.addWidget(QLabel("Target Database"))
        layout.addWidget(self.db)
        layout.addWidget(self.file)
        layout.addWidget(browse_btn)
        layout.addWidget(self.drop_checkbox)
        layout.addWidget(run_btn)

        self.setLayout(layout)

    def select_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Backup",
            "",
            "Tar Files (*.tar.gz)",
        )
        if file:
            self.file.setText(file)

    def run_restore(self):
        uri = self.uri.text().strip()
        db = self.db.text().strip()
        backup_file = self.file.text().strip()

        if not uri or not db or not backup_file:
            QMessageBox.warning(self, "Error", "All fields are required")
            return

        self.log_callback(format_log("Starting restore..."))
        self.run_btn.setEnabled(False)

        self.worker = RestoreWorker(
            backup_file,
            uri,
            db,
            self.drop_checkbox.isChecked(),
        )

        self.worker.finished_signal.connect(self.on_restore_finished)
        self.worker.start()

    def on_restore_finished(self, result):
        self.run_btn.setEnabled(True)

        if result["success"]:
            self.log_callback(format_log("Restore completed successfully"))

            if result.get("duplicate_count", 0) > 0:
                self.log_callback(
                    format_log(
                        f"{result['duplicate_count']} duplicate documents ignored"
                    )
                )

            if result.get("index_conflicts", 0) > 0:
                self.log_callback(
                    format_log(
                        f"{result['index_conflicts']} index conflicts detected"
                    )
                )

            self.log_callback(format_log(f"Log file: {result['log_file']}"))
        else:
            self.log_callback(format_log("Restore failed"))
