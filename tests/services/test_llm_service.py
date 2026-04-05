"""Tests for LLMService — httpx mocked via unittest.mock.patch."""
from unittest.mock import MagicMock, patch

import httpx
import pytest

from src.models.llm_config import LLMConfig
from src.services.llm_service import LLMError, LLMService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def config() -> LLMConfig:
    return LLMConfig(
        active_model="google/gemini-3-flash-preview",
        available_models=[],
    )


def _mock_http_response(
    status_code: int = 200,
    json_body: dict | None = None,
    text: str = "",
) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.is_success = 200 <= status_code < 300
    resp.text = text
    if json_body is not None:
        resp.json.return_value = json_body
    return resp


def _make_service_with_mock(config: LLMConfig, mock_response=None, side_effect=None):
    """Build an LLMService with a mocked httpx.Client.

    Returns (service, mock_client) so callers can inspect calls.
    """
    mock_client = MagicMock(spec=httpx.Client)
    if mock_response is not None:
        mock_client.post.return_value = mock_response
    if side_effect is not None:
        mock_client.post.side_effect = side_effect

    with patch("src.services.llm_service.httpx.Client", return_value=mock_client):
        service = LLMService(config=config, api_key="test-api-key-xyz")

    return service, mock_client


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_complete_sends_correct_payload(config: LLMConfig) -> None:
    resp = _mock_http_response(
        json_body={"choices": [{"message": {"content": "ok"}}]}
    )
    service, mock_client = _make_service_with_mock(config, mock_response=resp)
    service.complete("sys", "usr")
    _, kwargs = mock_client.post.call_args
    assert kwargs["json"]["model"] == "google/gemini-3-flash-preview"


def test_complete_returns_content_from_response(config: LLMConfig) -> None:
    expected = "1girl, silver hair, --niji 7 --s 750"
    resp = _mock_http_response(
        json_body={"choices": [{"message": {"content": expected}}]}
    )
    service, _ = _make_service_with_mock(config, mock_response=resp)
    result = service.complete("sys", "usr")
    assert result == expected


def test_complete_raises_on_401(config: LLMConfig) -> None:
    resp = _mock_http_response(status_code=401, text="Unauthorized")
    service, _ = _make_service_with_mock(config, mock_response=resp)
    with pytest.raises(LLMError) as exc_info:
        service.complete("sys", "usr")
    assert exc_info.value.status_code == 401
    assert "Invalid API key" in str(exc_info.value)


def test_complete_raises_on_429_with_friendly_message(config: LLMConfig) -> None:
    resp = _mock_http_response(status_code=429, text="Too Many Requests")
    service, _ = _make_service_with_mock(config, mock_response=resp)
    with pytest.raises(LLMError) as exc_info:
        service.complete("sys", "usr")
    assert exc_info.value.status_code == 429
    assert "Rate limit" in str(exc_info.value)


def test_complete_raises_on_timeout(config: LLMConfig) -> None:
    service, _ = _make_service_with_mock(
        config,
        side_effect=httpx.TimeoutException("connection timed out"),
    )
    with pytest.raises(LLMError) as exc_info:
        service.complete("sys", "usr")
    assert "timed out" in str(exc_info.value).lower()


def test_complete_raises_on_empty_content(config: LLMConfig) -> None:
    resp = _mock_http_response(
        json_body={"choices": [{"message": {"content": ""}}]}
    )
    service, _ = _make_service_with_mock(config, mock_response=resp)
    with pytest.raises(LLMError) as exc_info:
        service.complete("sys", "usr")
    assert "empty" in str(exc_info.value).lower()


def test_complete_raises_on_network_error(config: LLMConfig) -> None:
    service, _ = _make_service_with_mock(
        config,
        side_effect=httpx.RequestError("DNS failure"),
    )
    with pytest.raises(LLMError) as exc_info:
        service.complete("sys", "usr")
    assert "Network error" in str(exc_info.value)


def test_constructor_rejects_empty_api_key(config: LLMConfig) -> None:
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        LLMService(config=config, api_key="")


def test_headers_contain_authorization(config: LLMConfig) -> None:
    resp = _mock_http_response(
        json_body={"choices": [{"message": {"content": "ok"}}]}
    )
    service, _ = _make_service_with_mock(config, mock_response=resp)
    assert "Bearer test-api-key-xyz" in str(service._headers["Authorization"])
