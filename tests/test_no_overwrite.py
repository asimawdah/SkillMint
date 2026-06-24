from __future__ import annotations

from skillmint.generators import generate_all
from skillmint.installer import install_skills
from skillmint.models import Detection
from skillmint.registry import REGISTRY


def _detection(stack_id: str) -> Detection:
    return Detection(REGISTRY[stack_id], confidence=100, reasons=["test"])


def test_generate_all_skips_existing_instruction_file(tmp_path):
    existing = tmp_path / "AGENTS.md"
    existing.write_text("custom instructions\n", encoding="utf-8")

    skipped: list[str] = []
    written = generate_all(tmp_path, [_detection("python")], ["python"], skipped=skipped)

    assert existing.read_text(encoding="utf-8") == "custom instructions\n"
    assert "AGENTS.md: already exists" in skipped
    assert tmp_path / "CLAUDE.md" in written


def test_generate_all_force_overwrites_existing_instruction_file(tmp_path):
    existing = tmp_path / "AGENTS.md"
    existing.write_text("custom instructions\n", encoding="utf-8")

    skipped: list[str] = []
    written = generate_all(
        tmp_path,
        [_detection("python")],
        ["python"],
        overwrite=True,
        skipped=skipped,
    )

    assert "custom instructions" not in existing.read_text(encoding="utf-8")
    assert skipped == []
    assert existing in written


def test_install_skills_skips_existing_internal_skill(tmp_path):
    existing = tmp_path / ".ai" / "skills" / "python" / "SKILL.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("custom skill\n", encoding="utf-8")

    result = install_skills(
        tmp_path,
        [_detection("python")],
        ["python"],
        install_external=False,
    )

    assert existing.read_text(encoding="utf-8") == "custom skill\n"
    assert result.installed == []
    assert ".ai/skills/python/SKILL.md: already exists" in result.skipped
