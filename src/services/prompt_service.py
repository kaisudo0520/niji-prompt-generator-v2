"""
PromptService — Orchestrates template → LLM → assembled prompt.
This is the core business logic layer; it has no UI or HTTP dependencies.
"""
import json
import logging

from src.models.api import GenerateRequest, GenerateResponse
from src.models.template import TemplateDefinition
from src.services.llm_service import LLMService, LLMError
from src.services.template_service import TemplateService

logger = logging.getLogger(__name__)


class LLMParseError(ValueError):
    pass


class FieldMissingError(ValueError):
    pass


class PromptService:
    def __init__(
        self,
        template_service: TemplateService,
        llm_service: LLMService,
    ) -> None:
        self._templates = template_service
        self._llm = llm_service

    # ── Public API ───────────────────────────────────────────────────────────

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        template = self._templates.load(request.template_id)

        user_message = self._build_user_message(template, request)
        raw = self._llm.complete(template.system_prompt, user_message)
        fields = self._parse_fields(raw, template)
        prompt = self._assemble_prompt(template, fields, request.user_inputs)

        return GenerateResponse(
            prompt=prompt,
            fields=fields,
            template_id=request.template_id,
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    def _build_user_message(
        self, template: TemplateDefinition, request: GenerateRequest
    ) -> str:
        palette = request.user_inputs.get("color_palette", "")
        palette_line = (
            f'Color palette (user-selected): "{palette}"'
            if palette
            else "Choose an appropriate color palette."
        )

        title_ref = request.user_inputs.get("title_reference", "")
        title_line = (
            f'Title/song/album reference (use as creative direction): "{title_ref}"'
            if title_ref
            else ""
        )

        lines = [
            f'  "{f.key}": ""  // {f.hint}'
            if f.hint
            else f'  "{f.key}": ""'
            for f in template.fields
        ]
        field_keys = ",\n".join(lines)

        header_lines = [f'User description: "{request.user_description}"']
        if title_line:
            header_lines.append(title_line)
        header_lines.append(palette_line)

        header = "\n".join(header_lines)

        return (
            f"{header}\n\n"
            "Fill in the following fields in concise English "
            "(1-3 short phrases each, Midjourney syntax — less is more):\n"
            f"{{\n{field_keys}\n}}"
        )

    def _parse_fields(
        self, raw: str, template: TemplateDefinition
    ) -> dict[str, str]:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LLMParseError(f"LLM returned invalid JSON: {exc}\n\nRaw: {raw[:300]}")

        missing = [f.key for f in template.fields if f.key not in data]
        if missing:
            raise FieldMissingError(
                f"LLM response missing fields: {missing}\n\nReceived: {list(data.keys())}"
            )

        # Sanitize values: escape curly braces to prevent str.format() injection
        return {
            f.key: str(data[f.key]).replace("{", "{{").replace("}", "}}")
            for f in template.fields
        }

    def _assemble_prompt(
        self,
        template: TemplateDefinition,
        fields: dict[str, str],
        user_inputs: dict,
    ) -> str:
        artists: list[str] = user_inputs.get("artists", [])
        if not artists:
            artist_ref = "in the style of an anime artist"
        elif len(artists) == 1:
            artist_ref = f"in the style of {artists[0]}"
        else:
            artist_ref = f"in the style of {artists[0]} and {artists[1]}"

        aspect_ratio: str = user_inputs.get("aspect_ratio", "9:16")

        # Fill LLM fields into output_template
        prompt = template.output_template.format(
            artist_ref=artist_ref,
            **fields,
        )

        # Append fixed suffix with user-input substitutions
        suffix = template.fixed_suffix.format(
            aspect_ratio=aspect_ratio,
        )

        return f"{prompt} {suffix}".strip()
