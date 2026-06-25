from pathlib import Path

from skillmint.generators import generate_all, generate_internal_skill, preview_generated_skills
from skillmint.models import Detection, StackDefinition


def test_generate_all_writes_expected_instruction_files(tmp_path: Path) -> None:
    stack = StackDefinition(
        id="python",
        name="Python",
        commands={"test": "pytest -q"},
        rules=["Keep functions small and testable."],
        avoid=[".env", "__pycache__/"],
    )
    detections = [Detection(stack=stack, confidence=100, reasons=["pyproject.toml found"])]

    written_files = generate_all(tmp_path, detections, selected_stack_ids=["python"])

    relative_paths = sorted(path.relative_to(tmp_path).as_posix() for path in written_files)
    assert relative_paths == [
        ".cursor/rules/project.mdc",
        ".github/copilot-instructions.md",
        "AGENTS.md",
        "CLAUDE.md",
    ]

    agents_md = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "# AI Agent Instructions" in agents_md
    assert "- Python" in agents_md
    assert "- test: `pytest -q`" in agents_md
    assert "- `.env`" in agents_md

    cursor_rule = (tmp_path / ".cursor/rules/project.mdc").read_text(encoding="utf-8")
    assert cursor_rule.startswith("---\nalwaysApply: true\n---")


def test_generate_all_ignores_unselected_stacks(tmp_path: Path) -> None:
    detections = [
        Detection(stack=StackDefinition(id="python", name="Python"), confidence=100),
        Detection(stack=StackDefinition(id="go", name="Go"), confidence=80),
    ]

    written_files = generate_all(tmp_path, detections, selected_stack_ids=["go"])

    agents_md = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert len(written_files) == 4
    assert "- Go" in agents_md
    assert "- Python" not in agents_md


def test_preview_generated_skills_returns_selected_skill_content() -> None:
    detections = [
        Detection(
            stack=StackDefinition(
                id="python",
                name="Python",
                commands={"test": "pytest -q"},
                rules=["Keep functions small and testable."],
            ),
            confidence=100,
        ),
        Detection(stack=StackDefinition(id="go", name="Go"), confidence=80),
    ]

    previews = preview_generated_skills(detections, selected_stack_ids=["python"])

    assert len(previews) == 1
    path, content = previews[0]
    assert path == ".ai/skills/python/SKILL.md"
    assert "# Python Skill" in content
    assert "- test: `pytest -q`" in content
    assert "# Go Skill" not in content


def test_generate_internal_skill_includes_commands_rules_directories_and_avoid_items() -> None:
    stack = StackDefinition(
        id="flutter",
        name="Flutter",
        commands={"analyze": "flutter analyze"},
        rules=["Follow existing architecture."],
        directories=["lib/", "test/"],
        avoid=["build/"],
    )

    content = generate_internal_skill(stack)

    assert "# Flutter Skill" in content
    assert "- analyze: `flutter analyze`" in content
    assert "- Follow existing architecture." in content
    assert "- `lib/`" in content
    assert "- `build/`" in content
    assert content.endswith("\n")
