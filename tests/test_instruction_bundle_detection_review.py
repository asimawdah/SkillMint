from __future__ import annotations

import json
from pathlib import Path

from skillmint.instruction_bundle import verify_instruction_bundle, write_instruction_bundle
from skillmint.models import Detection, StackDefinition


def _low_confidence_detection() -> Detection:
    return Detection(
        stack=StackDefinition(
            id="custom-stack",
            name="Custom Stack",
            commands={"test": "custom test"},
            directories=["src"],
            rules=["Confirm generated guidance against project docs before editing."],
        ),
        confidence=45,
        reasons=["Only one weak marker matched."],
    )


def test_instruction_bundle_flags_low_confidence_detections(tmp_path: Path) -> None:
    detection = _low_confidence_detection()

    write_instruction_bundle(tmp_path, [detection], selected_stack_ids=["custom-stack"])

    manifest = json.loads((tmp_path / ".ai/instructions/MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["summary"]["low_confidence_threshold"] == 70
    assert manifest["summary"]["low_confidence_stack_ids"] == ["custom-stack"]
    assert manifest["summary"]["requires_detection_review"] is True

    next_steps = (tmp_path / ".ai/instructions/NEXT_STEPS.md").read_text(encoding="utf-8")
    assert "## Detection confidence review" in next_steps
    assert "`custom-stack`" in next_steps
    assert "Confirm this detection manually" in next_steps

    assert verify_instruction_bundle(tmp_path)["ok"] is True


def test_instruction_bundle_verification_detects_stale_low_confidence_summary(tmp_path: Path) -> None:
    detection = _low_confidence_detection()
    write_instruction_bundle(tmp_path, [detection], selected_stack_ids=["custom-stack"])
    manifest_path = tmp_path / ".ai/instructions/MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["summary"]["low_confidence_stack_ids"] = []
    manifest["summary"]["requires_detection_review"] = False
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = verify_instruction_bundle(tmp_path)

    assert result["ok"] is False
    assert "MANIFEST.json: summary.low_confidence_stack_ids do not match stacks below the confidence threshold" in result["errors"]
    assert "MANIFEST.json: summary.requires_detection_review does not match low-confidence detections" in result["errors"]


def test_instruction_bundle_verification_rejects_invalid_confidence_values(tmp_path: Path) -> None:
    detection = _low_confidence_detection()
    write_instruction_bundle(tmp_path, [detection], selected_stack_ids=["custom-stack"])
    manifest_path = tmp_path / ".ai/instructions/MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["stacks"][0]["confidence"] = 125
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = verify_instruction_bundle(tmp_path)

    assert result["ok"] is False
    assert "MANIFEST.json: stack 'custom-stack' confidence must be an integer from 0 to 100" in result["errors"]
