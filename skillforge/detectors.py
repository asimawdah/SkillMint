from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from .models import Detection
from .registry import REGISTRY


IGNORED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    "vendor",
    ".venv",
    "build",
    "dist",
    ".dart_tool",
}


def exists(root: Path, relative: str) -> bool:
    return (root / relative).exists()


def any_exists(root: Path, paths: Iterable[str]) -> bool:
    return any(exists(root, p) for p in paths)


def read_text_safe(path: Path, limit: int = 200_000) -> str:
    try:
        data = path.read_text(encoding="utf-8", errors="ignore")
        return data[:limit]
    except OSError:
        return ""


def detect(root: Path) -> List[Detection]:
    detections: List[Detection] = []
    detections.extend(_detect_flutter(root))
    detections.extend(_detect_react(root))
    detections.extend(_detect_laravel(root))
    detections.extend(_detect_python(root))
    detections.extend(_detect_go(root))
    detections.extend(_detect_docker(root))
    detections.extend(_detect_github_actions(root))

    by_id = {}
    for item in detections:
        previous = by_id.get(item.id)
        if previous is None or item.confidence > previous.confidence:
            by_id[item.id] = item

    return sorted(by_id.values(), key=lambda d: (-d.confidence, d.name.lower()))


def _detect_flutter(root: Path) -> List[Detection]:
    reasons = []
    confidence = 0
    if exists(root, "pubspec.yaml"):
        confidence += 50
        reasons.append("found pubspec.yaml")
        text = read_text_safe(root / "pubspec.yaml")
        if "flutter:" in text or "sdk: flutter" in text:
            confidence += 30
            reasons.append("pubspec.yaml references Flutter")
    if exists(root, "lib"):
        confidence += 10
        reasons.append("found lib/")
    if any_exists(root, ["android", "ios"]):
        confidence += 10
        reasons.append("found mobile platform directories")
    return [Detection(REGISTRY["flutter"], min(confidence, 100), reasons)] if confidence >= 50 else []


def _detect_react(root: Path) -> List[Detection]:
    package = root / "package.json"
    if not package.exists():
        return []
    reasons = ["found package.json"]
    confidence = 35
    try:
        data = json.loads(read_text_safe(package))
    except json.JSONDecodeError:
        data = {}
    deps = {}
    for key in ("dependencies", "devDependencies"):
        if isinstance(data.get(key), dict):
            deps.update(data[key])
    if "react" in deps:
        confidence += 45
        reasons.append("package.json includes react")
    if "vite" in deps or exists(root, "vite.config.ts") or exists(root, "vite.config.js"):
        confidence += 10
        reasons.append("detected Vite")
    if "next" in deps or exists(root, "next.config.js") or exists(root, "next.config.mjs"):
        confidence += 10
        reasons.append("detected Next.js")
    return [Detection(REGISTRY["react"], min(confidence, 100), reasons)] if confidence >= 50 else []


def _detect_laravel(root: Path) -> List[Detection]:
    reasons = []
    confidence = 0
    if exists(root, "artisan"):
        confidence += 45
        reasons.append("found artisan")
    composer = root / "composer.json"
    if composer.exists():
        confidence += 25
        reasons.append("found composer.json")
        text = read_text_safe(composer)
        if "laravel/framework" in text:
            confidence += 30
            reasons.append("composer.json includes laravel/framework")
    if exists(root, "app/Http/Controllers"):
        confidence += 10
        reasons.append("found app/Http/Controllers")
    return [Detection(REGISTRY["laravel"], min(confidence, 100), reasons)] if confidence >= 50 else []


def _detect_python(root: Path) -> List[Detection]:
    python_markers = ["pyproject.toml", "requirements.txt", "setup.py", "setup.cfg", "Pipfile"]
    if not any_exists(root, python_markers):
        return []
    detections: List[Detection] = []
    confidence = 55
    reasons = ["found Python dependency or packaging file"]
    all_text = "\n".join(read_text_safe(root / marker) for marker in python_markers if exists(root, marker))

    if "fastapi" in all_text.lower() or _file_contains(root, "main.py", "FastAPI") or _file_contains(root, "app/main.py", "FastAPI"):
        detections.append(Detection(REGISTRY["fastapi"], 85, reasons + ["detected FastAPI reference"]))
    if exists(root, "manage.py") or "django" in all_text.lower():
        detections.append(Detection(REGISTRY["django"], 85, reasons + ["detected Django reference"]))

    detections.append(Detection(REGISTRY["python"], confidence, reasons))
    return detections


def _file_contains(root: Path, relative: str, needle: str) -> bool:
    path = root / relative
    return path.exists() and needle in read_text_safe(path)


def _detect_go(root: Path) -> List[Detection]:
    reasons = []
    confidence = 0
    if exists(root, "go.mod"):
        confidence += 80
        reasons.append("found go.mod")
    if any(root.glob("*.go")):
        confidence += 20
        reasons.append("found Go files")
    return [Detection(REGISTRY["go"], min(confidence, 100), reasons)] if confidence >= 60 else []


def _detect_docker(root: Path) -> List[Detection]:
    reasons = []
    confidence = 0
    if exists(root, "Dockerfile"):
        confidence += 60
        reasons.append("found Dockerfile")
    if any_exists(root, ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]):
        confidence += 40
        reasons.append("found Docker Compose file")
    return [Detection(REGISTRY["docker"], min(confidence, 100), reasons)] if confidence >= 40 else []


def _detect_github_actions(root: Path) -> List[Detection]:
    workflows = root / ".github" / "workflows"
    if workflows.exists() and (any(workflows.glob("*.yml")) or any(workflows.glob("*.yaml"))):
        return [Detection(REGISTRY["github-actions"], 80, ["found .github/workflows/"])]
    return []
