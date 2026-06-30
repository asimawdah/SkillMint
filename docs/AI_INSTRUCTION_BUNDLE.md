# AI Instruction Bundle

SkillMint can now write a compact instruction bundle into one clear folder:

```text
.ai/instructions/
├── README.md
├── STACKS.md
├── COMMANDS.md
├── SAFE_CHANGES.md
├── NEXT_STEPS.md
└── MANIFEST.json
```

## Usage

Preview the files first:

```bash
skillmint --dry-run
```

Generate files with the default output folder:

```bash
skillmint --yes
```

Choose a different folder:

```bash
skillmint --yes --instructions-dir docs/project-ai
```

Overwrite an existing generated bundle intentionally:

```bash
skillmint --yes --force
```

## What each file contains

- `README.md`: short overview and reading order.
- `STACKS.md`: detected stacks, confidence, and evidence.
- `COMMANDS.md`: install, run, test, and build commands from the detected stack definitions.
- `SAFE_CHANGES.md`: focused editing rules and paths that should normally be avoided.
- `NEXT_STEPS.md`: review checklist and per-stack validation hints for the next safe edit.
- `MANIFEST.json`: machine-readable metadata for AI agents and automation tools, including schema version, generated file paths, detected stack IDs, commands, directories, avoid rules, and the preferred validation command per stack.

## Review flow

After generation, review the bundle in this order:

1. Read `MANIFEST.json` if the bundle is being consumed by an automation or AI agent.
2. Confirm `STACKS.md` matches the real project.
3. Copy the relevant command from `COMMANDS.md` before changing code.
4. Check `SAFE_CHANGES.md` for conventions and paths to avoid.
5. Use `NEXT_STEPS.md` as the short checklist for the next change.

## Manifest schema

The manifest is intentionally small and stable enough for scripts to parse:

```json
{
  "schema_version": "1.0",
  "bundle_dir": ".ai/instructions",
  "files": [".ai/instructions/README.md"],
  "stacks": [
    {
      "id": "python",
      "name": "Python",
      "confidence": 70,
      "reasons": ["found Python packaging or dependency file"],
      "commands": {"test": "pytest"},
      "directories": ["src", "tests"],
      "avoid": [".venv", "__pycache__"],
      "validation_command": "pytest"
    }
  ]
}
```

Use `schema_version` before building downstream automation around the manifest.

## Example output

For a Flutter + Python + Docker project, SkillMint may create:

```markdown
# Detected Stacks

## Flutter / Dart

Confidence: 95%

- found Flutter pubspec.yaml

## Python

Confidence: 70%

- found Python packaging or dependency file

## Docker

Confidence: 80%

- detected Docker files
```

`NEXT_STEPS.md` may include:

```markdown
# Next Steps

1. Confirm detected stacks in STACKS.md.
2. Run relevant commands from COMMANDS.md.
3. Follow SAFE_CHANGES.md before editing.
4. Refresh this folder when project structure changes.
```

The bundle is generated in addition to the existing root instruction files such as `AGENTS.md`, `CLAUDE.md`, Cursor rules, and Copilot instructions.
