"""
CompactSingleSelect  — Labelled QComboBox for single-value pill inputs.
CompactCategorySelect — Labelled QComboBox for grouped category inputs.
Both expose the same get_value() / reset() interface as their larger siblings.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QLineEdit
from PySide6.QtGui import QColor, QCursor, QStandardItem
from PySide6.QtCore import Qt

from src.ui.styles.theme import Palette


class CompactSingleSelect(QWidget):
    def __init__(self, input_def, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        lbl = QLabel(input_def.label)
        lbl.setObjectName("dimLabel")
        layout.addWidget(lbl)

        self._combo = QComboBox()
        self._combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        for opt in input_def.options:
            self._combo.addItem(opt.label, opt.value)

        # Honour default value if set
        default = getattr(input_def, "default", "")
        if default:
            idx = next(
                (i for i, opt in enumerate(input_def.options) if opt.value == default), 0
            )
            self._combo.setCurrentIndex(idx)

        layout.addWidget(self._combo)

    def get_value(self) -> str:
        return self._combo.currentData() or ""

    def reset(self) -> None:
        self._combo.setCurrentIndex(0)


class CompactTextInput(QWidget):
    def __init__(self, input_def, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        lbl = QLabel(input_def.label)
        lbl.setObjectName("dimLabel")
        layout.addWidget(lbl)

        self._line_edit = QLineEdit()
        self._line_edit.setPlaceholderText(
            getattr(input_def, "placeholder", "")
        )
        self._line_edit.setMinimumWidth(180)
        layout.addWidget(self._line_edit)

    def get_value(self) -> str:
        return self._line_edit.text().strip()

    def reset(self) -> None:
        self._line_edit.clear()


class CompactCategorySelect(QWidget):
    def __init__(self, input_def, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        lbl = QLabel(input_def.label)
        lbl.setObjectName("dimLabel")
        layout.addWidget(lbl)

        self._combo = QComboBox()
        self._combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._combo.setMinimumWidth(160)

        if getattr(input_def, "allow_empty", False):
            empty_label = getattr(input_def, "empty_label", "—")
            self._combo.addItem(empty_label, "")

        for cat in input_def.categories:
            # Non-selectable group header
            self._combo.addItem(f"  {cat.label}", None)
            header_item: QStandardItem = self._combo.model().item(self._combo.count() - 1)
            header_item.setEnabled(False)
            header_item.setForeground(QColor(Palette.TEXT_DIM))

            for opt in cat.options:
                self._combo.addItem(f"    {opt.label}", opt.value)

        layout.addWidget(self._combo)

    def get_value(self) -> str:
        return self._combo.currentData() or ""

    def reset(self) -> None:
        self._combo.setCurrentIndex(0)
