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


@pytest.fixture
def service(config: LLMConfig) -> LLMService:
    return LLMService(config=config, api_key="test-api-key-xyz")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def _patch_httpx_client(mock_response: MagicMock):
    """Context manager: patch httpx.Client and wire it to return mock_response."""
    mock_client = MagicMock()
    mock_client.post.return_value = mock_response

    patcher = patch("httpx.Client")
    mock_cls = patcher.start()
    mock_cls.return_value.__enter__.return_value = mock_client
    mock_cls.return_value.__exit__.return_value = False
    return patcher, mock_client


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_complete_sends_correct_authorization_header(service: LLMService) -> None:
    resp = _mock_http_response(
        json_body={"choices": [{"message": {"content": "ok"}}]}
    )
    patcher, mock_client = _patch_httpx_client(resp)
    try:
        service.complete("sys", "usr")
        _, kwargs = mock_client.post.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer test-api-key-xyz"
    finally:
        patcher.stop()


def test_complete_returns_content_from_response(service: LLMService) -> None:
    expected = "1girl, silver hair, --niji 7 --s 750"
    resp = _mock_http_response(
        json_body={"choices": [{"message": {"content": expected}}]}
    )
    patcher, _ = _patch_httpx_client(resp)
    try:
        result = service.complete("sys", "usr")
        assert result == expected
    finally:
        patcher.stop()


def test_complete_raises_on_401(service: LLMService) -> None:
    resp = _mock_http_response(status_code=401, text="Unauthorized")
    patcher, _ = _patch_httpx_client(resp)
    try:
        with pytest.raises(LLMError) as exc_info:
            service.complete("sys", "usr")
        assert exc_info.value.status_code == 401
        assert "Invalid API key" in str(exc_info.value)
    finally:
        patcher.stop()


def test_complete_raises_on_429_with_friendly_message(service: LLMService) -> None:
    resp = _mock_http_response(status_code=429, text="Too Many Requests")
    patcher, _ = _patch_httpx_client(resp)
    try:
        with pytest.raises(LLMError) as exc_info:
            service.complete("sys", "usr")
        assert exc_info.value.status_code == 429
        assert "Rate limit" in str(exc_info.value)
    finally:
        patcher.stop()


def test_complete_raises_on_timeout(service: LLMService) -> None:
    patcher = patch("httpx.Client")
    mock_cls = patcher.start()
    mock_client = MagicMock()
    mock_cls.return_value.__enter__.return_value = mock_client
    mock_cls.return_value.__exit__.return_value = False
    mock_client.post.side_effect = httpx.TimeoutException("connection timed out")
    try:
        with pytest.raises(LLMError) as exc_info:
            service.complete("sys", "usr")
        assert "timed out" in str(exc_info.value).lower()
    finally:
        patcher.stop()
