"""
SingleSelectPills — Horizontal pill button group for single-select options.
Used for aspect ratio selection.
"""
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor


# Visual ratio indicators using Unicode block characters
_RATIO_ICONS: dict[str, str] = {
    "16:9": "▬",
    "1:1":  "■",
    "4:3":  "▰",
    "3:4":  "▮",
    "9:16": "▮",
}


class SingleSelectPills(QWidget):
    """
    Renders a row of pill buttons where exactly one is selected at a time.
    Emits selection_changed(value: str).
    """

    selection_changed = Signal(str)

    def __init__(self, input_def, parent=None):
        super().__init__(parent)
        self.input_def = input_def
        self._selected: str = input_def.default or ""
        self._buttons: dict[str, QPushButton] = {}
        self._build_ui()
        if self._selected:
            self._apply_selection(self._selected, emit=False)

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(8)

        lbl = QLabel(self.input_def.label)
        lbl.setObjectName("sectionLabel")
        outer.addWidget(lbl)

        row = QHBoxLayout()
        row.setSpacing(6)
        row.setContentsMargins(0, 2, 0, 0)

        for opt in self.input_def.options:
            icon = _RATIO_ICONS.get(opt.value, "")
            text = f"{icon}  {opt.label}" if icon else opt.label
            btn = QPushButton(text)
            btn.setObjectName("pill")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda _checked, v=opt.value: self._on_click(v))
            self._buttons[opt.value] = btn
            row.addWidget(btn)

        row.addStretch()
        outer.addLayout(row)

    def _on_click(self, value: str) -> None:
        self._apply_selection(value, emit=True)

    def _apply_selection(self, value: str, *, emit: bool) -> None:
        self._selected = value
        for v, btn in self._buttons.items():
            btn.setProperty("selected", v == value)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        if emit:
            self.selection_changed.emit(value)

    def get_value(self) -> str:
        return self._selected

    def reset(self) -> None:
        default = self.input_def.default or ""
        self._apply_selection(default, emit=False)
