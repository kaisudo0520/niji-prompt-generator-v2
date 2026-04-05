"""Request / Response models for the generate pipeline."""
from typing import Union

from pydantic import BaseModel


class GenerateRequest(BaseModel):
    template_id: str
    user_description: str
    # key = UserInputDef.id; values: list[str] (artists), str (aspect_ratio, color_palette)
    user_inputs: dict[str, Union[str, list[str]]]


class GenerateResponse(BaseModel):
    prompt: str              # Final Midjourney string
    fields: dict[str, str]   # LLM-filled field values
    template_id: str
