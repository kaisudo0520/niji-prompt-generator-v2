"""
MainWindow — Three-row layout:

  Row 1  ┌─────────────────┬──────────────────────┐
         │  角色描述        │  繪師風格選擇          │
         └─────────────────┴──────────────────────┘
  Row 2  ┌──────────┬──────────────────────────────┐
         │  比例    │  色調選擇                      │
         └──────────┴──────────────────────────────┘
         ┌───────────────────────────────────────────┐
  CTA    │  ✦ 生成提示詞                             │
         └───────────────────────────────────────────┘
  Row 3  ┌───────────────────────────────────────────┐
         │  生成結果                                  │
         └───────────────────────────────────────────┘
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QSplitter, QMessageBox, QSizePolicy,
    QPushButton, QScrollArea, QGraphicsOpacityEffect,
)
from PySide6.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QCursor

from src.ui.widgets.template_selector import TemplateSelector
from src.ui.widgets.description_panel import DescriptionPanel
from src.ui.widgets.input_controller import InputController
from src.ui.widgets.prompt_output import PromptOutput
from src.ui.workers.generate_worker import GenerateWorker
from src.ui.styles.theme import Palette


_LOADING_FRAMES = ["✦  生成中", "✦  生成中 ·", "✦  生成中 ··", "✦  生成中 ···"]

_DEV_RESULT = {
    "prompt": (
        "1girl, full body, silver hair, starry blue eyes, "
        "celestial mage robe with silver trim, ornate star-tipped staff, "
        "silver hair cascading, glowing sapphire eyes, "
        "serene smile, casting a constellation spell, "
        "pink and gold, professional golden lighting, "
        "luminous brushwork, use of light and shadow, "
        "grand moonlit library at midnight, "
        "in the style of RURUDO, "
        "official art, anime aesthetic, "
        "elegant composition, soft bokeh "
        "--ar 9:16 --niji 7 --s 750"
    ),
    "fields": {
        "character_and_shot":     "1girl, full body, silver hair, starry blue eyes",
        "outfit_and_accessories": "celestial mage robe with silver trim, ornate star-tipped staff",
        "hair_and_eyes":          "silver hair cascading, glowing sapphire eyes",
        "expression_and_action":  "serene smile, casting a constellation spell",
        "color_palette":          "pink and gold",
        "lighting":               "professional golden lighting",
        "scene_and_atmosphere":   "grand moonlit library at midnight",
        "composition":            "elegant composition, soft bokeh",
    },
}


class MainWindow(QMainWindow):
    def __init__(
        self,
        template_service=None,
        prompt_service=None,
        llm_config=None,
        parent=None,
    ):
        super().__init__(parent)
        self._template_service = template_service
        self._prompt_service = prompt_service
        self._llm_config = llm_config
        self._worker: GenerateWorker | None = None
        self._active_template = None

        self._input_ctrl = InputController()
        self._pulse_anim: QPropertyAnimation | None = None
        self._loading_timer = QTimer(self)
        self._loading_timer.setInterval(400)
        self._loading_timer.timeout.connect(self._tick_loading)
        self._loading_tick = 0
        self._loading = False

        self._setup_window()
        self._build_ui()

        if self._template_service:
            self._load_templates()

    # ── Window setup ─────────────────────────────────────────────────────────

    def _setup_window(self) -> None:
        self.setWindowTitle("Niji Prompt Generator")
        self.setMinimumSize(QSize(880, 620))
        self.resize(QSize(1260, 760))

    # ── UI construction ──────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        root.addWidget(self._build_template_selector())
        root.addWidget(self._build_thin_divider())
        root.addWidget(self._build_main_content(), 1)

    def _build_header(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("headerBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(10)

        gem = QLabel("✦")
        gem.setStyleSheet(f"color: {Palette.ACCENT}; font-size: 16px; background: transparent;")
        layout.addWidget(gem)

        title = QLabel("Niji Prompt Generator")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        layout.addStretch()

        model_name = "—"
        if self._llm_config:
            model_name = self._llm_config.active_model.split("/")[-1]
        self._model_lbl = QLabel(f"⬡  {model_name}")
        self._model_lbl.setObjectName("statusModel")
        layout.addWidget(self._model_lbl)

        return bar

    def _build_template_selector(self) -> TemplateSelector:
        self._template_selector = TemplateSelector()
        self._template_selector.template_changed.connect(self._on_template_changed)
        return self._template_selector

    def _build_thin_divider(self) -> QFrame:
        d = QFrame()
        d.setObjectName("divider")
        return d

    def _build_main_content(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Vertical splitter: Row1 (form) + Row2 (output) ──────────────────
        self._vsplit = QSplitter(Qt.Orientation.Vertical)
        self._vsplit.setHandleWidth(1)

        # Row 1: Description | Artists
        row1 = QSplitter(Qt.Orientation.Horizontal)
        row1.setHandleWidth(1)
        self._description_panel = DescriptionPanel()
        row1.addWidget(self._description_panel)
        self._artists_scroll, self._artists_inner = self._make_scroll_section()
        row1.addWidget(self._artists_scroll)
        row1.setSizes([560, 700])
        self._vsplit.addWidget(row1)

        # Row 2: Output
        self._prompt_output = PromptOutput()
        self._vsplit.addWidget(self._prompt_output)

        self._vsplit.setSizes([360, 340])
        layout.addWidget(self._vsplit, 1)

        # ── Action bar: dropdowns + generate button ──────────────────────────
        layout.addWidget(self._build_thin_divider())
        layout.addWidget(self._build_action_bar())

        return container

    def _make_scroll_section(self) -> tuple[QScrollArea, QWidget]:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        inner = QWidget()
        inner.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(20, 20, 20, 20)
        inner_layout.setSpacing(0)
        inner_layout.addStretch(1)

        scroll.setWidget(inner)
        return scroll, inner

    def _build_action_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("generateFooter")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(24, 12, 24, 14)
        bar_layout.setSpacing(20)

        # Dropdown slots (populated in _rebuild_input_layout)
        self._ratio_slot = QWidget()
        self._ratio_slot_layout = QHBoxLayout(self._ratio_slot)
        self._ratio_slot_layout.setContentsMargins(0, 0, 0, 0)
        bar_layout.addWidget(self._ratio_slot)

        self._color_slot = QWidget()
        self._color_slot_layout = QHBoxLayout(self._color_slot)
        self._color_slot_layout.setContentsMargins(0, 0, 0, 0)
        bar_layout.addWidget(self._color_slot)

        bar_layout.addStretch(1)

        self._gen_btn = QPushButton("✦  生成提示詞")
        self._gen_btn.setObjectName("generateBtn")
        self._gen_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._gen_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._gen_btn.clicked.connect(self._on_generate_clicked)
        bar_layout.addWidget(self._gen_btn)

        return bar

    # ── Section widget placement ─────────────────────────────────────────────

    def _place_widget(self, inner: QWidget, widget: QWidget | None) -> None:
        """Clear inner widget's layout and insert new widget (before the stretch)."""
        layout = inner.layout()
        # Remove all non-stretch items
        while layout.count() > 1:
            item = layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        if widget:
            layout.insertWidget(0, widget)

    def _place_in_slot(self, slot_layout: QHBoxLayout, widget) -> None:
        while slot_layout.count():
            item = slot_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        if widget:
            slot_layout.addWidget(widget)

    def _rebuild_input_layout(self) -> None:
        self._place_widget(self._artists_inner, self._input_ctrl.get_widget("artists"))
        self._place_in_slot(self._ratio_slot_layout, self._input_ctrl.get_widget("aspect_ratio"))
        self._place_in_slot(self._color_slot_layout, self._input_ctrl.get_widget("color_palette"))

    # ── Template loading ─────────────────────────────────────────────────────

    def _load_templates(self) -> None:
        templates = self._template_service.get_all()
        self._template_selector.set_templates(templates)
        if templates:
            self._active_template = templates[0]
            self._input_ctrl.render_template(templates[0])
            self._rebuild_input_layout()

    def _on_template_changed(self, template_id: str) -> None:
        if not self._template_service:
            return
        tmpl = self._template_service.load(template_id)
        self._active_template = tmpl
        self._input_ctrl.render_template(tmpl)
        self._rebuild_input_layout()
        self._prompt_output.clear()

    # ── Generation ───────────────────────────────────────────────────────────

    def _on_generate_clicked(self) -> None:
        desc_ok, desc_msg = self._description_panel.validate()
        if not desc_ok:
            self._description_panel.focus_input()
            QMessageBox.warning(self, "請填寫必要欄位", desc_msg)
            return

        form_ok, form_msg = self._input_ctrl.validate()
        if not form_ok:
            QMessageBox.warning(self, "請填寫必要欄位", form_msg)
            return

        description = self._description_panel.get_description()
        user_inputs = self._input_ctrl.get_user_inputs()

        # Dev mode
        if not self._prompt_service:
            self._prompt_output.display_result(
                prompt=_DEV_RESULT["prompt"],
                fields=_DEV_RESULT["fields"],
            )
            return

        # Production
        try:
            from src.models.api import GenerateRequest
            request = GenerateRequest(
                template_id=self._active_template.id,
                user_description=description,
                user_inputs=user_inputs,
            )
        except Exception as exc:
            QMessageBox.critical(self, "請求錯誤", str(exc))
            return

        self._set_loading(True)

        self._worker = GenerateWorker(self._prompt_service, request, parent=self)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_finished(self, response) -> None:
        self._set_loading(False)
        self._prompt_output.display_result(
            prompt=response.prompt,
            fields=response.fields,
        )

    def _on_error(self, message: str) -> None:
        self._set_loading(False)
        self._prompt_output.display_error(message)
        QMessageBox.critical(self, "生成失敗", message)

    # ── Loading state ────────────────────────────────────────────────────────

    def _set_loading(self, loading: bool) -> None:
        self._loading = loading
        self._gen_btn.setEnabled(not loading)
        self._description_panel.set_loading(loading)
        self._input_ctrl.set_loading(loading)
        self._prompt_output.set_loading(loading)

        if loading:
            self._loading_tick = 0
            self._loading_timer.start()
            self._start_pulse()
        else:
            self._loading_timer.stop()
            self._stop_pulse()
            self._gen_btn.setText("✦  生成提示詞")

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

    def _tick_loading(self) -> None:
        if self._loading:
            self._gen_btn.setText(_LOADING_FRAMES[self._loading_tick % len(_LOADING_FRAMES)])
            self._loading_tick += 1
