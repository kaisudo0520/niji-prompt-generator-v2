"""
DynamicForm — Middle column: style selectors + Generate button.
Renders input widgets driven by TemplateDefinition.user_inputs.
Adding a new template requires zero changes here (unless a new input type is introduced).

Layout:
  ┌─────────────────────────────┐
  │  QScrollArea  (flex)        │  ← artist / ratio / palette selectors
  ├─────────────────────────────┤
  │  Footer: Generate button    │  ← always visible, never clipped
  └─────────────────────────────┘
"""
from PySide6.QtWidgets import (
    QScrollArea, QWidget, QVBoxLayout,
    QPushButton, QFrame, QSizePolicy, QGraphicsOpacityEffect,
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QCursor

from src.ui.widgets.inputs.multi_select_cards import MultiSelectCards
from src.ui.widgets.inputs.single_select_pills import SingleSelectPills
from src.ui.widgets.inputs.category_select import CategorySelect


_LOADING_FRAMES = ["✦  生成中", "✦  生成中 ·", "✦  生成中 ··", "✦  生成中 ···"]


class DynamicForm(QWidget):
    """
    Middle-panel selector widget.
    Emits generate_clicked() when the user presses the Generate button.
    Caller should read get_user_inputs() after receiving the signal.
    """

    generate_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(300)

        self._input_widgets: dict[str, QWidget] = {}
        self._loading = False
        self._pulse_anim: QPropertyAnimation | None = None
        self._loading_timer = QTimer(self)
        self._loading_timer.setInterval(400)
        self._loading_timer.timeout.connect(self._tick_loading)
        self._loading_tick = 0

        self._build_structure()

    # ── Structure (called once) ──────────────────────────────────────────────

    def _build_structure(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Scroll area ──────────────────────────────────────────────────────
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._inner = QWidget()
        self._inner.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._layout = QVBoxLayout(self._inner)
        self._layout.setContentsMargins(20, 24, 20, 20)
        self._layout.setSpacing(0)
        self._scroll.setWidget(self._inner)
        outer.addWidget(self._scroll, 1)

        # ── Footer separator ─────────────────────────────────────────────────
        sep = QFrame()
        sep.setObjectName("divider")
        outer.addWidget(sep)

        # ── Footer with Generate button ──────────────────────────────────────
        footer = QWidget()
        footer.setObjectName("generateFooter")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(20, 14, 20, 20)

        self._gen_btn = QPushButton("✦  生成提示詞")
        self._gen_btn.setObjectName("generateBtn")
        self._gen_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._gen_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._gen_btn.clicked.connect(self._on_generate_clicked)
        footer_layout.addWidget(self._gen_btn)

        outer.addWidget(footer)

    # ── Public API ───────────────────────────────────────────────────────────

    def render_template(self, template) -> None:
        """Rebuild the scrollable selector content for the given template."""
        self._input_widgets.clear()
        self._loading = False
        self._loading_timer.stop()
        self._stop_pulse()
        self._gen_btn.setText("✦  生成提示詞")
        self._gen_btn.setEnabled(True)

        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for input_def in template.user_inputs:
            widget = self._make_input_widget(input_def)
            if widget:
                self._input_widgets[input_def.id] = widget
                self._layout.addWidget(widget)
                self._layout.addSpacing(20)

        self._layout.addStretch(1)

    def get_user_inputs(self) -> dict:
        return {k: w.get_value() for k, w in self._input_widgets.items()}

    def validate(self) -> tuple[bool, str]:
        """Validates selector widgets only (description is validated by DescriptionPanel)."""
        artist_w = self._input_widgets.get("artists")
        if artist_w and not artist_w.get_value():
            return False, "請至少選擇一位繪師"
        return True, ""

    def set_loading(self, loading: bool) -> None:
        self._loading = loading
        self._gen_btn.setEnabled(not loading)
        if loading:
            self._loading_tick = 0
            self._loading_timer.start()
            self._start_pulse()
        else:
            self._loading_timer.stop()
            self._stop_pulse()
            self._gen_btn.setText("✦  生成提示詞")

    # ── Pulse animation ──────────────────────────────────────────────────────

    def _start_pulse(self) -> None:
        effect = QGraphicsOpacityEffect(self._gen_btn)
        self._gen_btn.setGraphicsEffect(effect)
        self._pulse_anim = QPropertyAnimation(effect, b"opacity", self)
        self._pulse_anim.setDuration(900)
        self._pulse_anim.setKeyValueAt(0.0, 1.0)
        self._pulse_anim.setKeyValueAt(0.5, 0.45)
        self._pulse_anim.setKeyValueAt(1.0, 1.0)
        self._pulse_anim.setLoopCount(-1)
        self._pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._pulse_anim.start()

    def _stop_pulse(self) -> None:
        if self._pulse_anim:
            self._pulse_anim.stop()
            self._pulse_anim = None
        if self._gen_btn.graphicsEffect():
            self._gen_btn.setGraphicsEffect(None)

    # ── Private builders ─────────────────────────────────────────────────────

    def _make_input_widget(self, input_def) -> QWidget | None:
        match input_def.type:
            case "multi_select_cards":
                return MultiSelectCards(input_def)
            case "single_select_pills":
                return SingleSelectPills(input_def)
            case "category_select":
                return CategorySelect(input_def)
            case _:
                return None

    # ── Event handlers ───────────────────────────────────────────────────────

    def _on_generate_clicked(self) -> None:
        self.generate_clicked.emit()

    def _tick_loading(self) -> None:
        if self._loading:
            self._gen_btn.setText(_LOADING_FRAMES[self._loading_tick % len(_LOADING_FRAMES)])
            self._loading_tick += 1
