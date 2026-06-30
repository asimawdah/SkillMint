from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from .models import Detection


DEFAULT_INSTRUCTIONS_DIR = ".ai/instructions"
INSTRUCTION_BUNDLE_FILES = ["README.md", "STACKS.md", "COMMANDS.md", "SAFE_CHANGES.md", "NEXT_STEPS.md", "MANIFEST.json"]
INSTRUCTION_BUNDLE_ROLES = {
    "human_entrypoint": "README.md",
    "stack_evidence": "STACKS.md",
    "commands": "COMMANDS.md",
    "safe_change_rules": "SAFE_CHANGES.md",
    "next_steps": "NEXT_STEPS.md",
    "machine_manifest": "MANIFEST.json",
}
SCHEMA_VERSION = "1.1"


def write_instruction_bundle(root: Path, detections: List[Detection], selected_stack_ids: Iterable[str], *, output_dir: str = DEFAULT_INSTRUCTIONS_DIR, overwrite: bool = False, skipped: List[str] | None = None) -> List[Path]:
    selected_ids = set(selected_stack_ids)
    selected = [d for d in detections if d.id in selected_ids]
    if not selected:
        return []
    target = validate_instruction_bundle_dir(root, output_dir)
    outputs = {
        "README.md": _readme(selected),
        "STACKS.md": _stacks(selected),
        "COMMANDS.md": _commands(selected),
        "SAFE_CHANGES.md": _safe_changes(selected),
        "NEXT_STEPS.md": _next_steps(selected),
        "MANIFEST.json": _manifest(selected, output_dir),
    }
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
    raw_output_dir = output_dir.strip()
    if Path(raw_output_dir).is_absolute():
        target = Path(raw_output_dir).resolve()
    else:
        target = (resolved_root / _normalise_output_dir(output_dir)).resolve()
    try:
        target.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("--instructions-dir must stay inside the project root") from exc
    return target


def _normalise_output_dir(output_dir: str = DEFAULT_INSTRUCTIONS_DIR) -> str:
    cleaned = output_dir.strip().replace("\\", "/").strip("/")
    parts = [part for part in cleaned.split("/") if part]
    return "/".join(parts) or DEFAULT_INSTRUCTIONS_DIR


def _bundle_path(base: str, filename: str) -> str:
    return f"{base}/{filename}"


def _bundle_role_paths(base: str) -> dict[str, str]:
    return {role: _bundle_path(base, filename) for role, filename in INSTRUCTION_BUNDLE_ROLES.items()}


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


def _next_steps(detections: List[Detection]) -> str:
    lines = ["# Next Steps", "", "1. Confirm detected stacks in STACKS.md.", "2. Run relevant commands from COMMANDS.md.", "3. Follow SAFE_CHANGES.md.", "4. Refresh this folder when project structure changes.", "", "## Per-stack checks", ""]
    for detection in detections:
        lines += [f"### {detection.name}", ""]
        command = _preferred_validation_command(detection)
        if command:
            lines.append(f"- Validate related changes with `{command}`.")
        else:
            lines.append("- Add a validation command when this stack gains tests or checks.")
        if detection.stack.directories:
            paths = ", ".join(f"`{path}`" for path in detection.stack.directories[:3])
            lines.append(f"- Review expected paths: {paths}.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _manifest(detections: List[Detection], output_dir: str = DEFAULT_INSTRUCTIONS_DIR) -> str:
    base = _normalise_output_dir(output_dir)
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
    role_paths = _bundle_role_paths(base)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "bundle_dir": base,
        "entrypoints": {
            "human": role_paths["human_entrypoint"],
            "machine": role_paths["machine_manifest"],
        },
        "files": [f"{base}/{name}" for name in INSTRUCTION_BUNDLE_FILES],
        "files_by_role": role_paths,
        "summary": {
            "stack_count": len(stacks),
            "stack_ids": [stack["id"] for stack in stacks],
            "validation_commands": validation_commands,
            "has_validation_commands": bool(validation_commands),
        },
        "stacks": stacks,
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n