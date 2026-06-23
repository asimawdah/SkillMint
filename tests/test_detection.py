from pathlib import Path

from skillmint.detectors import detect
from skillmint.generators import generate_all
from skillmint.installer import install_skills


def detected_ids(root: Path) -> set[str]:
    return {d.id for d in detect(root)}


def test_detect_flutter(tmp_path: Path):
    (tmp_path / "pubspec.yaml").write_text(
        "name: demo\ndependencies:\n  flutter:\n    sdk: flutter\n",
        encoding="utf-8",
    )
    (tmp_path / "lib").mkdir()
    assert "flutter" in detected_ids(tmp_path)


def test_detect_react(tmp_path: Path):
    (tmp_path / "package.json").write_text('{"dependencies":{"react":"latest","vite":"latest"}}', encoding="utf-8")
    assert "react" in detected_ids(tmp_path)


def test_detect_node_optional_dependencies(tmp_path: Path):
    (tmp_path / "package.json").write_text('{"optionalDependencies":{"express":"latest"}}', encoding="utf-8")
    ids = detected_ids(tmp_path)
    assert "node" in ids
    assert "express" in ids


def test_detect_node_bundled_dependencies_list(tmp_path: Path):
    (tmp_path / "package.json").write_text('{"bundledDependencies":["react"]}', encoding="utf-8")
    ids = detected_ids(tmp_path)
    assert "node" in ids
    assert "react" in ids


def test_detect_laravel(tmp_path: Path):
    (tmp_path / "artisan").write_text("", encoding="utf-8")
    (tmp_path / "composer.json").write_text('{"require":{"laravel/framework":"^11.0"}}', encoding="utf-8")
    assert "laravel" in detected_ids(tmp_path)


def test_detect_python_fastapi(tmp_path: Path):
    (tmp_path / "requirements.txt").write_text("fastapi\nuvicorn\npytest\n", encoding="utf-8")
    ids = detected_ids(tmp_path)
    assert "python" in ids
    assert "fastapi" in ids


def test_detect_docker_and_github_actions(tmp_path: Path):
    (tmp_path / "Dockerfile").write_text("FROM python:3.12-slim\n", encoding="utf-8")
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text("name: CI\n", encoding="utf-8")
    ids = detected_ids(tmp_path)
    assert "docker" in ids
    assert "github-actions" in ids


def test_generate_files_and_local_skill(tmp_path: Path):
    (tmp_path / "package.json").write_text('{"dependencies":{"react":"latest"}}', encoding="utf-8")
    detections = detect(tmp_path)
    selected = ["react"]
    written = generate_all(tmp_path, detections, selected)
    result = install_skills(tmp_path, detections, selected, install_external=False)

    assert tmp_path.joinpath("AGENTS.md").exists()
    assert tmp_path.joinpath("CLAUDE.md").exists()
    assert tmp_path.joinpath(".cursor/rules/project.mdc").exists()
    assert tmp_path.joinpath(".github/copilot-instructions.md").exists()
    assert tmp_path.joinpath(".ai/skills/react/SKILL.md").exists()
    assert len(written) == 4
    assert result.installed == [".ai/skills/react/SKILL.md"]
