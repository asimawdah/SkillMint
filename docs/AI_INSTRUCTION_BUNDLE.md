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
- `MANIFEST.json`: machine-readable metadata for automation, including schema version, generated file paths, role paths, summary metadata, detected stack IDs, commands, directories, avoid rules, and the preferred validation command per stack.

## Review flow

After generation, review the bundle in this order:

1. Read `MANIFEST.json` if the bundle is being consumed programmatically.
2. Confirm `STACKS.md` matches the real project.
3. Copy the relevant command from `COMMANDS.md` before changing code.
4. Check `SAFE_CHANGES.md` for conventions and paths to avoid.
5. Use `NEXT_STEPS.md` as the short checklist for the next change.

## Manifest schema

The manifest is intentionally small and stable enough for scripts to parse:

```json
{
  "schema_version": "1.2",
  "bundle_dir": ".ai/instructions",
  "entrypoints": {
    "human": ".ai/instructions/README.md",
    "machine": ".ai/instructions/MANIFEST.json"
  },
  "files": [".ai/instructions/README.md"],
  "files_by_role": {
    "human_entrypoint": ".ai/instructions/README.md",
    "stack_evidence": ".ai/instructions/STACKS.md",
    "commands": ".ai/instructions/COMMANDS.md",
    "safe_change_rules": ".ai/instructions/SAFE_CHANGES.md",
    "next_steps": ".ai/instructions/NEXT_STEPS.md",
    "machine_manifest": ".ai/instructions/MANIFEST.json"
  },
  "summary": {
    "stack_count": 1,
    "stack_ids": ["python"],
    "validation_commands": ["pytest"],
    "has_validation_commands": true
  },
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

The top-level `summary` block is designed for quick automation checks so scripts do not need to scan every stack object just to know which stacks were selected or which validation commands should run. Use `entrypoints` and `files_by_role` when tooling needs a stable path for a specific purpose instead of guessing filenames.

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