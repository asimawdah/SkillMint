from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .models import Detection
from .registry import REGISTRY


NODE_DEPENDENCY_KEYS = (
    "dependencies",
    "devDependencies",
    "peerDependencies",
    "optionalDependencies",
    "bundledDependencies",
    "bundleDependencies",
)


def exists(root: Path, relative: str) -> bool:
    return (root / relative).exists()


def read_text_safe(path: Path, limit: int = 200_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except OSError:
        return ""


def package_json(root: Path) -> dict:
    path = root / "package.json"
    if not path.exists():
        return {}
    try:
        return json.loads(read_text_safe(path))
    except json.JSONDecodeError:
        return {}


def package_names(data: dict) -> set[str]:
    names = set()
    for key in NODE_DEPENDENCY_KEYS:
        value = data.get(key)
        if isinstance(value, dict):
            names.update(value.keys())
        elif isinstance(value, list):
            names.update(item for item in value if isinstance(item, str))
    return names


def add(items: List[Detection], stack_id: str, confidence: int, reasons: List[str]) -> None:
    stack = REGISTRY.get(stack_id)
    if stack is not None:
        items.append(Detection(stack, min(confidence, 100), reasons))


def detect(root: Path) -> List[Detection]:
    detections: List[Detection] = []

    if exists(root, "pubspec.yaml"):
        text = read_text_safe(root / "pubspec.yaml").lower()
        if "flutter:" in text or "sdk: flutter" in text:
            add(detections, "flutter", 95, ["found Flutter pubspec.yaml"])
        else:
            add(detections, "dart", 80, ["found Dart pubspec.yaml"])

    pkg = package_json(root)
    deps = package_names(pkg)
    if pkg:
        add(detections, "node", 65, ["found package.json"])
        if "react" in deps:
            add(detections, "react", 90, ["package.json includes react"])
        if "next" in deps or exists(root, "next.config.js") or exists(root, "next.config.mjs"):
            add(detections, "nextjs", 90, ["detected Next.js"])
        if "vue" in deps or "@vue/core" in deps or exists(root, "vue.config.js"):
            add(detections, "vue", 85, ["detected Vue"])
        if "nuxt" in deps or exists(root, "nuxt.config.ts") or exists(root, "nuxt.config.js"):
            add(detections, "nuxt", 90, ["detected Nuxt"])
        if "svelte" in deps or "@sveltejs/kit" in deps or exists(root, "svelte.config.js"):
            add(detections, "svelte", 90, ["detected Svelte or SvelteKit"])
        if "@angular/core" in deps or exists(root, "angular.json"):
            add(detections, "angular", 90, ["detected Angular"])
        if "express" in deps:
            add(detections, "express", 85, ["detected Express"])
        if "@nestjs/core" in deps:
            add(detections, "nestjs", 90, ["detected NestJS"])
        if "expo" in deps or exists(root, "app.json") or exists(root, "app.config.js") or exists(root, "app.config.ts"):
            add(detections, "expo", 90, ["detected Expo"])

    py_markers = ["pyproject.toml", "requirements.txt", "setup.py", "setup.cfg", "Pipfile"]
    if any(exists(root, marker) for marker in py_markers):
        add(detections, "python", 70, ["found Python packaging or dependency file"])
        text = "\n".join(read_text_safe(root / marker).lower() for marker in py_markers if exists(root, marker))
        if "fastapi" in text or "fastapi" in read_text_safe(root / "main.py").lower() or "fastapi" in read_text_safe(root / "app/main.py").lower():
            add(detections, "fastapi", 90, ["detected FastAPI"])
        if "django" in text or exists(root, "manage.py"):
            add(detections, "django", 90, ["detected Django"])
        if "flask" in text:
            add(detections, "flask", 85, ["detected Flask"])

    if exists(root, "go.mod"):
        add(detections, "go", 95, ["found go.mod"])
    if exists(root, "Cargo.toml"):
        add(detections, "rust", 95, ["found Cargo.toml"])
    if exists(root, "composer.json"):
        composer = read_text_safe(root / "composer.json").lower()
        if "laravel/framework" in composer or exists(root, "artisan"):
            add(detections, "laravel", 95, ["detected Laravel"])
    if exists(root, "pom.xml") or exists(root, "build.gradle") or exists(root, "build.gradle.kts"):
        add(detections, "java", 70, ["found JVM build file"])
        text = read_text_safe(root / "pom.xml").lower() + read_text_safe(root / "build.gradle").lower() + read_text_safe(root / "build.gradle.kts").lower()
        if "spring-boot" in text or "org.springframework.boot" in text:
            add(detections, "spring", 90, ["detected Spring Boot"])
        if "kotlin" in text or exists(root, "src/main/kotlin"):
            add(detections, "kotlin", 85, ["detected Kotlin"])
        if exists(root, "app/src/main/AndroidManifest.xml") or exists(root, "AndroidManifest.xml"):
            add(detections, "android", 90, ["detected Android"])

    if exists(root, "Dockerfile") or exists(root, "docker-compose.yml") or exists(root, "compose.yml"):
        add(detections, "docker", 80, ["detected Docker files"])
    if exists(root, ".github/workflows"):
        add(detections, "github-actions", 80, ["found .github/workflows/"])

    by_id = {}
    for item in detections:
        current = by_id.get(item.id)
        if current is None or item.confidence > current.confidence:
            by_id[item.id] = item
    return sorted(by_id.values(), key=lambda item: (-item.confidence, item.name.lower()))
