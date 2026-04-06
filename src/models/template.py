"""
Template data models — the SDD specification for all template-related data.
These Pydantic models serve as both type definitions and JSON schema validators.
"""
from __future__ import annotations

from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field


class SelectOption(BaseModel):
    value: str
    label: str
    description: str = ""


class CategoryGroup(BaseModel):
    label: str
    options: list[SelectOption]


# ── UserInput discriminated union ────────────────────────────────────────────

class MultiSelectCardsInput(BaseModel):
    type: Literal["multi_select_cards"]
    id: str
    label: str
    options: list[SelectOption]
    max_selections: int = Field(ge=1, default=2)


class SingleSelectPillsInput(BaseModel):
    type: Literal["single_select_pills"]
    id: str
    label: str
    options: list[SelectOption]
    default: str = ""


class CategorySelectInput(BaseModel):
    type: Literal["category_select"]
    id: str
    label: str
    categories: list[CategoryGroup]
    allow_empty: bool = False
    empty_label: str = "讓 LLM 決定"


class TextInput(BaseModel):
    type: Literal["text_input"]
    id: str
    label: str
    placeholder: str = ""
    required: bool = False


UserInputDef = Annotated[
    Union[
        MultiSelectCardsInput,
        SingleSelectPillsInput,
        CategorySelectInput,
        TextInput,
    ],
    Field(discriminator="type"),
]


# ── Field definition ─────────────────────────────────────────────────────────

class FieldDef(BaseModel):
    key: str
    label: str
    hint: str = ""


# ── Top-level template ───────────────────────────────────────────────────────

class TemplateDefinition(BaseModel):
    id: str
    name: str
    description: str
    icon: str = ""
    user_inputs: list[UserInputDef]
    fields: list[FieldDef]
    system_prompt: str
    # {field_key} placeholders for LLM fields; {artist_ref} and {aspect_ratio}
    # are special-cased in PromptService.
    output_template: str
    fixed_suffix: str = ""
