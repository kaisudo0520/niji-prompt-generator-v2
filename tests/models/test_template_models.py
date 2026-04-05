"""Tests for Pydantic template models and JSON deserialization."""
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.models.template import (
    TemplateDefinition,
    MultiSelectCardsInput,
    SingleSelectPillsInput,
    CategorySelectInput,
)

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"


def test_niji_template_loads_from_json(niji_template):
    assert niji_template.id == "niji-anime"
    assert niji_template.name == "Niji Anime"
    assert len(niji_template.user_inputs) == 3
    assert len(niji_template.fields) == 8


def test_user_inputs_discriminator_resolves_correctly(niji_template):
    inputs = niji_template.user_inputs
    assert isinstance(inputs[0], MultiSelectCardsInput)
    assert isinstance(inputs[1], SingleSelectPillsInput)
    assert isinstance(inputs[2], CategorySelectInput)


def test_multi_select_cards_has_correct_artists(niji_template):
    artists_input = niji_template.user_inputs[0]
    values = [o.value for o in artists_input.options]
    assert "RURUDO" in values
    assert "Lake" in values
    assert artists_input.max_selections == 2


def test_aspect_ratio_default_is_9_16(niji_template):
    ratio_input = niji_template.user_inputs[1]
    assert ratio_input.default == "9:16"


def test_color_palette_allows_empty(niji_template):
    palette_input = niji_template.user_inputs[2]
    assert palette_input.allow_empty is True


def test_template_requires_id():
    with pytest.raises(ValidationError):
        TemplateDefinition(
            name="Test",
            description="Missing id",
            user_inputs=[],
            fields=[],
            system_prompt="",
            output_template="",
        )


def test_all_json_templates_are_valid():
    """Ensures every .json in templates/ passes Pydantic validation."""
    for path in TEMPLATES_DIR.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        tmpl = TemplateDefinition(**data)
        assert tmpl.id, f"{path.name} has empty id"
