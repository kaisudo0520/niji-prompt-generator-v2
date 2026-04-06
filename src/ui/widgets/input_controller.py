"""
InputController — Creates and manages template-driven input widgets.
Not a QWidget; purely a controller that builds and tracks widget instances.
MainWindow owns the layout and decides widget placement.
"""
from typing import Any

from PySide6.QtWidgets import QWidget

from src.ui.widgets.inputs.multi_select_cards import MultiSelectCards
from src.ui.widgets.inputs.compact_selects import (
    CompactSingleSelect,
    CompactCategorySelect,
    CompactTextInput,
)


class InputController:
    def __init__(self) -> None:
        self._widgets: dict[str, QWidget] = {}

    def render_template(self, template) -> None:
        """Destroy old widgets and create new ones from template definition."""
        for w in self._widgets.values():
            w.setParent(None)
            w.deleteLater()
        self._widgets.clear()

        for input_def in template.user_inputs:
            widget = self._make_widget(input_def)
            if widget:
                self._widgets[input_def.id] = widget

    def get_widget(self, input_id: str) -> QWidget | None:
        return self._widgets.get(input_id)

    def get_user_inputs(self) -> dict[str, Any]:
        return {k: w.get_value() for k, w in self._widgets.items()}

    def validate(self) -> tuple[bool, str]:
        artist_w = self._widgets.get("artists")
        if artist_w and not artist_w.get_value():
            return False, "請至少選擇一位繪師"
        return True, ""

    def set_loading(self, loading: bool) -> None:
        for w in self._widgets.values():
            w.setEnabled(not loading)

    def _make_widget(self, input_def) -> QWidget | None:
        match input_def.type:
            case "multi_select_cards":
                return MultiSelectCards(input_def)
            case "single_select_pills":
                return CompactSingleSelect(input_def)
            case "category_select":
                return CompactCategorySelect(input_def)
            case "text_input":
                return CompactTextInput(input_def)
            case _:
                return None
