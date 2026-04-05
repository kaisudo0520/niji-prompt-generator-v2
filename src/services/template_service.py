"""
TemplateService — Loads and caches TemplateDefinition objects from JSON files.
Invalid JSON files are skipped with a warning, not a crash.
"""
import json
import logging
from pathlib import Path

from src.models.template import TemplateDefinition

logger = logging.getLogger(__name__)


class TemplateNotFoundError(ValueError):
    pass


class TemplateService:
    def __init__(self, templates_dir: Path) -> None:
        self._dir = templates_dir
        self._cache: dict[str, TemplateDefinition] = {}
        self._load_all()

    # ── Public API ───────────────────────────────────────��───────────────────

    def get_all(self) -> list[TemplateDefinition]:
        return list(self._cache.values())

    def load(self, template_id: str) -> TemplateDefinition:
        try:
            return self._cache[template_id]
        except KeyError:
            raise TemplateNotFoundError(f"Template not found: {template_id!r}")

    def get_registered_ids(self) -> list[str]:
        return list(self._cache.keys())

    # ── Private ────────────────────────────��────────────────────────────���────

    def _load_all(self) -> None:
        if not self._dir.exists():
            logger.warning("Templates directory not found: %s", self._dir)
            return

        for path in sorted(self._dir.glob("*.json")):
            self._load_file(path)

        logger.info("Loaded %d template(s): %s", len(self._cache), list(self._cache))

    def _load_file(self, path: Path) -> None:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            tmpl = TemplateDefinition(**data)
            self._cache[tmpl.id] = tmpl
        except Exception as exc:
            logger.warning("Skipping invalid template %s: %s", path.name, exc)
