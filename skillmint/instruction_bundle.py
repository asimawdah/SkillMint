from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable, List

from .models import Detection


DEFAULT_INSTRUCTIONS_DIR = ".ai/instructions"
INSTRUCTION_BUNDLE_FILES = ["README.md", "STACKS.md", "COMMANDS.md", "SAFE_CHANGES.md", "NEXT_STEPS.md", "MANIFEST.json"]
HASH_ALGORITHM = "sha256"
SHA256_HEX_LENGTH = 64
LOW_CONFIDENCE_THRESHOLD = 70
INSTRUCTION_BUNDLE_ROLES = {
    "human_entrypoint": "README.md",
    "stack_evidence": "STACKS.md",
    "commands": "COMMANDS.md",
    "safe_change_rules": "SAFE_CHANGES.md",
    "next_steps": "NEXT_STEPS.md",
    "machine_manifest": "MANIFEST.json",
}
SCHEMA_VERSION = "1.7"


def write_instruction_bundle(root: Path, detections: List[Detection], selected_stack_ids: Iterable[str], *, output_dir: str = DEFAULT_INSTRUCTIONS_DIR, overwrite: bool = False, skipped: List[str] | None = None) -> List[Path]:
    detection_by_id = {detection.id: detection for detection in detections}
    selected: List[Detection] = []
    seen_ids: set[str] = set()
    for stack_id in selected_stack_ids:
        if stack_id in seen_ids:
            continue
        detection = detection_by_id.get(stack_id)
        if detection is not None:
            selected.append(detection)
            seen_ids.add(stack_id)
    if not selected:
        return []
    target = validate_instruction_bundle_dir(root, output_dir)
    bundle_dir = _relative_bundle_dir(root, target)
    outputs = _instruction_bundle_outputs(selected, bundle_dir)
    written: List[Path] = []
    for name, content in outputs.items():
        path = target / name
        relative = path.relative_to(root.resolve()).as_posix()
        if path.exists() and not overwrite:
            if skipped is not None:
                skipped.append(f"{relative}: already exists")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written


def planned_instruction_bundle_outputs(output_dir: str = DEFAULT_INSTRUCTIONS_DIR) -> List[str]:
    base = _normalise_output_dir(output_dir)
    return [f"{base}/{name}" for name in INSTRUCTION_BUNDLE_FILES]


def validate_instruction_bundle_dir(root: Path, output_dir: str = DEFAULT_INSTRUCTIONS_DIR) -> Path:
    """Return a safe bundle output directory inside the project root."""

    resolved_root = root.resolve()
    cleaned_output_dir = _clean_output_dir(output_dir)
    normalised_output_dir = _normalise_output_dir(output_dir)
    if Path(cleaned_output_dir).is_absolute():
        target = Path(cleaned_output_dir).resolve()
    else:
        target = (resolved_root / normalised_output_dir).resolve()
    try:
        target.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("--instructions-dir must stay inside the project root") from exc
    if target == resolved_root:
        raise ValueError("--instructions-dir must point to a folder below the project root")
    if target.exists() and not target.is_dir():
        raise ValueError("--instructions-dir must point to a folder, not an existing file")
    return target


def verify_instruction_bundle(root: Path, output_dir: str = DEFAULT_INSTRUCTIONS_DIR) -> dict[str, object]:
    """Verify a generated instruction bundle manifest, role paths, and hashed files."""

    target = validate_instruction_bundle_dir(root, output_dir)
    manifest_path = target / "MANIFEST.json"
    bundle_dir = _relative_bundle_dir(root, target)
    expected_files = [_bundle_path(bundle_dir, name) for name in INSTRUCTION_BUNDLE_FILES]
    expected_role_paths = _bundle_role_paths(bundle_dir)
    expected_entrypoints = {
        "human": expected_role_paths["human_entrypoint"],
        "machine": expected_role_paths["machine_manifest"],
    }
    errors: list[str] = []

    if not manifest_path.exists():
        errors.append(f"{_bundle_path(bundle_dir, 'MANIFEST.json')}: missing manifest")
        return {
            "ok": False,
            "bundle_dir": bundle_dir,
            "checked_files": [],
            "expected_files": expected_files,
            "errors": errors,
        }

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_bundle_path(bundle_dir, 'MANIFEST.json')}: invalid JSON at line {exc.lineno}, column {exc.colno}")
        return {
            "ok": False,
            "bundle_dir": bundle_dir,
            "checked_files": [],
            "expected_files": expected_files,
            "errors": errors,
        }

    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"MANIFEST.json: expected schema_version {SCHEMA_VERSION}, found {manifest.get('schema_version')!r}")
    if manifest.get("bundle_dir") != bundle_dir:
        errors.append(f"MANIFEST.json: expected bundle_dir {bundle_dir!r}, found {manifest.get('bundle_dir')!r}")

    manifest_files = manifest.get("files")
    if manifest_files != expected_files:
        errors.append("MANIFEST.json: files list does not match the expected instruction bundle files")

    if manifest.get("entrypoints") != expected_entrypoints:
        errors.append("MANIFEST.json: entrypoints do not match the expected instruction bundle entrypoints")
    if manifest.get("files_by_role") != expected_role_paths:
        errors.append("MANIFEST.json: files_by_role does not match the expected instruction bundle role paths")

    stacks = manifest.get("stacks")
    if not isinstance(stacks, list):
        errors.append("MANIFEST.json: stacks must be a list")
        stacks = []
    stack_ids = [stack.get("id") for stack in stacks if isinstance(stack, dict)]
    low_confidence_stack_ids: list[str] = []
    for stack in stacks:
        if not isinstance(stack, dict):
            errors.append("MANIFEST.json: stacks must contain objects")
            continue
        confidence = stack.get("confidence")
        stack_id = stack.get("id")
        if not isinstance(confidence, int) or confidence < 0 or confidence > 100:
            errors.append(f"MANIFEST.json: stack {stack_id!r} confidence must be an integer from 0 to 100")
            continue
        if isinstance(stack_id, str) and confidence < LOW_CONFIDENCE_THRESHOLD:
            low_confidence_stack_ids.append(stack_id)

    summary = manifest.get("summary") if isinstance(manifest.get("summary"), dict) else {}
    if summary.get("stack_count") != len(stacks):
        errors.append(f"MANIFEST.json: summary.stack_count should be {len(stacks)}")
    if summary.get("stack_ids") != stack_ids:
        errors.append("MANIFEST.json: summary.stack_ids do not match stacks[].id order")
    if summary.get("low_confidence_stack_ids") != low_confidence_stack_ids:
        errors.append("MANIFEST.json: summary.low_confidence_stack_ids do not match stacks below the confidence threshold")
    if summary.get("requires_detection_review") != bool(low_confidence_stack_ids):
        errors.append("MANIFEST.json: summary.requires_detection_review does not match low-confidence detections")

    integrity = manifest.get("integrity") if isinstance(manifest.get("integrity"), dict) else {}
    if integrity.get("hash_algorithm") != HASH_ALGORITHM:
        errors.append(f"MANIFEST.json: expected hash algorithm {HASH_ALGORITHM}")
    if integrity.get("expected_file_count") != len(expected_files):
        errors.append(f"MANIFEST.json: expected_file_count should be {len(expected_files)}")
    if integrity.get("role_count") != len(expected_role_paths):
        errors.append(f"MANIFEST.json: role_count should be {len(expected_role_paths)}")

    file_hashes = manifest.get("file_hashes")
    if not isinstance(file_hashes, dict):
        errors.append("MANIFEST.json: file_hashes must be an object")
        file_hashes = {}
    expected_hashed_files = [path for path in expected_files if not path.endswith("/MANIFEST.json") and path != "MANIFEST.json"]
    if set(file_hashes) != set(expected_hashed_files):
        errors.append("MANIFEST.json: file_hashes keys do not match expected Markdown bundle files")
    for relative_path, expected_digest in file_hashes.items():
        if relative_path in expected_hashed_files and not _is_sha256_digest(expected_digest):
            errors.append(f"MANIFEST.json: file_hashes[{relative_path!r}] must be a 64-character sha256 hex digest")
    if integrity.get("hashed_file_count") != len(file_hashes):
        errors.append("MANIFEST.json: hashed_file_count does not match file_hashes")

    checked_files: list[str] = []
    for relative_path in expected_files:
        path = root.resolve() / relative_path
        if not path.exists():
            errors.append(f"{relative_path}: missing file")
            continue
        if path.is_dir():
            errors.append(f"{relative_path}: expected file but found directory")
            continue
        if relative_path == _bundle_path(bundle_dir, "MANIFEST.json"):
            continue
        digest = hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
        checked_files.append(relative_path)
        expected_digest = file_hashes.get(relative_path)
        if expected_digest != digest:
            errors.append(f"{relative_path}: sha256 mismatch")

    return {
        "ok": not errors,
        "bundle_dir": bundle_dir,
        "checked_files": checked_files,
        "expected_files": expected_files,
        "errors": errors,
    }


def _clean_output_dir(output_dir: str = DEFAULT_INSTRUCTIONS_DIR) -> str:
    return output_dir.strip().replace("\\", "/")


def _normalise_output_dir(output_dir: str = DEFAULT_INSTRUCTIONS_DIR) -> str:
    cleaned = _clean_output_dir(output_dir).strip("/")
    parts = [part for part in cleaned.split("/") if part]
    if not parts:
        return DEFAULT_INSTRUCTIONS_DIR
    unsafe_parts = {".", ".."}
    if any(part in unsafe_parts for part in parts):
        raise ValueError("--instructions-dir must use direct folder names without . or .. segments")
    if any(any(ord(char) < 32 for char in part) for part in parts):
        raise ValueError("--instructions-dir must not contain control characters")
    return "/".join(parts)


def _relative_bundle_dir(root: Path, target: Path) -> str:
    """Return the manifest-facing bundle directory relative to the project root."""

    relative = target.resolve().relative_to(root.resolve()).as_posix()
    return relative or "."


def _bundle_path(base: str, filename: str) -> str:
    if base == ".":
        return filename
    return f"{base}/{filename}"


def _bundle_role_paths(base: str) -> dict[str, str]:
    return {role: _bundle_path(base, filename) for role, filename in INSTRUCTION_BUNDLE_ROLES.items()}


def _content_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _is_sha256_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == SHA256_HEX_LENGTH and all(char in "0123456789abcdef" for char in value.lower())


def _file_hashes(outputs: dict[str, str], base: str) -> dict[str, str]:
    return {
        _bundle_path(base, name): _content_sha256(content)
        for name, content in outputs.items()
        if name != "MANIFEST.json"
    }


def _instruction_bundle_outputs(detections: List[Detection], bundle_dir: str) -> dict[str, str]:
    outputs = {
        "README.md": _readme(detections),
        "STACKS.md": _stacks(detections),
        "COMMANDS.md": _commands(detections),
        "SAFE_CHANGES.md": _safe_changes(detections),
        "NEXT_STEPS.md": _next_steps(detections),
    }
    outputs["MANIFEST.json"] = _manifest(detections, bundle_dir, file_hashes=_file_hashes(outputs, _normalise_output_dir(bundle_dir)))
    return outputs


def _readme(detections: List[Detection]) -> str:
    names = ", ".join(d.name for d in detections)
    return f"# Project Instructions\n\nDetected stacks: {names}\n\nRead MANIFEST.json first for machine-readable metadata, then STACKS.md, COMMANDS.md, SAFE_CHANGES.md, and NEXT_STEPS.md before making changes.\n"


def _stacks(detections: List[Detection]) -> str:
    lines = ["# Detected Stacks", ""]
    for detection in detections:
        lines += [f"## {detection.name}", "", f"Confidence: {detection.confidence}%", ""]
        for reason in detection.reasons:
            lines.append(f"- {reason}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _commands(detections: List[Detection]) -> str:
    lines = ["# Commands", ""]
    for detection in detections:
        if not detection.stack.commands:
            continue
        lines += [f"## {detection.name}", ""]
        for label, command in detection.stack.commands.items():
            lines.append(f"- {label}: `{command}`")
        lines.append("")
    if len(lines) == 2:
        lines.append("No stack-specific commands were detected.")
    return "\n".join(lines).rstrip() + "\n"


def _safe_changes(detections: List[Detection]) -> str:
    lines = ["# Safe Change Rules", "", "- Inspect relevant files first.", "- Keep changes focused.", "- Add or update tests when behavior changes.", ""]
    avoid = []
    for detection in detections:
        if detection.stack.rules:
            lines += [f"## {detection.name}", ""]
            for rule in detection.stack.rules:
                lines.append(f"- {rule}")
            lines.append("")
        avoid.extend(detection.stack.avoid)
    if avoid:
        lines += ["## Avoid editing", ""]
        for item in sorted(set(avoid)):
            lines.append(f"- `{item}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _preferred_validation_command(detection: Detection) -> str | None:
    commands = detection.stack.commands
    for keyword in ("test", "check", "analy"):
        for label, command in commands.items():
            if keyword in label.lower():
                return command
    return next(iter(commands.values()), None)


def _validation_commands(detections: List[Detection]) -> List[str]:
    commands = []
    seen = set()
    for detection in detections:
        command = _preferred_validation_command(detection)
        if command and command not in seen:
            commands.append(command)
            seen.add(command)
    return commands


def _missing_validation_stack_ids(detections: List[Detection]) -> List[str]:
    return [detection.id for detection in detections if _preferred_validation_command(detection) is None]


def _low_confidence_stack_ids(detections: List[Detection]) -> List[str]:
    return [detection.id for detection in detections if detection.confidence < LOW_CONFIDENCE_THRESHOLD]


def _next_steps(detections: List[Detection]) -> str:
    missing_validation = _missing_validation_stack_ids(detections)
    low_confidence = _low_confidence_stack_ids(detections)
    lines = ["# Next Steps", "", "1. Confirm detected stacks in STACKS.md.", "2. Run relevant commands from COMMANDS.md.", "3. Follow SAFE_CHANGES.md.", "4. Refresh this folder when project structure changes.", ""]
    if low_confidence:
        lines += [
            "## Detection confidence review",
            "",
            f"Manually confirm stacks below {LOW_CONFIDENCE_THRESHOLD}% confidence before allowing broad automated edits:",
            "",
        ]
        for stack_id in low_confidence:
            lines.append(f"- `{stack_id}`")
        lines.append("")
    if missing_validation:
        lines += [
            "## Validation gaps",
            "",
            "Add or document validation commands for these detected stacks before relying on automated edits:",
            "",
        ]
        for stack_id in missing_validation:
            lines.append(f"- `{stack_id}`")
        lines.append("")
    lines += ["## Per-stack checks", ""]
    for detection in detections:
        lines += [f"### {detection.name}", ""]
        command = _preferred_validation_command(detection)
        if command:
            lines.append(f"- Validate related changes with `{command}`.")
        else:
            lines.append("- Add a validation command when this stack gains tests or checks.")
        if detection.confidence < LOW_CONFIDENCE_THRESHOLD:
            lines.append("- Confirm this detection manually before making wide project changes.")
        if detection.stack.directories:
            paths = ", ".join(f"`{path}`" for path in detection.stack.directories[:3])
            lines.append(f"- Review expected paths: {paths}.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _manifest(detections: List[Detection], bundle_dir: str = DEFAULT_INSTRUCTIONS_DIR, *, file_hashes: dict[str, str] | None = None) -> str:
    base = _normalise_output_dir(bundle_dir)
    stacks = []
    for detection in detections:
        stacks.append(
            {
                "id": detection.id,
                "name": detection.name,
                "confidence": detection.confidence,
                "reasons": list(detection.reasons),
                "commands": dict(detection.stack.commands),
                "directories": list(detection.stack.directories),
                "avoid": sorted(set(detection.stack.avoid)),
                "validation_command": _preferred_validation_command(detection),
            }
        )
    validation_commands = _validation_commands(detections)
    missing_validation_stack_ids = _missing_validation_stack_ids(detections)
    low_confidence_stack_ids = _low_confidence_stack_ids(detections)
    role_paths = _bundle_role_paths(base)
    files = [_bundle_path(base, name) for name in INSTRUCTION_BUNDLE_FILES]
    hashed_files = file_hashes or {}
    payload = {
        "schema_version": SCHEMA_VERSION,
        "bundle_dir": base,
        "entrypoints": {
            "human": role_paths["human_entrypoint"],
            "machine": role_paths["machine_manifest"],
        },
        "files": files,
        "file_hashes": hashed_files,
        "files_by_role": role_paths,
        "integrity": {
            "hash_algorithm": HASH_ALGORITHM,
            "hashed_file_count": len(hashed_files),
            "manifest_included_in_hashes": False,
            "expected_file_count": len(files),
            "role_count": len(role_paths),
        },
        "summary": {
            "stack_count": len(stacks),
            "stack_ids": [stack["id"] for stack in stacks],
            "validation_commands": validation_commands,
            "has_validation_commands": bool(validation_commands),
            "missing_validation_stack_ids": missing_validation_stack_ids,
            "requires_validation_review": bool(missing_validation_stack_ids),
            "low_confidence_threshold": LOW_CONFIDENCE_THRESHOLD,
            "low_confidence_stack_ids": low_confidence_stack_ids,
            "requires_detection_review": bool(low_confidence_stack_ids),
        },
        "stacks": stacks,
    }
    return f"{json.dumps(payload, indent=2, sort_keys=True)}\n"
