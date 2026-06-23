# AI Agent Instructions

This repository contains SkillForge, a Python CLI that detects a codebase stack and installs AI-ready skills and instruction files.

## Product rule

The main user experience must stay one command:

```bash
skillforge
```

Do not turn the primary flow into many required commands. Advanced flags are allowed, but the default command should scan, show results, ask what to install, and write files.

## Development commands

```bash
python -m pip install -e .[dev]
pytest -q
python -m skillforge --version
```

## Code rules

- Keep the project dependency-light and offline-first.
- Do not download external skills without an explicit user confirmation or `--yes`.
- Prefer simple detectors based on well-known project files.
- Keep generated files readable and easy to review.
- Add tests when changing detection, generation, or installation behavior.
