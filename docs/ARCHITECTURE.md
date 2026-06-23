# Architecture

SkillMint is intentionally small and dependency-light.

## Flow

1. `skillmint` starts the CLI wizard.
2. Detectors inspect the project root for stack markers.
3. The UI shows detections and recommended skills.
4. Generators write agent instruction files.
5. Installers copy skills or generate local fallback skills.

## Modules

- `skillmint/cli.py` — command entrypoint and orchestration.
- `skillmint/detectors.py` — stack detection logic.
- `skillmint/registry.py` — built-in stack definitions and trusted skill sources.
- `skillmint/generators.py` — AGENTS.md, CLAUDE.md, Cursor, and Copilot outputs.
- `skillmint/installer.py` — skill installation.
- `skillmint/ui.py` — interactive prompts and output.
- `skillmint/models.py` — shared dataclasses.
