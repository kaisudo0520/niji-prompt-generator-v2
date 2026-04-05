"""
End-to-end integration test — requires OPENROUTER_API_KEY in .env.
Skipped automatically when the key is absent.
"""
import os

import pytest
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY", "")

pytestmark = pytest.mark.skipif(
    not API_KEY,
    reason="OPENROUTER_API_KEY not set — skipping live API test",
)


@pytest.fixture(scope="module")
def prompt_service():
    from pathlib import Path

    from src.config.llm_config_loader import load_llm_config
    from src.services.llm_service import LLMService
    from src.services.prompt_service import PromptService
    from src.services.template_service import TemplateService

    root = Path(__file__).parent.parent.parent
    config = load_llm_config(root / "config" / "llm_config.json")
    return PromptService(
        template_service=TemplateService(root / "templates"),
        llm_service=LLMService(config=config, api_key=API_KEY),
    )


def test_e2e_prompt_ends_with_niji_suffix(prompt_service) -> None:
    """Real call to google/gemini-3-flash-preview via OpenRouter."""
    from src.models.api import GenerateRequest

    request = GenerateRequest(
        template_id="niji-anime",
        user_description="銀髮魔法少女",
        user_inputs={
            "artists": ["RURUDO"],
            "aspect_ratio": "9:16",
            "color_palette": "pink and gold",
        },
    )

    response = prompt_service.generate(request)

    assert response.prompt, "Prompt should not be empty"
    assert "--niji 7 --s 750" in response.prompt, (
        f"Expected '--niji 7 --s 750' in prompt, got:\n{response.prompt}"
    )
    assert "--ar 9:16" in response.prompt, (
        f"Expected '--ar 9:16' in prompt, got:\n{response.prompt}"
    )
    assert len(response.fields) > 0, "Fields should be populated"

    print(f"\n[E2E] Generated prompt:\n{response.prompt}")
