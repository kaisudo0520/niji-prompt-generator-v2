"""
CategorySelect — Grouped color palette selector with color swatch previews.
Supports an optional "let LLM decide" empty value.
"""
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor

from src.ui.styles.theme import COLOR_PREVIEW_MAP, Palette


class _ColorSwatch(QFrame):
    """Small circular color preview dot."""

    def __init__(self, hex_color: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(10, 10)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {hex_color};
                border-radius: 5px;
                border: none;
            }}
        """)


class ColorChip(QFrame):
    """Single selectable color chip with optional swatch dot."""

    clicked = Signal(str)  # emits value string

    def __init__(
        self,
        value: str,
        label: str,
        color_hex: str = "",
        is_empty: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.value = value
        self._selected = False
        self.is_empty = is_empty

        self.setObjectName("colorChip")
        if is_empty:
            self.setProperty("is_empty", True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedHeight(30)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 12, 0)
        layout.setSpacing(7)

        if color_hex and not is_empty:
            swatch = _ColorSwatch(color_hex)
            layout.addWidget(swatch)

        text_color = Palette.TEXT_DIM if is_empty else Palette.TEXT_SUB
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"font-size: 12px; color: {text_color}; background: transparent;"
            + (" font-style: italic;" if is_empty else "")
        )
        self._label = lbl
        layout.addWidget(lbl)
        layout.addStretch()

    # ── State ────────────────────────────────────────────────────────────────

    def set_selected(self, value: bool) -> None:
        self._selected = value
        self.setProperty("selected", value)
        self.style().unpolish(self)
        self.style().polish(self)

        accent = Palette.ACCENT if (value and not self.is_empty) else (
            Palette.TEXT_SUB if value else (Palette.TEXT_DIM if self.is_empty else Palette.TEXT_SUB)
        )
        style = (
            f"font-size: 12px; color: {accent}; background: transparent;"
            + (" font-style: italic;" if self.is_empty else "")
            + (" font-weight: 600;" if value and not self.is_empty else "")
        )
        self._label.setStyleSheet(style)

    @property
    def is_selected(self) -> bool:
        return self._selected

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.value)
        super().mousePressEvent(event)


class CategorySelect(QWidget):
    """
    Renders color palette options grouped by category.
    Optionally includes an "empty" / "let LLM decide" chip.
    Emits selection_changed(value: str).
    """

    selection_changed = Signal(str)

    def __init__(self, input_def, parent=None):
        super().__init__(parent)
        self.input_def = input_def
        self._selected: str = ""  # empty = LLM decides
        self._chips: dict[str, ColorChip] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(8)

        lbl = QLabel(self.input_def.label)
        lbl.setObjectName("sectionLabel")
        outer.addWidget(lbl)

        # "LLM decides" option
        if self.input_def.allow_empty:
            empty_chip = ColorChip(
                value="",
                label=self.input_def.empty_label,
                is_empty=True,
            )
            empty_chip.set_selected(True)  # default
            empty_chip.clicked.connect(lambda v="": self._on_click(v))
            self._chips[""] = empty_chip
            outer.addWidget(empty_chip)

        # Category groups
        for cat in self.input_def.categories:
            cat_header = QLabel(cat.label)
            cat_header.setStyleSheet(
                f"font-size: 11px; color: {Palette.TEXT_DIM}; "
                "background: transparent; margin-top: 4px;"
            )
            outer.addWidget(cat_header)

            row = QHBoxLayout()
            row.setSpacing(6)
            row.setContentsMargins(0, 2, 0, 0)

            for opt in cat.options:
                hex_color = COLOR_PREVIEW_MAP.get(opt.value, "")
                chip = ColorChip(
                    value=opt.value,
                    label=opt.label,
                    color_hex=hex_color,
                )
                chip.clicked.connect(lambda _v=opt.value: self._on_click(_v))
                self._chips[opt.value] = chip
                row.addWidget(chip)

            row.addStretch()
            outer.addLayout(row)

    def _on_click(self, value: str) -> None:
        self._selected = value
        for v, chip in self._chips.items():
            chip.set_selected(v == value)
        self.selection_changed.emit(value)

    def get_value(self) -> str:
        return self._selected

    def reset(self) -> None:
        self._on_click("")
