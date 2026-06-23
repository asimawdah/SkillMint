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
}
