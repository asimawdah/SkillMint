from __future__ import annotations

import json
from pathlib import Path

from skillmint.detectors import detect
from skillmint.instruction_bundle import verify_instruction_bundle, write_instruction_bundle


def test_instruction_bundle_verification_detects_stale_stack_summary(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\ndependencies = ['fastapi']\n", encoding="utf-8")
    write_instruction_bundle(tmp_path, detect(tmp_path), selected_stack_ids=["python", "fastapi"])
    manifest_path = tmp_path / ".ai/instructions/MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["summary"]["stack_count"] = 1
    manifest["summary"]["stack_ids"] = ["fastapi", "python"]
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = verify_instruction_bundle(tmp_path)

    assert result["ok"] is False
    assert "MANIFEST.json: summary.stack_count should be 2" in result["errors"]
    assert "MANIFEST.json: summary.stack_ids do not match stacks[].id order" in result["errors"]


def test_instruction_bundle_verification_requires_stack_list_shape(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")
    write_instruction_bundle(tmp_path, detect(tmp_path), selected_stack_ids=["python"])
    manifest_path = tmp_path / ".ai/instructions/MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["stacks"] = {"python": manifest["stacks"][0]}
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = verify_instruction_bundle(tmp_path)

    assert result["ok"] is False
    assert "MANIFEST.json: stacks must be a list" in result["errors"]
    assert "MANIFEST.json: summary.stack_count should be 0" in result["errors"]


def test_instruction_bundle_verification_rejects_malformed_sha256_digest(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")
    write_instruction_bundle(tmp_path, detect(tmp_path), selected_stack_ids=["python"])
    manifest_path = tmp_path / ".ai/instructions/MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["file_hashes"][".ai/instructions/README.md"] = "not-a-sha256-digest"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = verify_instruction_bundle(tmp_path)

    assert result["ok"] is False
    assert "MANIFEST.json: file_hashes['.ai/instructions/README.md'] must be a 64-character sha256 hex digest" in result["errors"]
    assert ".ai/instructions/README.md: sha256 mismatch" in result["errors"]
