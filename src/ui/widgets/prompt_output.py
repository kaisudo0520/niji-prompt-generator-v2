"""
PromptOutput — Displays the generated Midjourney prompt and field breakdown.
Features: readonly monospace display, one-click copy, collapsible field details.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QGroupBox, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QGuiApplication, QCursor

from src.ui.styles.theme import Palette

_COPY_FLASH_QSS = (
    f"QTextEdit#promptOutput {{"
    f"  background-color: {Palette.ACCENT_BG};"
    f"  border-color: {Palette.ACCENT_DIM};"
    f"}}"
)


class _FieldRow(QWidget):
    """Single key/value row inside the field details panel."""

    def __init__(self, label: str, value: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 3, 0, 3)
        layout.setSpacing(12)

        key_lbl = QLabel(label)
        key_lbl.setFixedWidth(120)
        key_lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        key_lbl.setStyleSheet(
            f"font-size: 11px; color: {Palette.TEXT_DIM}; background: transparent;"
        )

        val_lbl = QLabel(value)
        val_lbl.setWordWrap(True)
        val_lbl.setStyleSheet(
            f"font-size: 11px; color: {Palette.TEXT_SUB}; background: transparent;"
        )
        val_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        layout.addWidget(key_lbl)
        layout.addWidget(val_lbl, 1)


class PromptOutput(QWidget):
    """
    Right-panel output widget.
    Call display_result() after generation, set_loading() during, display_error() on failure.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(300)
        self._build_ui()
        self._reset_status()

    # ── Build UI ─────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 24, 24, 24)
        outer.setSpacing(10)

        # Header row
        header = QHBoxLayout()
        result_lbl = QLabel("生成結果")
        result_lbl.setObjectName("sectionLabel")
        header.addWidget(result_lbl)
        header.addStretch()
        self._status_lbl = QLabel("等待生成…")
        self._status_lbl.setObjectName("dimLabel")
        header.addWidget(self._status_lbl)
        outer.addLayout(header)

        # Prompt text area
        self._prompt_edit = QTextEdit()
        self._prompt_edit.setObjectName("promptOutput")
        self._prompt_edit.setReadOnly(True)
        self._prompt_edit.setPlaceholderText(
            "生成的 Midjourney 提示詞將在此顯示…\n\n"
            "1. 在左側填寫角色描述\n"
            "2. 選擇繪師風格與比例\n"
            "3. 點擊「✦ 生成提示詞」"
        )
        outer.addWidget(self._prompt_edit, 1)

        # Copy button row
        copy_row = QHBoxLayout()
        copy_row.addStretch()
        self._copy_btn = QPushButton("複製提示詞")
        self._copy_btn.setObjectName("copyBtn")
        self._copy_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._copy_btn.setEnabled(False)
        self._copy_btn.clicked.connect(self._on_copy)
        copy_row.addWidget(self._copy_btn)
        outer.addLayout(copy_row)

        # Field details (collapsible QGroupBox)
        self._details_box = QGroupBox("欄位明細")
        details_layout = QVBoxLayout(self._details_box)
        details_layout.setContentsMargins(14, 8, 14, 12)
        details_layout.setSpacing(0)
        self._details_container = QWidget()
        self._details_inner = QVBoxLayout(self._details_container)
        self._details_inner.setContentsMargins(0, 0, 0, 0)
        self._details_inner.setSpacing(0)
        details_layout.addWidget(self._details_container)
        self._details_box.setVisible(False)
        outer.addWidget(self._details_box)

    # ── Public API ───────────────────────────────────────────────────────────

    def display_result(self, prompt: str, fields: dict[str, str]) -> None:
        self._prompt_edit.setPlainText(prompt)
        self._prompt_edit.setStyleSheet("")  # reset any error styling
        self._copy_btn.setEnabled(True)
        self._set_status("✓  已生成", Palette.SUCCESS)

        # Repopulate field details
        self._clear_details()
        if fields:
            for key, value in fields.items():
                row = _FieldRow(key, value)
                self._details_inner.addWidget(row)
            self._details_box.setVisible(True)

    def set_loading(self, loading: bool) -> None:
        if loading:
            self._prompt_edit.setPlainText("")
            self._prompt_edit.setStyleSheet("")
            self._copy_btn.setEnabled(False)
            self._details_box.setVisible(False)
            self._set_status("生成中…", Palette.TEXT_DIM)

    def display_error(self, message: str) -> None:
        self._prompt_edit.setPlainText(f"⚠  生成失敗\n\n{message}")
        self._prompt_edit.setStyleSheet(
            f"QTextEdit#promptOutput {{ color: {Palette.ERROR}; }}"
        )
        self._copy_btn.setEnabled(False)
        self._set_status("錯誤", Palette.ERROR)

    def clear(self) -> None:
        self._prompt_edit.clear()
        self._prompt_edit.setStyleSheet("")
        self._copy_btn.setEnabled(False)
        self._clear_details()
        self._details_box.setVisible(False)
        self._reset_status()

    # ── Private ──────────────────────────────────────────────────────────────

    def _set_status(self, text: str, color: str) -> None:
        self._status_lbl.setText(text)
        self._status_lbl.setStyleSheet(
            f"font-size: 11px; color: {color}; background: transparent;"
        )

    def _reset_status(self) -> None:
        self._set_status("等待生成…", Palette.TEXT_DIM)

    def _clear_details(self) -> None:
        while self._details_inner.count():
            item = self._details_inner.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _on_copy(self) -> None:
        text = self._prompt_edit.toPlainText().strip()
        if not text:
            return
        QGuiApplication.clipboard().setText(text)

        # Flash the prompt area
        self._prompt_edit.setStyleSheet(_COPY_FLASH_QSS)
        QTimer.singleShot(600, lambda: self._prompt_edit.setStyleSheet(""))

        # Button feedback
        self._copy_btn.setText("✓  已複製！")
        self._copy_btn.setProperty("copied", True)
        self._copy_btn.style().unpolish(self._copy_btn)
        self._copy_btn.style().polish(self._copy_btn)
        QTimer.singleShot(2200, self._reset_copy_btn)

    def _reset_copy_btn(self) -> None:
        self._copy_btn.setText("複製提示詞")
        self._copy_btn.setProperty("copied", False)
        self._copy_btn.style().unpolish(self._copy_btn)
        self._copy_btn.style().polish(self._copy_btn)
