from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QFileDialog,
    QScrollArea, QHBoxLayout, QMessageBox
)

from app.services.restore_service import restore_database
from app.services.mongo_service import get_collections
from app.utils.logger import format_log


class RestoreTab(QWidget):
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

        # Target DB
        self.db = QLineEdit()
        self.db.setPlaceholderText("Target Database")

        # Backup file
        self.file = QLineEdit()
        browse_btn = QPushButton("Select Backup File")
        browse_btn.clicked.connect(self.select_file)

        # Drop checkbox
        self.drop_checkbox = QCheckBox("Drop Existing Collections")

        # Fetch collections (optional)
        fetch_btn = QPushButton("Fetch Target Collections")
        fetch_btn.clicked.connect(self.load_collections)

        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.collection_container = QWidget()
        self.collection_layout = QVBoxLayout()
        self.collection_container.setLayout(self.collection_layout)
        self.scroll_area.setWidget(self.collection_container)

        # Select/Deselect
        btn_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        deselect_all_btn = QPushButton("Deselect All")

        select_all_btn.clicked.connect(self.select_all)
        deselect_all_btn.clicked.connect(self.deselect_all)

        btn_layout.addWidget(select_all_btn)
        btn_layout.addWidget(deselect_all_btn)

        run_btn = QPushButton("Run Restore")
        run_btn.clicked.connect(self.run_restore)

        # Layout
        layout.addWidget(QLabel("Mongo URI"))
        layout.addWidget(self.uri)

        layout.addWidget(QLabel("Target Database"))
        layout.addWidget(self.db)

        layout.addWidget(self.file)
        layout.addWidget(browse_btn)

        layout.addWidget(self.drop_checkbox)
        layout.addWidget(fetch_btn)

        layout.addWidget(QLabel("Collections (Optional)"))
        layout.addLayout(btn_layout)
        layout.addWidget(self.scroll_area)

        layout.addWidget(run_btn)

        self.setLayout(layout)

    # -----------------------------
    # File Picker
    # -----------------------------

    def select_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Backup",
            "",
            "Tar Files (*.tar.gz)"
        )
        if file:
            self.file.setText(file)

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
    # Run Restore
    # -----------------------------

    def run_restore(self):
        selected = [
            cb.text()
            for cb in self.collection_checkboxes
            if cb.isChecked()
        ]

        result = restore_database(
            backup_file=self.file.text().strip(),
            uri=self.uri.text().strip(),
            db_name=self.db.text().strip(),
            drop=self.drop_checkbox.isChecked(),
            include_collections=selected
        )

        if result.get("success"):
            self.log_callback(format_log("Restore completed successfully"))
        else:
            self.log_callback(format_log(
                f"Restore failed: {result.get('error', 'Unknown error')}"
            ))
