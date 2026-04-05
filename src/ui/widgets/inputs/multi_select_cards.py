"""
MultiSelectCards — Artist card grid selector.
Allows selecting 1..max_selections items. Cards beyond the limit are disabled.
"""
from PySide6.QtWidgets import QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor

from src.ui.styles.theme import ARTIST_COLORS, Palette


class ArtistCard(QFrame):
    """Single selectable artist card."""

    clicked = Signal(str)  # emits artist value

    def __init__(
        self,
        value: str,
        label: str,
        description: str,
        accent_color: str = "#C9A96E",
        parent=None,
    ):
        super().__init__(parent)
        self.value = value
        self._selected = False
        self._disabled_card = False
        self.accent_color = accent_color

        self.setObjectName("artistCard")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedHeight(76)
        self.setMinimumWidth(130)
        self._build_ui(label, description)

    def _build_ui(self, label: str, description: str) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        # Avatar circle
        avatar = QLabel(label[0].upper())
        avatar.setFixedSize(32, 32)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            QLabel {{
                background-color: {self.accent_color}22;
                color: {self.accent_color};
                border: 1px solid {self.accent_color}55;
                border-radius: 16px;
                font-size: 13px;
                font-weight: 700;
            }}
        """)

        # Text column
        text_col = QVBoxLayout()
        text_col.setSpacing(3)
        text_col.setContentsMargins(0, 0, 0, 0)

        name_lbl = QLabel(label)
        name_lbl.setStyleSheet(
            "font-size: 13px; font-weight: 600; "
            f"color: {Palette.TEXT}; background: transparent;"
        )

        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet(
            f"font-size: 11px; color: {Palette.TEXT_SUB}; background: transparent;"
        )
        desc_lbl.setWordWrap(True)

        text_col.addWidget(name_lbl)
        text_col.addWidget(desc_lbl)

        layout.addWidget(avatar)
        layout.addLayout(text_col, 1)

    # ── Selection state ──────────────────────────────────────────────────────

    def set_selected(self, value: bool) -> None:
        self._selected = value
        if value:
            self.setStyleSheet(f"""
                QFrame#artistCard {{
                    background-color: {Palette.BG_CARD_SEL};
                    border: 1.5px solid {self.accent_color};
                }}
                QFrame#artistCard:hover {{
                    background-color: {Palette.BG_CARD_SEL};
                    border: 1.5px solid {self.accent_color};
                }}
            """)
        else:
            self.setStyleSheet("")
        self.update()

    def set_disabled_card(self, value: bool) -> None:
        self._disabled_card = value
        self.setEnabled(not value)
        self.setCursor(
            QCursor(Qt.CursorShape.ForbiddenCursor if value else Qt.CursorShape.PointingHandCursor)
        )

    @property
    def is_selected(self) -> bool:
        return self._selected

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and not self._disabled_card:
            self.clicked.emit(self.value)
        super().mousePressEvent(event)


class MultiSelectCards(QWidget):
    """
    Artist card grid that enforces a max_selections limit.
    Emits selection_changed(selected_values: list[str]).
    """

    selection_changed = Signal(list)

    def __init__(self, input_def, parent=None):
        super().__init__(parent)
        self.input_def = input_def
        self.max_selections: int = input_def.max_selections
        self._selected: list[str] = []
        self._cards: dict[str, ArtistCard] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(8)

        # Section label
        lbl = QLabel(self.input_def.label)
        lbl.setObjectName("sectionLabel")
        outer.addWidget(lbl)

        # Grid — 2 columns
        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setContentsMargins(0, 4, 0, 0)

        for i, opt in enumerate(self.input_def.options):
            accent = ARTIST_COLORS.get(opt.value, Palette.ACCENT)
            card = ArtistCard(
                value=opt.value,
                label=opt.label,
                description=opt.description,
                accent_color=accent,
            )
            card.clicked.connect(self._on_card_click)
            self._cards[opt.value] = card
            row, col = divmod(i, 2)
            grid.addWidget(card, row, col)

        outer.addLayout(grid)

        # Hint
        self._hint = QLabel(f"最多選 {self.max_selections} 名")
        self._hint.setObjectName("dimLabel")
        outer.addWidget(self._hint)

    def _on_card_click(self, value: str) -> None:
        if value in self._selected:
            self._selected.remove(value)
            self._cards[value].set_selected(False)
        else:
            if len(self._selected) >= self.max_selections:
                return
            self._selected.append(value)
            self._cards[value].set_selected(True)

        maxed = len(self._selected) >= self.max_selections
        for v, card in self._cards.items():
            if v not in self._selected:
                card.set_disabled_card(maxed)

        self.selection_changed.emit(list(self._selected))

    def get_value(self) -> list[str]:
        return list(self._selected)

    def reset(self) -> None:
        self._selected.clear()
        for card in self._cards.values():
            card.set_selected(False)
            card.set_disabled_card(False)
        self.selection_changed.emit([])
