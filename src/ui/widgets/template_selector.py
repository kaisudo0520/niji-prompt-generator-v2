"""
TemplateSelector — Horizontal strip of template chips.
Auto-hides when only one template is registered.
"""
from PySide6.QtWidgets import QWidget, QFrame, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor

from src.ui.styles.theme import Palette


class _TemplateChip(QFrame):
    """Single clickable template tab."""

    clicked = Signal(str)

    def __init__(
        self,
        template_id: str,
        name: str,
        icon: str = "",
        active: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.template_id = template_id
        self.setObjectName("templateChip")
        self.setProperty("active", active)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedHeight(32)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 14, 0)
        layout.setSpacing(7)

        if icon:
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 14px; background: transparent;")
            layout.addWidget(icon_lbl)

        weight = "600" if active else "400"
        color = Palette.ACCENT if active else Palette.TEXT_SUB
        self._name_lbl = QLabel(name)
        self._name_lbl.setStyleSheet(
            f"font-size: 13px; font-weight: {weight}; "
            f"color: {color}; background: transparent;"
        )
        layout.addWidget(self._name_lbl)

    def set_active(self, active: bool) -> None:
        self.setProperty("active", active)
        self.style().unpolish(self)
        self.style().polish(self)
        weight = "600" if active else "400"
        color = Palette.ACCENT if active else Palette.TEXT_SUB
        self._name_lbl.setStyleSheet(
            f"font-size: 13px; font-weight: {weight}; "
            f"color: {color}; background: transparent;"
        )

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.template_id)
        super().mousePressEvent(event)


class TemplateSelector(QWidget):
    """
    Horizontal strip of template chips.
    Call set_templates() after loading; widget auto-hides for single-template case.
    Emits template_changed(template_id: str).
    """

    template_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._chips: dict[str, _TemplateChip] = {}
        self._active: str = ""
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 6, 20, 6)
        layout.setSpacing(8)
        self._row = layout

    def set_templates(self, templates: list) -> None:
        """Populate from a list of TemplateDefinition-like objects."""
        # Clear previous
        while self._row.count():
            item = self._row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._chips.clear()

        for i, tmpl in enumerate(templates):
            chip = _TemplateChip(
                template_id=tmpl.id,
                name=tmpl.name,
                icon=getattr(tmpl, "icon", ""),
                active=(i == 0),
            )
            chip.clicked.connect(self._on_chip_click)
            self._chips[tmpl.id] = chip
            self._row.addWidget(chip)

        self._row.addStretch()

        if templates:
            self._active = templates[0].id

        # Hide when there is only one template — no choice to make
        self.setVisible(len(templates) > 1)

    def _on_chip_click(self, template_id: str) -> None:
        if template_id == self._active:
            return
        for tid, chip in self._chips.items():
            chip.set_active(tid == template_id)
        self._active = template_id
        self.template_changed.emit(template_id)
