"""TDD tests for PromptService."""
import json
from unittest.mock import MagicMock, patch

import pytest

from src.models.api import GenerateRequest
from src.services.prompt_service import PromptService, LLMParseError, FieldMissingError
from src.services.template_service import TemplateNotFoundError


def _make_service(niji_template, llm_response: str):
    """Helper: build a PromptService with mocked dependencies."""
    template_svc = MagicMock()
    template_svc.load.return_value = niji_template
    llm_svc = MagicMock()
    llm_svc.complete.return_value = llm_response
    return PromptService(template_svc, llm_svc)


# ── Normal flow ───────────────────────────────────────────────────────────────

def test_generate_returns_complete_prompt(niji_template, mock_llm_response, basic_request):
    svc = _make_service(niji_template, mock_llm_response)
    resp = svc.generate(basic_request)
    assert resp.prompt
    assert resp.template_id == "niji-anime"


def test_prompt_contains_niji_suffix(niji_template, mock_llm_response, basic_request):
    svc = _make_service(niji_template, mock_llm_response)
    resp = svc.generate(basic_request)
    assert "--niji 7 --s 750" in resp.prompt


def test_prompt_contains_aspect_ratio(niji_template, mock_llm_response, basic_request):
    svc = _make_service(niji_template, mock_llm_response)
    resp = svc.generate(basic_request)
    assert "--ar 9:16" in resp.prompt


def test_single_artist_style_ref(niji_template, mock_llm_response, basic_request):
    svc = _make_service(niji_template, mock_llm_response)
    resp = svc.generate(basic_request)
    assert "in the style of RURUDO" in resp.prompt
    assert " and " not in resp.prompt.split("in the style of")[1].split(",")[0]


def test_two_artist_style_ref(niji_template, mock_llm_response, two_artist_request):
    svc = _make_service(niji_template, mock_llm_response)
    resp = svc.generate(two_artist_request)
    assert "in the style of Lake and Liduke" in resp.prompt


def test_user_selected_palette_included_in_user_message(
    niji_template, mock_llm_response, two_artist_request
):
    template_svc = MagicMock()
    template_svc.load.return_value = niji_template
    llm_svc = MagicMock()
    llm_svc.complete.return_value = mock_llm_response

    svc = PromptService(template_svc, llm_svc)
    svc.generate(two_artist_request)

    call_args = llm_svc.complete.call_args
    user_message = call_args[0][1]
    assert "dark bronze and red" in user_message


def test_empty_palette_tells_llm_to_choose(niji_template, mock_llm_response, basic_request):
    template_svc = MagicMock()
    template_svc.load.return_value = niji_template
    llm_svc = MagicMock()
    llm_svc.complete.return_value = mock_llm_response

    svc = PromptService(template_svc, llm_svc)
    svc.generate(basic_request)

    user_message = llm_svc.complete.call_args[0][1]
    assert "Choose an appropriate color palette" in user_message


def test_response_includes_all_fields(niji_template, mock_llm_response, basic_request):
    svc = _make_service(niji_template, mock_llm_response)
    resp = svc.generate(basic_request)
    expected_keys = {f.key for f in niji_template.fields}
    assert expected_keys == set(resp.fields.keys())


# ── Error cases ───────────────────────────────────────────────────────────────

def test_raises_when_llm_returns_invalid_json(niji_template, basic_request):
    svc = _make_service(niji_template, "not valid json at all")
    with pytest.raises(LLMParseError):
        svc.generate(basic_request)


def test_raises_when_llm_fields_incomplete(niji_template, basic_request):
    incomplete = json.dumps({"character_and_shot": "1girl"})  # missing 7 fields
    svc = _make_service(niji_template, incomplete)
    with pytest.raises(FieldMissingError):
        svc.generate(basic_request)


def test_raises_when_template_not_found(niji_template, basic_request):
    template_svc = MagicMock()
    template_svc.load.side_effect = TemplateNotFoundError("niji-anime")
    llm_svc = MagicMock()
    svc = PromptService(template_svc, llm_svc)
    with pytest.raises(TemplateNotFoundError):
        svc.generate(basic_request)


# ── Field hint injection ──────────────────────────────────────────────────────

def test_user_message_includes_field_hints(niji_template, mock_llm_response, basic_request):
    """user_message should contain hint text as inline comments for each field."""
    template_svc = MagicMock()
    template_svc.load.return_value = niji_template
    llm_svc = MagicMock()
    llm_svc.complete.return_value = mock_llm_response

    svc = PromptService(template_svc, llm_svc)
    svc.generate(basic_request)

    user_message = llm_svc.complete.call_args[0][1]
    # The 'lighting' field has hint containing "warm golden backlight"
    assert "warm golden backlight" in user_message


def test_user_message_omits_hint_comment_when_empty(mock_llm_response, basic_request):
    """When a field has no hint, its line in user_message must not contain '//'."""
    import copy
    from src.models.template import TemplateDefinition

    # Load the real template and clear one field's hint
    import json
    from pathlib import Path

    raw = json.loads(
        (Path(__file__).parent.parent.parent / "templates" / "niji-anime.json").read_text(
            encoding="utf-8"
        )
    )
    # Clear the hint for 'lighting' specifically
    for field in raw["fields"]:
        if field["key"] == "lighting":
            field["hint"] = ""
    no_hint_template = TemplateDefinition(**raw)

    template_svc = MagicMock()
    template_svc.load.return_value = no_hint_template
    llm_svc = MagicMock()
    llm_svc.complete.return_value = mock_llm_response

    svc = PromptService(template_svc, llm_svc)
    svc.generate(basic_request)

    user_message = llm_svc.complete.call_args[0][1]
    # Find the line corresponding to 'lighting' and assert no '//' comment
    lighting_line = next(
        (line for line in user_message.splitlines() if '"lighting"' in line), None
    )
    assert lighting_line is not None, "Expected a line with 'lighting' key in user_message"
    assert "//" not in lighting_line


# ── system_prompt content ─────────────────────────────────────────────────────

def test_system_prompt_contains_creative_freedom_instruction(niji_template):
    """system_prompt must include the adaptive creative-freedom instructions."""
    assert "creative freedom" in niji_template.system_prompt
    assert "faithfully translate" in niji_template.system_prompt
