"""TDD tests for TemplateService."""
import json
from pathlib import Path

import pytest

from src.services.template_service import TemplateService, TemplateNotFoundError


def test_load_all_returns_niji_template(tmp_path):
    # Copy real template into a temp dir
    real = Path("templates/niji-anime.json")
    (tmp_path / "niji-anime.json").write_text(real.read_text(encoding="utf-8"), encoding="utf-8")
    svc = TemplateService(tmp_path)
    templates = svc.get_all()
    assert len(templates) == 1
    assert templates[0].id == "niji-anime"


def test_load_by_id_returns_correct_template(tmp_path):
    real = Path("templates/niji-anime.json")
    (tmp_path / "niji-anime.json").write_text(real.read_text(encoding="utf-8"), encoding="utf-8")
    svc = TemplateService(tmp_path)
    tmpl = svc.load("niji-anime")
    assert tmpl.name == "Niji Anime"


def test_load_raises_when_id_not_found(tmp_path):
    svc = TemplateService(tmp_path)  # empty dir
    with pytest.raises(TemplateNotFoundError):
        svc.load("nonexistent")


def test_load_skips_invalid_json_with_warning(tmp_path, caplog):
    (tmp_path / "bad.json").write_text("{invalid json", encoding="utf-8")
    import logging
    with caplog.at_level(logging.WARNING):
        svc = TemplateService(tmp_path)
    assert len(svc.get_all()) == 0
    assert "bad.json" in caplog.text


def test_empty_templates_dir_returns_empty_list(tmp_path):
    svc = TemplateService(tmp_path)
    assert svc.get_all() == []


def test_missing_dir_returns_empty_list():
    svc = TemplateService(Path("nonexistent_dir_xyz"))
    assert svc.get_all() == []
