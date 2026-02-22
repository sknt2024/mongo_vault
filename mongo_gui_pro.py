import sys
import os
import subprocess
import datetime
import shutil
import tarfile
import tempfile

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTabWidget,
    QLabel, QLineEdit, QPushButton, QFileDialog,
    QTextEdit, QHBoxLayout, QMessageBox, QComboBox
)
from PyQt6.QtCore import QThread, pyqtSignal


# ==========================
# Worker Thread
# ==========================
class Worker(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            for line in process.stdout:
                self.log_signal.emit(line.strip())

            process.wait()

            if process.returncode == 0:
                self.finished_signal.emit(True)
            else:
                self.finished_signal.emit(False)

        except Exception as e:
            self.log_signal.emit(str(e))
            self.finished_signal.emit(False)


# ==========================
# Main App
# ==========================
class MongoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MongoDB Backup & Restore")
        self.setGeometry(300, 200, 800, 600)

        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_backup_tab(), "Backup")
        self.tabs.addTab(self.create_restore_tab(), "Restore")

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        layout.addWidget(self.tabs)
        layout.addWidget(QLabel("Logs"))
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    # ==========================
    # Backup Tab
    # ==========================
    def create_backup_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.backup_uri = QLineEdit()
        self.backup_uri.setPlaceholderText("Mongo URI")

        self.backup_db = QLineEdit()
        self.backup_db.setPlaceholderText("Database Name")

        self.backup_dir = QLineEdit("./backups")

        browse_btn = QPushButton("Browse Backup Directory")
        browse_btn.clicked.connect(self.select_backup_dir)

        run_btn = QPushButton("Run Backup")
        run_btn.clicked.connect(self.run_backup)

        layout.addWidget(QLabel("Mongo URI"))
        layout.addWidget(self.backup_uri)
        layout.addWidget(QLabel("Database"))
        layout.addWidget(self.backup_db)
        layout.addWidget(QLabel("Backup Directory"))
        layout.addWidget(self.backup_dir)
        layout.addWidget(browse_btn)
        layout.addWidget(run_btn)

        widget.setLayout(layout)
        return widget

    # ==========================
    # Restore Tab
    # ==========================
    def create_restore_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.restore_uri = QLineEdit()
        self.restore_uri.setPlaceholderText("Mongo URI")

        self.restore_db = QLineEdit()
        self.restore_db.setPlaceholderText("Target Database")

        self.restore_file = QLineEdit()

        browse_file_btn = QPushButton("Select Backup File")
        browse_file_btn.clicked.connect(self.select_restore_file)

        self.restore_mode = QComboBox()
        self.restore_mode.addItems(["Append (Safe)", "Replace (--drop)"])

        run_btn = QPushButton("Run Restore")
        run_btn.clicked.connect(self.run_restore)

        layout.addWidget(QLabel("Mongo URI"))
        layout.addWidget(self.restore_uri)
        layout.addWidget(QLabel("Target Database"))
        layout.addWidget(self.restore_db)
        layout.addWidget(QLabel("Backup File (.tar.gz)"))
        layout.addWidget(self.restore_file)
        layout.addWidget(browse_file_btn)
        layout.addWidget(QLabel("Restore Mode"))
        layout.addWidget(self.restore_mode)
        layout.addWidget(run_btn)

        widget.setLayout(layout)
        return widget

    # ==========================
    # UI Actions
    # ==========================
    def select_backup_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Backup Directory")
        if folder:
            self.backup_dir.setText(folder)

    def select_restore_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Select Backup File", "", "Tar Files (*.tar.gz)"
        )
        if file:
            self.restore_file.setText(file)

    def append_log(self, text):
        self.log_output.append(text)

    def show_result(self, success):
        if success:
            QMessageBox.information(self, "Success", "Operation completed successfully!")
        else:
            QMessageBox.critical(self, "Error", "Operation failed. Check logs.")

    # ==========================
    # Backup Logic
    # ==========================
    def run_backup(self):
        uri = self.backup_uri.text()
        db = self.backup_db.text()
        directory = self.backup_dir.text()

        if not uri or not db:
            QMessageBox.warning(self, "Error", "URI and DB required")
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_path = os.path.join(directory, timestamp)

        os.makedirs(backup_path, exist_ok=True)

        command = [
            "mongodump",
            "--uri", uri,
            "--db", db,
            "--out", backup_path
        ]

        self.worker = Worker(command)
        self.worker.log_signal.connect(self.append_log)
        self.worker.finished_signal.connect(self.show_result)
        self.worker.start()

    # ==========================
    # Restore Logic
    # ==========================
    def run_restore(self):
        uri = self.restore_uri.text()
        db = self.restore_db.text()
        file = self.restore_file.text()

        if not uri or not db or not file:
            QMessageBox.warning(self, "Error", "All fields required")
            return

        temp_dir = tempfile.mkdtemp()

        try:
            with tarfile.open(file, "r:gz") as tar:
                tar.extractall(temp_dir)

            timestamp_dir = os.listdir(temp_dir)[0]
            restore_path = os.path.join(temp_dir, timestamp_dir)

            command = [
                "mongorestore",
                "--uri", uri,
                "--dir", restore_path
            ]

            if self.restore_mode.currentIndex() == 1:
                command.append("--drop")

            self.worker = Worker(command)
            self.worker.log_signal.connect(self.append_log)
            self.worker.finished_signal.connect(self.show_result)
            self.worker.start()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# ==========================
# Run App
# ==========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MongoApp()
    window.show()
    sys.exit(app.exec())
