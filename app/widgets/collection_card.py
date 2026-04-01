from PyQt6.QtWidgets import QFrame, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont


class CollectionCard(QFrame):
    toggled = pyqtSignal(str, bool)

    def __init__(self, name: str):
        super().__init__()

        self.name = name
        self.selected = False

        self.setFixedHeight(48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("collectionCard")

        layout = QHBoxLayout()
        layout.setContentsMargins(14, 0, 16, 0)
        layout.setSpacing(12)

        # LEFT — square checkbox (QSS-driven)
        self.checkbox = QLabel("✓")
        self.checkbox.setObjectName("cardCheckbox")
        self.checkbox.setFixedSize(20, 20)
        self.checkbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.checkbox.setProperty("checked", False)

        # Collection name
        self.name_label = QLabel(name)
        self.name_label.setObjectName("cardName")
        font = QFont()
        font.setPointSize(11)
        self.name_label.setFont(font)

        layout.addWidget(self.checkbox)
        layout.addWidget(self.name_label)
        layout.addStretch()
        self.setLayout(layout)

        # Smooth press flicker animation
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(100)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    def _refresh(self, *widgets):
        for w in widgets:
            w.style().unpolish(w)
            w.style().polish(w)
            w.update()

    # ── Programmatic selection ───────────────────────────────────────────

    def set_selected(self, state: bool):
        if self.selected == state:
            return
        self.selected = state
        self.setProperty("selected", state)
        self.checkbox.setProperty("checked", state)
        self._refresh(self, self.checkbox)
        self.toggled.emit(self.name, self.selected)

    # ── Events ───────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        self.selected = not self.selected
        self.setProperty("selected", self.selected)
        self.checkbox.setProperty("checked", self.selected)
        self._animate()
        self._refresh(self, self.checkbox)
        self.toggled.emit(self.name, self.selected)

    def enterEvent(self, event):
        if not self.selected:
            self.setProperty("hovered", True)
            self._refresh(self)

    def leaveEvent(self, event):
        self.setProperty("hovered", False)
        self._refresh(self)

    def _animate(self):
        rect = self.geometry()
        self.anim.stop()
        self.anim.setStartValue(rect)
        self.anim.setEndValue(rect)
        self.anim.start()