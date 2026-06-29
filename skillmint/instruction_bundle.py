from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from .models import Detection


DEFAULT_INSTRUCTIONS_DIR = ".ai/instructions"


def write_instruction_bundle(root: Path, detections: List[Detection], selected_stack_ids: Iterable[str], *, output_dir: str = DEFAULT_INSTRUCTIONS_DIR, overwrite: bool = False, skipped: List[str] | None = None) -> List[Path]:
    selected_ids = set(selected_stack_ids)
    selected = [d for d in detections if d.id in selected_ids]
    if not selected:
        return []
    target = _safe_output_dir(root, output_dir)
    outputs = {
        "README.md": _readme(selected),
        "STACKS.md": _stacks(selected),
        "COMMANDS.md": _commands(selected),
        "SAFE_CHANGES.md": _safe_changes(selected),
    }
    written: List[Path] = []
    for name, content in outputs.items():
        path = target / name
        relative = path.relative_to(root).as_posix()
        if path.exists() and not overwrite:
            if skipped is not None:
                skipped.append(f"{relative}: already exists")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written


def planned_instruction_bundle_outputs(output_dir: str = DEFAULT_INSTRUCTIONS_DIR) -> List[str]:
    base = output_dir.strip().strip("/") or DEFAULT_INSTRUCTIONS_DIR
    return [f"{base}/README.md", f"{base}/STACKS.md", f"{base}/COMMANDS.md", f"{base}/SAFE_CHANGES.md"]


def _safe_output_dir(root: Path, output_dir: str) -> Path:
    target = (root / (output_dir.strip() or DEFAULT_INSTRUCTIONS_DIR)).resolve()
    target.relative_to(root.resolve())
    return target


def _readme(detections: List[Detection]) -> str:
    names = ", ".join(d.name for d in detections)
    return f"# Project AI Instructions\n\nDetected stacks: {names}\n\nRead STACKS.md, COMMANDS.md, and SAFE_CHANGES.md before changing the project.\n"


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
    lines = ["# Safe Change Rules", "", "- Inspect relevant files before editing.", "- Keep changes focused.", "- Add or update tests when behavior changes.", ""]
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
