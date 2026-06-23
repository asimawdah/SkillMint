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
}
