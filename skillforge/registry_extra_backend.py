from __future__ import annotations

from .models import StackDefinition

BACKEND_REGISTRY = {
    "rust": StackDefinition(
        id="rust",
        name="Rust",
        commands={"Check": "cargo check", "Test": "cargo test", "Build": "cargo build", "Format": "cargo fmt"},
        directories=["src/", "tests/", "crates/"],
        avoid=["target/"],
        rules=["Follow idiomatic Rust ownership and error handling."],
    ),
    "flask": StackDefinition(
        id="flask",
        name="Flask",
        commands={"Install dependencies": "pip install -r requirements.txt", "Run app": "flask run", "Test": "pytest"},
        directories=["app/", "templates/", "static/", "tests/"],
        avoid=[".venv/", "__pycache__/"],
        rules=["Follow the existing Flask app factory or module layout."],
    ),
}
