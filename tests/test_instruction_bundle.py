from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from skillmint.cli import main
from skillmint.detectors import detect
from skillmint.instruction_bundle import planned_instruction_bundle_outputs, validate_instruction_bundle_dir, verify_instruction_bundle, write_instruction_bundle


EXPECTED_BUNDLE_FILES = [
    ".ai/instructions/README.md",
    ".ai/instructions/STACKS.md",
    ".ai/instructions/COMMANDS.md",
    ".ai/instructions/SAFE_CHANGES.md",
    ".ai/instructions/NEXT_STEPS.md",
    ".ai/instructions/MANIFEST.json",
]


def test_instruction_bundle_detects_multiple_project_types_and_writes_folder(tmp_path: Path) -> None:
    (tmp_path / "pubspec.yaml").write_text("name: demo\ndependencies:\n  flutter:\n    sdk: flutter\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\ndependencies = ['fastapi']\n", encoding="utf-8")
    (tmp_path / "Dockerfile").write_text("FROM python:3.12-slim\n", encoding="utf-8")

    detections = detect(tmp_path)
    ids = {item.id for item in detections}
    assert {"flutter", "python", "fastapi", "docker"}.issubset(ids)

    written = write_instruction_bundle(tmp_path, detections, selected_stack_ids=["flutter", "python", "fastapi", "docker"], output_dir=".ai/instructions")
    relative = sorted(path.relative_to(tmp_path).as_posix() for path in written)
    assert relative == sorted(EXPECTED_BUNDLE_FILES)

    commands = (tmp_path / ".ai/instructions/COMMANDS.md").read_text(encoding="utf-8")
    assert "flutter test" in commands
    assert "pytest" in commands
    assert "docker build ." in commands

    next_steps = (tmp_path / ".ai/instructions/NEXT_STEPS.md").read_text(encoding="utf-8")
    assert "Validate related changes with `flutter test`" in next_steps


def test_instruction_bundle_writes_machine_readable_manifest(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")
    write_instruction_bundle(tmp_path, detect(tmp_path), selected_stack_ids=["python"], output_dir="docs/project-ai")

    manifest = json.loads((tmp_path / "docs/project-ai/MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "1.5"
    assert manifest["bundle_dir"] == "docs/project-ai"
    assert manifest["entrypoints"] == {"human": "docs/project-ai/README.md", "machine": "docs/project-ai/MANIFEST.json"}
    assert manifest["files_by_role"]["commands"] == "docs/project-ai/COMMANDS.md"
    assert manifest["files_by_role"]["safe_change_rules"] == "docs/project-ai/SAFE_CHANGES.md"
    assert manifest["summary"] == {
        "stack_count": 1,
        "stack_ids": ["python"],
        "validation_commands": ["pytest"],
        "has_validation_commands": True,
        "missing_validation_stack_ids": [],
        "requires_validation_review": False,
    }
    assert manifest["stacks"][0]["id"] == "python"
    assert manifest["stacks"][0]["validation_command"] == "pytest"


def test_instruction_bundle_manifest_includes_file_hashes(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")
    write_instruction_bundle(tmp_path, detect(tmp_path), selected_stack_ids=["python"])

    manifest = json.loads((tmp_path / ".ai/instructions/MANIFEST.json").read_text(encoding="utf-8"))
    hashes = manifest["file_hashes"]
    assert set(hashes) == set(EXPECTED_BUNDLE_FILES) - {".ai/instructions/MANIFEST.json"}
    for relative_path, digest in hashes.items():
        content = (tmp_path / relative_path).read_text(encoding="utf-8")
        assert digest == hashlib.sha256(content.encode("utf-8")).hexdigest()


def test_instruction_bundle_manifest_includes_integrity_metadata(tmp_path: Path) -> None:
    (tmp_path / "go.mod").write_text("module example.com/demo\n", encoding="utf-8")
    write_instruction_bundle(tmp_path, detect(tmp_path), selected_stack_ids=["go"])

    manifest = json.loads((tmp_path / ".ai/instructions/MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["integrity"] == {
        "hash_algorithm": "sha256",
        "hashed_file_count": 5,
        "manifest_included_in_hashes": False,
        "expected_file_count": 6,
    }
    assert manifest["integrity"]["hashed_file_count"] == len(manifest["file_hashes"])
    assert manifest["integrity"]["expected_file_count"] == len(manifest["files"])


def test_instruction_bundle_verification_passes_for_fresh_bundle(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")
    write_instruction_bundle(tmp_path, detect(tmp_path), selected_stack_ids=["python"])

    result = verify_instruction_bundle(tmp_path)

    assert result["ok"] is True
    assert result["bundle_dir"] == ".ai/instructions"
    assert result["checked_files"] == EXPECTED_BUNDLE_FILES[:-1]
    assert result["errors"] == []


def test_instruction_bundle_verification_detects_changed_file(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")
    write_instruction_bundle(tmp_path, detect(tmp_path), selected_stack_ids=["python"])
    (tmp_path / ".ai/instructions/COMMANDS.md").write_text("# Commands\n\nchanged by hand\n", encoding="utf-8")

    result = verify_instruction_bundle(tmp_path)

    assert result["ok"] is False
    assert ".ai/instructions/COMMANDS.md: sha256 mismatch" in result["errors"]


def test_instruction_bundle_verification_detects_missing_file(tmp_path: Path) -> None:
    (tmp_path / "go.mod").write_text("module example.com/demo\n", encoding="utf-8")
    write_instruction_bundle(tmp_path, detect(tmp_path), selected_stack_ids=["go"])
    (tmp_path / ".ai/instructions/NEXT_STEPS.md").unlink()

    result = verify_instruction_bundle(tmp_path)

    assert result["ok"] is False
    assert ".ai/instructions/NEXT_STEPS.md: missing file" in result["errors"]


def test_instruction_bundle_verification_reports_missing_manifest(tmp_path: Path) -> None:
    result = verify_instruction_bundle(tmp_path)

    assert result["ok"] is False
    assert ".ai/instructions/MANIFEST.json: missing manifest" in result["errors"]


def test_cli_verify_instructions_returns_success_for_valid_bundle(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")
    write_instruction_bundle(tmp_path, detect(tmp_path), selected_stack_ids=["python"])

    assert main(["--root", str(tmp_path), "--verify-instructions"]) == 0
    output = capsys.readouterr().out
    assert "Instruction bundle verified: .ai/instructions" in output
    assert ".ai/instructions/COMMANDS.md" in output


def test_cli_verify_instructions_returns_failure_for_invalid_bundle(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "go.mod").write_text("module example.com/demo\n", encoding="utf-8")
    write_instruction_bundle(tmp_path, detect(tmp_path), selected_stack_ids=["go"])
    (tmp_path / ".ai/instructions/README.md").write_text("changed\n", encoding="utf-8")

    assert main(["--root", str(tmp_path), "--verify-instructions"]) == 1
    output = capsys.readouterr().out
    assert "Instruction bundle verification failed: .ai/instructions" in output
    assert ".ai/instructions/README.md: sha256 mismatch" in output


def test_instruction_bundle_manifest_summary_deduplicates_validation_commands(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\ndependencies = ['fastapi']\n", encoding="utf-8")
    write_instruction_bundle(tmp_path, detect(tmp_path), selected_stack_ids=["python", "fastapi"])

    manifest = json.loads((tmp_path / ".ai/instructions/MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["summary"]["stack_count"] == 2
    assert manifest["summary"]["stack_ids"] == ["python", "fastapi"]
    assert manifest["summary"]["validation_commands"] == ["pytest"]
    assert manifest["summary"]["missing_validation_stack_ids"] == []
    assert manifest["summary"]["requires_validation_review"] is False
    assert manifest["files_by_role"]["human_entrypoint"] == ".ai/instructions/README.md"
    assert manifest["files_by_role"]["machine_manifest"] == ".ai/instructions/MANIFEST.json"


def test_instruction_bundle_flags_stacks_without_validation_commands(tmp_path: Path) -> None:
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("name: CI\n", encoding="utf-8")

    write_instruction_bundle(tmp_path, detect(tmp_path), selected_stack_ids=["github-actions"])

    manifest = json.loads((tmp_path / ".ai/instructions/MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["summary"]["missing_validation_stack_ids"] == ["github-actions"]
    assert manifest["summary"]["requires_validation_review"] is True
    assert manifest["summary"]["has_validation_commands"] is False
    assert manifest["stacks"][0]["validation_command"] is None

    next_steps = (tmp_path / ".ai/instructions/NEXT_STEPS.md").read_text(encoding="utf-8")
    assert "## Validation gaps" in next_steps
    assert "`github-actions`" in next_steps


def test_instruction_bundle_manifest_uses_relative_paths_for_absolute_output_dir(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")
    absolute_output_dir = tmp_path / "docs" / "project-ai"

    written = write_instruction_bundle(tmp_path, detect(tmp_path), selected_stack_ids=["python"], output_dir=str(absolute_output_dir))

    assert absolute_output_dir / "MANIFEST.json" in written
    manifest = json.loads((absolute_output_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["bundle_dir"] == "docs/project-ai"
    assert manifest["entrypoints"] == {"human": "docs/project-ai/README.md", "machine": "docs/project-ai/MANIFEST.json"}
    assert manifest["files_by_role"]["machine_manifest"] == "docs/project-ai/MANIFEST.json"
    assert all(not path.startswith(str(tmp_path)) for path in manifest["files"])
    assert all(path.startswith("docs/project-ai/") for path in manifest["file_hashes"])


def test_readme_documents_generated_manifest_output() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    assert ".ai/instructions/MANIFEST.json" in readme
    assert "machine-readable manifest" in readme
    assert "--verify-instructions" in readme


def test_instruction_bundle_readme_points_to_manifest(tmp_path: Path) -> None:
    (tmp_path / "go.mod").write_text("module example.com/demo\n", encoding="utf-8")
    write_instruction_bundle(tmp_path, detect(tmp_path), selected_stack_ids=["go"])
    readme = (tmp_path / ".ai/instructions/README.md").read_text(encoding="utf-8")
    assert "Read MANIFEST.json first" in readme


def test_instruction_bundle_skips_existing_files_without_force(tmp_path: Path) -> None:
    (tmp_path / "go.mod").write_text("module example.com/demo\n", encoding="utf-8")
    target = tmp_path / ".ai/instructions"
    target.mkdir(parents=True)
    (target / "README.md").write_text("custom notes\n", encoding="utf-8")

    skipped: list[str] = []
    written = write_instruction_bundle(tmp_path, detect(tmp_path), selected_stack_ids=["go"], skipped=skipped)
    assert (target / "README.md").read_text(encoding="utf-8") == "custom notes\n"
    assert ".ai/instructions/README.md: already exists" in skipped
    assert ".ai/instructions/STACKS.md" in {path.relative_to(tmp_path).as_posix() for path in written}
    assert ".ai/instructions/NEXT_STEPS.md" in {path.relative_to(tmp_path).as_posix() for path in written}
    assert ".ai/instructions/MANIFEST.json" in {path.relative_to(tmp_path).as_posix() for path in written}


def test_instruction_bundle_rejects_parent_directory_escape(tmp_path: Path) -> None:
    (tmp_path / "go.mod").write_text("module example.com/demo\n", encoding="utf-8")
    with pytest.raises(ValueError, match="without . or .. segments"):
        write_instruction_bundle(tmp_path, detect(tmp_path), selected_stack_ids=["go"], output_dir="../sibling-ai")


def test_validate_instruction_bundle_dir_accepts_nested_project_path(tmp_path: Path) -> None:
    assert validate_instruction_bundle_dir(tmp_path, "docs/project-ai") == tmp_path / "docs/project-ai"


def test_validate_instruction_bundle_dir_normalises_backslashes(tmp_path: Path) -> None:
    assert validate_instruction_bundle_dir(tmp_path, r"docs\project-ai") == tmp_path / "docs/project-ai"


def test_validate_instruction_bundle_dir_rejects_absolute_sibling_path(tmp_path: Path) -> None:
    sibling = tmp_path.parent / "sibling-ai"
    with pytest.raises(ValueError, match="inside the project root"):
        validate_instruction_bundle_dir(tmp_path, str(sibling))


def test_validate_instruction_bundle_dir_rejects_project_root_absolute_path(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="below the project root"):
        validate_instruction_bundle_dir(tmp_path, str(tmp_path))


def test_validate_instruction_bundle_dir_rejects_existing_file_target(tmp_path: Path) -> None:
    target_file = tmp_path / "docs"
    target_file.write_text("not a directory\n", encoding="utf-8")

    with pytest.raises(ValueError, match="not an existing file"):
        validate_instruction_bundle_dir(tmp_path, "docs")


def test_cli_rejects_existing_file_instruction_dir_before_detection(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target_file = tmp_path / "docs"
    target_file.write_text("not a directory\n", encoding="utf-8")

    assert main(["--root", str(tmp_path), "--instructions-dir", "docs", "--verify-instructions"]) == 2
    output = capsys.readouterr().out
    assert "Invalid --instructions-dir" in output
    assert "not an existing file" in output


def test_instruction_bundle_rejects_ambiguous_relative_segments(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="without . or .. segments"):
        validate_instruction_bundle_dir(tmp_path, "docs/../.ai/instructions")
    with pytest.raises(ValueError, match="without . or .. segments"):
        planned_instruction_bundle_outputs("./docs/project-ai")


def test_instruction_bundle_rejects_control_characters_in_output_dir(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="control characters"):
        validate_instruction_bundle_dir(tmp_path, "docs/project\nai")
    with pytest.raises(ValueError, match="control characters"):
        planned_instruction_bundle_outputs("docs/project\tai")


def test_planned_instruction_bundle_outputs_uses_custom_folder() -> None:
    assert planned_instruction_bundle_outputs("docs/project") == [
        "docs/project/README.md",
        "docs/project/STACKS.md",
        "docs/project/COMMANDS.md",
        "docs/project/SAFE_CHANGES.md",
        "docs/project/NEXT_STEPS.md",
        "docs/project/MANIFEST.json",
    ]


def test_planned_instruction_bundle_outputs_normalises_empty_and_windows_paths() -> None:
    assert planned_instruction_bundle_outputs("   ") == EXPECTED_BUNDLE_FILES
    assert planned_instruction_bundle_outputs(r"docs\project") == [
        "docs/project/README.md",
        "docs/project/STACKS.md",
        "docs/project/COMMANDS.md",
        "docs/project/SAFE_CHANGES.md",
        "docs/project/NEXT_STEPS.md",
        "docs/project/MANIFEST.json",
    ]
