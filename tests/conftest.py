"""Shared pytest fixtures."""
import json
from pathlib import Path

import pytest

from src.models.template import TemplateDefinition
from src.models.llm_config import LLMConfig
from src.models.api import GenerateRequest

FIXTURES = Path(__file__).parent / "fixtures"
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


@pytest.fixture
def niji_template() -> TemplateDefinition:
    data = json.loads((TEMPLATES_DIR / "niji-anime.json").read_text(encoding="utf-8"))
    return TemplateDefinition(**data)


@pytest.fixture
def llm_config() -> LLMConfig:
    return LLMConfig(
        active_model="google/gemini-3-flash-preview",
        available_models=[],
    )


@pytest.fixture
def mock_llm_response() -> str:
    return (FIXTURES / "mock_llm_response.json").read_text(encoding="utf-8")


@pytest.fixture
def basic_request() -> GenerateRequest:
    return GenerateRequest(
        template_id="niji-anime",
        user_description="銀髮魔法少女",
        user_inputs={
            "artists": ["RURUDO"],
            "aspect_ratio": "9:16",
            "color_palette": "",
        },
    )


@pytest.fixture
def two_artist_request() -> GenerateRequest:
    return GenerateRequest(
        template_id="niji-anime",
        user_description="神秘的暗黑魔女",
        user_inputs={
            "artists": ["Lake", "Liduke"],
            "aspect_ratio": "1:1",
            "color_palette": "dark bronze and red",
        },
    )
