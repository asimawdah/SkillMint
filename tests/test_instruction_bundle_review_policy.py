from __future__ import annotations

from pathlib import Path


REVIEW_POLICY = Path("docs/AI_INSTRUCTION_BUNDLE_REVIEW.md")


def test_ai_instruction_bundle_review_policy_exists_and_covers_required_gates() -> None:
    policy = REVIEW_POLICY.read_text(encoding="utf-8")

    required_sections = [
        "## Review goals",
        "## Required gates",
        "**Detection review**",
        "**Validation review**",
        "**Integrity review**",
        "**Path safety review**",
        "**Automation consumption review**",
        "## Safe review command sequence",
        "## Pull request checklist",
    ]
    for section in required_sections:
        assert section in policy

    required_terms = [
        "summary.requires_detection_review",
        "summary.low_confidence_stack_ids",
        "summary.requires_validation_review",
        "integrity.hash_algorithm",
        "file_hashes",
        "lowercase 64-character SHA-256 hex digest",
        "skillmint --verify-instructions",
        "entrypoints",
        "files_by_role",
        "." / "..",
    ]
    for term in required_terms:
        assert term in policy


def test_ai_instruction_bundle_review_policy_keeps_automation_safety_language() -> None:
    policy = REVIEW_POLICY.read_text(encoding="utf-8").lower()

    assert "stop automation when verification fails" in policy
    assert "manual review" in policy
    assert "inside the selected project root" in policy
    assert "do not use ambiguous" in policy
