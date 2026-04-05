"""LLM routing configuration model."""
from pydantic import BaseModel


class ModelOption(BaseModel):
    id: str    # OpenRouter model ID, e.g. "google/gemini-2.5-flash-preview"
    name: str  # Human-readable display name


class LLMConfig(BaseModel):
    provider: str = "openrouter"
    base_url: str = "https://openrouter.ai/api/v1"
    active_model: str
    available_models: list[ModelOption] = []
    temperature: float = 0.7
    max_tokens: int = 1024
