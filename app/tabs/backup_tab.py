from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QSlider, QScrollArea,
    QCheckBox, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt

from app.services.backup_service import backup_database
from app.services.mongo_service import get_collections
from app.utils.logger import format_log


class BackupTab(QWidget):
    def __init__(self, log_callback):
        super().__init__()
        self.log_callback = log_callback
        self.collection_checkboxes = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # URI
        self.uri = QLineEdit()
        self.uri.setPlaceholderText("Mongo URI")

        # Database
        self.db = QLineEdit()
        self.db.setPlaceholderText("Database Name")

        fetch_btn = QPushButton("Fetch Collections")
        fetch_btn.clicked.connect(self.load_collections)

        # Scrollable collection area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.collection_container = QWidget()
        self.collection_layout = QVBoxLayout()
        self.collection_container.setLayout(self.collection_layout)
        self.scroll_area.setWidget(self.collection_container)

        # Select/Deselect buttons
        btn_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        deselect_all_btn = QPushButton("Deselect All")

        select_all_btn.clicked.connect(self.select_all)
        deselect_all_btn.clicked.connect(self.deselect_all)

        btn_layout.addWidget(select_all_btn)
        btn_layout.addWidget(deselect_all_btn)

        # Parallel slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(16)
        self.slider.setValue(1)

        # Run button
        self.run_btn = QPushButton("Run Backup")
        self.run_btn.clicked.connect(self.run_backup)

        # Layout
        layout.addWidget(QLabel("Mongo URI"))
        layout.addWidget(self.uri)

        layout.addWidget(QLabel("Database"))
        layout.addWidget(self.db)

        layout.addWidget(fetch_btn)
        layout.addWidget(QLabel("Collections"))
        layout.addLayout(btn_layout)
        layout.addWidget(self.scroll_area)

        layout.addWidget(QLabel("Parallel Collections"))
        layout.addWidget(self.slider)
        layout.addWidget(self.run_btn)

        self.setLayout(layout)

    # -----------------------------
    # Load Collections
    # -----------------------------

    def load_collections(self):
        uri = self.uri.text().strip()
        db_name = self.db.text().strip()

        if not uri or not db_name:
            QMessageBox.warning(self, "Error", "Provide URI and Database first")
            return

        collections = get_collections(uri, db_name)

        # Clear existing checkboxes
        for i in reversed(range(self.collection_layout.count())):
            widget = self.collection_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.collection_checkboxes = []

        for col in collections:
            checkbox = QCheckBox(col)
            checkbox.setChecked(True)
            self.collection_layout.addWidget(checkbox)
            self.collection_checkboxes.append(checkbox)

        self.log_callback(format_log(f"Loaded {len(collections)} collections"))

    def select_all(self):
        for cb in self.collection_checkboxes:
            cb.setChecked(True)

    def deselect_all(self):
        for cb in self.collection_checkboxes:
            cb.setChecked(False)

    # -----------------------------
    # Run Backup
    # -----------------------------

    def run_backup(self):
        selected = [
            cb.text()
            for cb in self.collection_checkboxes
            if cb.isChecked()
        ]

        result = backup_database(
            uri=self.uri.text().strip(),
            db_name=self.db.text().strip(),
            backup_root="./backups",
            parallel=self.slider.value(),
            include_collections=selected
        )

        if result.get("success"):
            self.log_callback(format_log(
                f"Backup created: {result['backup_file']} "
                f"({result['size_mb']} MB)"
            ))
        else:
            self.log_callback(format_log(
                f"Backup failed: {result.get('error', 'Unknown error')}"
            ))
