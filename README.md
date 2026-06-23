# SkillForge

**One command to make your codebase AI-agent ready.**

SkillForge detects your project stack and installs the right AI skills, rules, and instruction files for coding agents.

It is designed for Claude Code, Cursor, GitHub Copilot, Codex, Hermes, Cline, Roo Code, Aider, and similar coding agents.

## Why

AI coding agents work better when a repository tells them:

- What stack the project uses.
- Which commands install, run, test, and build the project.
- Which files and directories should not be edited.
- Which framework conventions should be followed.
- Which agent instruction files should exist in the repo.

SkillForge creates that setup with one command.

## Install

From source:

```bash
python -m pip install -e .
```

Later, when published:

```bash
pip install skillforge
```

## Usage

Inside any project, run:

```bash
skillforge
```

SkillForge will:

1. Scan the current project.
2. Detect the stack.
3. Show recommended AI skills.
4. Ask what you want to install.
5. Generate agent instruction files.
6. Copy or generate skills into the project.

## Generated files

SkillForge can create:

```text
AGENTS.md
CLAUDE.md
.cursor/rules/project.mdc
.github/copilot-instructions.md
.ai/skills/<stack>/SKILL.md
```

For Flutter projects, SkillForge can install the official Flutter agent skills from:

```text
https://github.com/flutter/skills
```

External downloads require confirmation.

## Supported stacks in v0.1

- Flutter / Dart
- React / Vite / Node
- Laravel / PHP
- Python / FastAPI / Django
- Go
- Docker
- GitHub Actions

## Safety

SkillForge does not download external skills silently in the normal interactive flow. It shows the source URL and asks before installing external skills.

In non-interactive mode, external downloads are disabled by default unless `--yes` is used.

If an external download fails, SkillForge creates a local skill reference file instead.

## Development

```bash
python -m pip install -e .[dev]
pytest -q
python -m skillforge --version
```

## Design principle

The primary user experience should remain one command:

```bash
skillforge
```

Additional flags may exist for automation, but users should not need to remember a list of commands.

## License

MIT
