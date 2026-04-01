from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QSlider, QScrollArea,
    QHBoxLayout, QMessageBox, QGridLayout,
    QProgressBar
)
from PyQt6.QtCore import Qt
import os
import datetime

from app.services.mongo_service import get_collections
from app.services.backup_service import validate_connection, apply_retention_policy
from app.utils.logger import format_log
from app.widgets.collection_card import CollectionCard
from app.worker import CommandWorker


class BackupTab(QWidget):
    def __init__(self, log_callback):
        super().__init__()
        self.log_callback = log_callback
        self.selected_collections = set()
        self.collection_cards = []
        self.all_collections = []
        self.columns = 3
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

        # ── Database Name + Fetch ───────────────────────────────────────
        db_lbl = QLabel("Database Name")
        db_lbl.setObjectName("sectionLabel")
        self.db = QLineEdit()
        self.db.setPlaceholderText("Select or type database")

        fetch_btn = QPushButton("↻  Fetch")
        fetch_btn.setObjectName("fetchBtn")
        fetch_btn.clicked.connect(self.load_collections)

        db_row = QHBoxLayout()
        db_row.setSpacing(8)
        db_row.addWidget(self.db, 1)
        db_row.addWidget(fetch_btn)

        # ── Collections header ──────────────────────────────────────────
        coll_title = QLabel("Collections")
        coll_title.setObjectName("sectionTitle")

        self.badge = QLabel("SELECTED: 0")
        self.badge.setObjectName("selectedBadge")

        select_all_btn = QPushButton("SELECT ALL")
        select_all_btn.setObjectName("linkBtn")
        select_all_btn.clicked.connect(self.select_all)

        none_btn = QPushButton("NONE")
        none_btn.setObjectName("linkBtn")
        none_btn.clicked.connect(self.deselect_all)

        coll_header = QHBoxLayout()
        coll_header.setSpacing(8)
        coll_header.addWidget(coll_title)
        coll_header.addWidget(self.badge)
        coll_header.addStretch()
        coll_header.addWidget(select_all_btn)
        coll_header.addWidget(none_btn)

        # ── Filter input ─────────────────────────────────────────────────
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Filter collections...")
        self.search_input.textChanged.connect(self.filter_collections)

        # ── Collection scroll ──────────────────────────────────────────────
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.collection_container = QWidget()
        self.collection_grid = QGridLayout()
        self.collection_grid.setSpacing(0)  # list-item style, no gaps
        self.collection_grid.setContentsMargins(0, 0, 0, 0)
        self.collection_container.setLayout(self.collection_grid)
        self.scroll_area.setWidget(self.collection_container)

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
        self.run_btn = QPushButton("☁  Run Backup")
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.clicked.connect(self.run_backup)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("ghostBtn")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_backup)

        # ── Assemble ────────────────────────────────────────────────────────
        layout.addWidget(uri_lbl)
        layout.addWidget(self.uri)
        layout.addWidget(db_lbl)
        layout.addLayout(db_row)
        layout.addLayout(coll_header)
        layout.addWidget(self.search_input)
        layout.addWidget(self.scroll_area, 1)
        layout.addLayout(par_header)
        layout.addWidget(self.slider)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.stats_label)
        layout.addWidget(self.run_btn)
        layout.addWidget(self.cancel_btn)

        self.setLayout(layout)

    def _update_parallel_label(self, value):
        self.parallel_value_label.setText(str(value))

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
        self.all_collections = collections
        self.populate_grid(collections)
        self.select_all()

        self.log_callback(format_log(f"Loaded {len(collections)} collections"))

    def populate_grid(self, collections):
        for i in reversed(range(self.collection_grid.count())):
            widget = self.collection_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.collection_cards = []

        # Single-column list style to match mockup
        for index, name in enumerate(collections):
            card = CollectionCard(name)
            card.toggled.connect(self.on_collection_toggled)
            self.collection_grid.addWidget(card, index, 0)
            self.collection_cards.append(card)

    def resizeEvent(self, event):
        if self.all_collections:
            self.populate_grid(self.all_collections)
        super().resizeEvent(event)

    # -----------------------------
    # Selection
    # -----------------------------

    def on_collection_toggled(self, name, selected):
        if selected:
            self.selected_collections.add(name)
        else:
            self.selected_collections.discard(name)
        count = len(self.selected_collections)
        self.badge.setText(f"SELECTED: {count}")

    def select_all(self):
        for card in self.collection_cards:
            card.set_selected(True)

    def deselect_all(self):
        for card in self.collection_cards:
            card.set_selected(False)

    # -----------------------------
    # Search
    # -----------------------------

    def filter_collections(self, text):
        filtered = [
            name for name in self.all_collections
            if text.lower() in name.lower()
        ]
        self.populate_grid(filtered)

    # -----------------------------
    # Run Backup (Non-blocking)
    # -----------------------------

    def run_backup(self):

        if not self.selected_collections:
            QMessageBox.warning(self, "Error", "Select at least one collection")
            return

        uri = self.uri.text().strip()
        db_name = self.db.text().strip()

        validation = validate_connection(uri, db_name)
        if not validation.get("success"):
            QMessageBox.warning(self, "Connection Failed", validation.get("error"))
            return

        os.makedirs("./backups", exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        archive_path = f"./backups/{db_name}_backup_{timestamp}.archive.gz"

        command = [
            "mongodump",
            "--uri", uri,
            "--db", db_name,
            f"--archive={archive_path}",
            "--gzip",
            f"--numParallelCollections={self.slider.value()}"
        ]

        # mongodump has no multi-collection include flag.
        # Inverse selection: exclude collections that are NOT selected.
        all_cols = set(self.all_collections)
        selected_cols = set(self.selected_collections)
        for col in (all_cols - selected_cols):
            command.append(f"--excludeCollection={col}")

        self.progress_bar.setValue(0)
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)

        self.worker = CommandWorker(
            command,
            archive_path=archive_path,
            total_steps=len(self.selected_collections)
        )

        self.worker.log_signal.connect(self.log_callback)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.stats_signal.connect(self.stats_label.setText)
        self.worker.finished_signal.connect(
            lambda result: self.on_backup_finished(result, archive_path)
        )

        self.worker.start()

    def on_backup_finished(self, result, archive_path):

        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

        if not result.get("success"):
            self.log_callback("❌ Backup failed.")
            return

        if not os.path.exists(archive_path):
            self.log_callback("❌ Archive not created.")
            return

        size_bytes = os.path.getsize(archive_path)
        size_mb = round(size_bytes / (1024 * 1024), 2)

        self.progress_bar.setValue(100)

        self.log_callback(
            f"✅ Backup created: {archive_path} ({size_mb} MB)"
        )

        # Apply retention policy
        apply_retention_policy("./backups", keep_last=5)

    def cancel_backup(self):
        if self.worker:
            self.worker.cancel()
            self.log_callback("🛑 Backup cancelled.")