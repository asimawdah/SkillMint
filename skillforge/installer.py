from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List

from .generators import generate_internal_skill
from .models import Detection, ExternalSkill, StackDefinition


class InstallResult:
    def __init__(self) -> None:
        self.installed: List[str] = []
        self.skipped: List[str] = []
        self.failed: List[str] = []


def install_skills(root: Path, detections: List[Detection], selected_stack_ids: List[str], install_external: bool) -> InstallResult:
    result = InstallResult()
    selected = [d.stack for d in detections if d.id in selected_stack_ids]
    for stack in selected:
        if stack.external_skills and install_external:
            for external in stack.external_skills:
                if _install_external_skill(root, external, result):
                    continue
                _write_external_fallback(root, stack, external, result)
        else:
            _write_internal_skill(root, stack, result)
    return result


def _write_internal_skill(root: Path, stack: StackDefinition, result: InstallResult) -> None:
    path = root / ".ai" / "skills" / stack.id / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(generate_internal_skill(stack), encoding="utf-8")
    result.installed.append(str(path.relative_to(root)))


def _install_external_skill(root: Path, external: ExternalSkill, result: InstallResult) -> bool:
    target = root / external.install_path
    if target.exists() and not target.is_dir():
        result.failed.append(f"{external.name}: target exists and is not a directory: {external.install_path}")
        return False
    if target.exists() and any(target.iterdir()):
        result.skipped.append(f"{external.name}: target already exists at {external.install_path}")
        return True

    git = shutil.which("git")
    if git is None:
        result.failed.append(f"{external.name}: git is not installed")
        return False

    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="skillforge-") as tmp:
        tmp_path = Path(tmp) / "skill"
        command = [git, "clone", "--depth", "1", external.url, str(tmp_path)]
        completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if completed.returncode != 0:
            msg = completed.stderr.strip() or completed.stdout.strip() or "unknown git clone error"
            result.failed.append(f"{external.name}: {msg}")
            return False
        if target.exists():
            shutil.rmtree(target)
        ignore = shutil.ignore_patterns(".git", ".github")
        shutil.copytree(tmp_path, target, ignore=ignore)
        result.installed.append(f"{external.name} -> {external.install_path}")
        return True


def _write_external_fallback(root: Path, stack: StackDefinition, external: ExternalSkill, result: InstallResult) -> None:
    path = root / external.install_path / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {external.name}",
        "",
        "External skill source:",
        "",
        external.url,
        "",
        "SkillForge could not download this external skill automatically, so this local reference was created.",
        "",
        "## Project Stack",
        "",
        f"- {stack.name}",
        "",
        "## Suggested Commands",
        "",
    ]
    for name, command in stack.commands.items():
        lines.append(f"- {name}: `{command}`")
    lines.extend(["", "## Rules", ""])
    for rule in stack.rules:
        lines.append(f"- {rule}")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    result.installed.append(str(path.relative_to(root)))
