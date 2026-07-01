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

Absolute paths are accepted only when they resolve inside the selected project root. The generated `MANIFEST.json` still records `bundle_dir`, `files`, `entrypoints`, and `files_by_role` as project-relative paths so generated metadata is portable across machines and CI workspaces.

For predictable dry-runs and portable manifests, custom instruction directories must use direct folder names only. SkillMint rejects `.` and `..` path segments, project-root escapes, the project root itself, existing files used as output folders, and control characters before planning or writing bundle files. Prefer a simple project-relative folder such as `docs/project-ai` or `.ai/instructions`.

Verify an existing bundle before CI or automation consumes it:

```bash
skillmint --verify-instructions
```

Verify a custom bundle folder:

```bash
skillmint --root /path/to/project --instructions-dir docs/project-ai --verify-instructions
```

`--verify-instructions` checks that `MANIFEST.json` exists, parses as JSON, matches the expected schema and bundle directory, lists the expected generated files, uses the expected hash algorithm, and that every hashed Markdown file still matches its SHA-256 digest. It exits `0` when the bundle is valid and `1` when the bundle is missing, incomplete, stale, or changed after generation.

Overwrite an existing generated bundle intentionally:

```bash
skillmint --yes --force
```

## What each file contains

- `README.md`: short overview and reading order.
- `STACKS.md`: detected stacks, confidence, and evidence.
- `COMMANDS.md`: install, run, test, and build commands from the detected stack definitions.
- `SAFE_CHANGES.md`: focused editing rules and paths that should normally be avoided.
- `NEXT_STEPS.md`: review checklist, validation gaps, and per-stack validation hints for the next safe edit.
- `MANIFEST.json`: machine-readable metadata for automation, including schema version, generated file paths, SHA-256 file hashes, integrity metadata, role paths, summary metadata, detected stack IDs, commands, directories, avoid rules, preferred validation command per stack, and validation-gap flags.

## Review flow

After generation, review the bundle in this order:

1. Read `MANIFEST.json` if the bundle is being consumed programmatically.
2. Confirm `STACKS.md` matches the real project.
3. Copy the relevant command from `COMMANDS.md` before changing code.
4. Check `SAFE_CHANGES.md` for conventions and paths to avoid.
5. Use `NEXT_STEPS.md` as the short checklist for the next change.
6. If `requires_validation_review` is `true`, add or document validation commands before broad scripted use.
7. If automation consumes generated files, check `integrity.hash_algorithm`, `integrity.hashed_file_count`, and `integrity.expected_file_count` before trusting cached bundle output.
8. Run `skillmint --verify-instructions` as a lightweight regression check after generated files are committed or copied between workspaces.

## Manifest schema

The manifest is intentionally small and stable enough for scripts to parse:

```json
{
  "schema_version": "1.5",
  "bundle_dir": ".ai/instructions",
  "entrypoints": {
    "human": ".ai/instructions/README.md",
    "machine": ".ai/instructions/MANIFEST.json"
  },
  "files": [".ai/instructions/README.md"],
  "file_hashes": {
    ".ai/instructions/README.md": "<sha256>"
  },
  "files_by_role": {
    "human_entrypoint": ".ai/instructions/README.md",
    "stack_evidence": ".ai/instructions/STACKS.md",
    "commands": ".ai/instructions/COMMANDS.md",
    "safe_change_rules": ".ai/instructions/SAFE_CHANGES.md",
    "next_steps": ".ai/instructions/NEXT_STEPS.md",
    "machine_manifest": ".ai/instructions/MANIFEST.json"
  },
  "integrity": {
    "hash_algorithm": "sha256",
    "hashed_file_count": 5,
    "manifest_included_in_hashes": false,
    "expected_file_count": 6
  },
  "summary": {
    "stack_count": 1,
    "stack_ids": ["python"],
    "validation_commands": ["pytest"],
    "has_validation_commands": true,
    "missing_validation_stack_ids": [],
    "requires_validation_review": false
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

The `missing_validation_stack_ids` and `requires_validation_review` fields make validation gaps explicit. They are useful for CI and repository setup scripts that should pause for manual review when a detected stack has no known validation command.

The `file_hashes` block records SHA-256 hashes for the generated human-readable bundle files. Automation can use these hashes to detect manual edits, stale generated output, or accidental partial copies without parsing every Markdown file first. The manifest itself is not included in `file_hashes` so the hash list remains deterministic and easy to verify.

The `integrity` block records the hash algorithm, the number of hashed Markdown files, whether the manifest hashes itself, and the expected number of generated bundle files. Use this for lightweight CI checks that need to detect partial bundle output or unexpected schema changes before reading every Markdown file.

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

When a detected stack has no known validation command, `NEXT_STEPS.md` also includes a `Validation gaps` section listing the stack IDs that need manual review.

The bundle is generated in addition to the existing root instruction files such as `AGENTS.md`, `CLAUDE.md`, Cursor rules, and Copilot instructions.