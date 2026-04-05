"""
LLMService — Single-responsibility HTTP client for OpenRouter /chat/completions.
Returns raw text; the caller is responsible for JSON parsing and field validation.
"""
import logging
from typing import Any

import httpx

from src.models.llm_config import LLMConfig

logger = logging.getLogger(__name__)


class LLMError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class LLMService:
    def __init__(self, config: LLMConfig, api_key: str) -> None:
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is required")
        self._config = config
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/niji-prompt-generator",
            "X-Title": "Niji Prompt Generator",
        }

    def complete(self, system_prompt: str, user_message: str) -> str:
        """
        Call the active model and return the assistant's text content.
        Raises LLMError on HTTP errors or empty responses.
        """
        payload: dict[str, Any] = {
            "model": self._config.active_model,
            "messages": [
                {"role": "system",  "content": system_prompt},
                {"role": "user",    "content": user_message},
            ],
            "temperature": self._config.temperature,
            "max_tokens":  self._config.max_tokens,
            "response_format": {"type": "json_object"},
        }

        logger.debug("LLM request model=%s", self._config.active_model)

        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(
                    f"{self._config.base_url}/chat/completions",
                    headers=self._headers,
                    json=payload,
                )
        except httpx.TimeoutException:
            raise LLMError("Request timed out (60 s). Please try again.")
        except httpx.RequestError as exc:
            raise LLMError(f"Network error: {exc}")

        if resp.status_code == 429:
            raise LLMError("Rate limit reached. Please wait and try again.", 429)
        if resp.status_code == 401:
            raise LLMError("Invalid API key. Check your OPENROUTER_API_KEY.", 401)
        if not resp.is_success:
            raise LLMError(
                f"API error {resp.status_code}: {resp.text[:200]}", resp.status_code
            )

        try:
            content = resp.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise LLMError(f"Unexpected API response structure: {exc}")

        if not content:
            raise LLMError("LLM returned empty content.")

        logger.debug("LLM response length=%d", len(content))
        return content
