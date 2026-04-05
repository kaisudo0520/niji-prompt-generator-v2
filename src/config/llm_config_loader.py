"""Loads LLMConfig from a JSON file."""
import json
from pathlib import Path

from src.models.llm_config import LLMConfig


def load_llm_config(path: Path) -> LLMConfig:
    if not path.exists():
        raise FileNotFoundError(f"LLM config not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return LLMConfig(**data)
