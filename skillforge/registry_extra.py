from __future__ import annotations

from .models import StackDefinition

EXTRA_REGISTRY = {
    "dart": StackDefinition(
        id="dart",
        name="Dart",
        commands={"Install dependencies": "dart pub get", "Analyze": "dart analyze", "Test": "dart test"},
        directories=["bin/", "lib/", "test/"],
        avoid=[".dart_tool/", "build/"],
        rules=["Follow idiomatic Dart conventions."],
    ),
    "node": StackDefinition(
        id="node",
        name="Node.js / JavaScript / TypeScript",
        commands={"Install dependencies": "npm install", "Dev server": "npm run dev", "Build": "npm run build", "Test": "npm test"},
        directories=["src/", "test/", "scripts/"],
        avoid=["node_modules/", "dist/", "build/"],
        rules=["Use the package manager already used by the project."],
    ),
}
