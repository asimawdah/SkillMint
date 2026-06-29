from __future__ import annotations

from pathlib import Path

import pytest

from skillmint.detectors import detect
from skillmint.instruction_bundle import planned_instruction_bundle_outputs, validate_instruction_bundle_dir, write_instruction_bundle


def test_instruction_bundle_detects_multiple_project_types_and_writes_folder(tmp_path: Path) -> None:
    (tmp_path / "pubspec.yaml").write_text("name: demo\ndependencies:\n  flutter:\n    sdk: flutter\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\ndependencies = ['fastapi']\n", encoding="utf-8")
    (tmp_path / "Dockerfile").write_text("FROM python:3.12-slim\n", encoding="utf-8")

    detections = detect(tmp_path)
    ids = {item.id for item in detections}

    assert {"flutter", "python", "fastapi", "docker"}.issubset(ids)

    written = write_instruction_bundle(
        tmp_path,
        detections,
        selected_stack_ids=["flutter", "python", "fastapi", "docker"],
        output_dir=".ai/instructions",
    )

    relative = sorted(path.relative_to(tmp_path).as_posix() for path in written)
    assert relative == [
        ".ai/instructions/COMMANDS.md",
        ".ai/instructions/README.md",
        ".ai/instructions/SAFE_CHANGES.md",
        ".ai/instructions/STACKS.md",
    ]

    stacks = (tmp_path / ".ai/instructions/STACKS.md").read_text(encoding="utf-8")
    assert "## Flutter / Dart" in stacks
    assert "## Python" in stacks
    assert "## FastAPI" in stacks
    assert "## Docker" in stacks
    assert "found Flutter pubspec.yaml" in stacks

    commands = (tmp_path / ".ai/instructions/COMMANDS.md").read_text(encoding="utf-8")
    assert "flutter test" in commands
    assert "pytest" in commands
    assert "docker build ." in commands


def test_instruction_bundle_skips_existing_files_without_force(tmp_path: Path) -> None:
    (tmp_path / "go.mod").write_text("module example.com/demo\n", encoding="utf-8")
    target = tmp_path / ".ai/instructions"
    target.mkdir(parents=True)
    (target / "README.md").write_text("custom notes\n", encoding="utf-8")

    skipped: list[str] = []
    written = write_instruction_bundle(
        tmp_path,
        detect(tmp_path),
        selected_stack_ids=["go"],
        skipped=skipped,
    )

    assert (target / "README.md").read_text(encoding="utf-8") == "custom notes\n"
    assert ".ai/instructions/README.md: already exists" in skipped
    assert ".ai/instructions/STACKS.md" in {path.relative_to(tmp_path).as_posix() for path in written}


def test_instruction_bundle_rejects_output_outside_project(tmp_path: Path) -> None:
    (tmp_path / "go.mod").write_text("module example.com/demo\n", encoding="utf-8")

    with pytest.raises(ValueError, match="inside the project root"):
        write_instruction_bundle(tmp_path, detect(tmp_path), selected_stack_ids=["go"], output_dir="../outside")


def test_validate_instruction_bundle_dir_accepts_nested_project_path(tmp_path: Path) -> None:
    assert validate_instruction_bundle_dir(tmp_path, "docs/project-ai") == tmp_path / "docs/project-ai"


def test_validate_instruction_bundle_dir_normalises_backslashes(tmp_path: Path) -> None:
    assert validate_instruction_bundle_dir(tmp_path, r"docs\\project-ai") == tmp_path / "docs/project-ai"


def test_validate_instruction_bundle_dir_rejects_absolute_path_outside_project(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-ai"

    with pytest.raises(ValueError, match="inside the project root"):
        validate_instruction_bundle_dir(tmp_path, str(outside))


def test_planned_instruction_bundle_outputs_uses_custom_folder() -> None:
    assert planned_instruction_bundle_outputs("docs/project") == [
        "docs/project/README.md",
        "docs/project/STACKS.md",
        "docs/project/COMMANDS.md",
        "docs/project/SAFE_CHANGES.md",
    ]


def test_planned_instruction_bundle_outputs_normalises_empty_and_windows_paths() -> None:
    assert planned_instruction_bundle_outputs("   ") == [
        ".ai/instructions/README.md",
        ".ai/instructions/STACKS.md",
        ".ai/instructions/COMMANDS.md",
        ".ai/instructions/SAFE_CHANGES.md",
    ]
    assert planned_instruction_bundle_outputs(r"docs\\project") == [
        "docs/project/README.md",
        "docs/project/STACKS.md",
        "docs/project/COMMANDS.md",
        "docs/project/SAFE_CHANGES.md",
    ]
