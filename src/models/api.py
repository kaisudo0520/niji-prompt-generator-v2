"""Request / Response models for the generate pipeline."""
from pydantic import BaseModel


class GenerateRequest(BaseModel):
    template_id: str
    user_description: str
    user_inputs: dict[str, object]  # key = UserInputDef.id


class GenerateResponse(BaseModel):
    prompt: str              # Final Midjourney string
    fields: dict[str, str]   # LLM-filled field values
    template_id: str
