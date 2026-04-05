"""
DescriptionPanel — Left column: character / scene description input.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QSizePolicy,
)
from PySide6.QtCore import Qt

from src.ui.styles.theme import Palette


class DescriptionPanel(QWidget):
    """
    Simple left-column panel that holds the free-text description input.
    MainWindow reads get_description() before calling the prompt service.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(200)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 16, 24)
        layout.setSpacing(10)

        # Section header
        header = QLabel("角色 / 場景描述")
        header.setObjectName("sectionLabel")
        layout.addWidget(header)

        # Hint
        hint = QLabel("用中文或英文描述你想要的角色、場景、氛圍。LLM 會自動補全細節。")
        hint.setObjectName("dimLabel")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        layout.addSpacing(4)

        # Description textarea — flex, fills available height
        self._desc_edit = QTextEdit()
        self._desc_edit.setPlaceholderText(
            "例如：\n\n"
            "銀髮藍眼的魔法少女，\n"
            "手持星形法杖，\n"
            "夜晚的圖書館…\n\n"
            "（簡單描述也沒關係）"
        )
        self._desc_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self._desc_edit, 1)

    # ── Public API ───────────────────────────────────────────────────────────

    def get_description(self) -> str:
        return self._desc_edit.toPlainText().strip()

    def validate(self) -> tuple[bool, str]:
        if not self.get_description():
            return False, "請輸入角色 / 場景描述"
        return True, ""

    def set_loading(self, loading: bool) -> None:
        self._desc_edit.setReadOnly(loading)
        self._desc_edit.setStyleSheet(
            f"QTextEdit {{ color: {Palette.TEXT_DIM}; }}" if loading else ""
        )

    def focus_input(self) -> None:
        self._desc_edit.setFocus()
