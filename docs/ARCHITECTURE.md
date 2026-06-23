# Architecture

SkillForge is intentionally small and dependency-light.

## Flow

1. `skillforge` starts the CLI wizard.
2. Detectors inspect the project root for stack markers.
3. The UI shows detections and recommended skills.
4. Generators write agent instruction files.
5. Installers copy external skills or generate local fallback skills.

## Modules

- `skillforge/cli.py` — command entrypoint and orchestration.
- `skillforge/detectors.py` — stack detection logic.
- `skillforge/registry.py` — built-in stack definitions and trusted external skills.
- `skillforge/generators.py` — AGENTS.md, CLAUDE.md, Cursor, and Copilot outputs.
- `skillforge/installer.py` — local and external skill installation.
- `skillforge/ui.py` — interactive prompts and output.
- `skillforge/models.py` — shared dataclasses.

## Safety model

External skill downloads are never silent in normal interactive use. In non-interactive mode, external downloads default to disabled unless the user passes `--yes`.
