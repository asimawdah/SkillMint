# SkillMint

**One command to make your codebase AI-agent ready.**

SkillMint detects your project stack and installs the right AI skills, rules, and instruction files for coding agents.

It is designed for Claude Code, Cursor, GitHub Copilot, Codex, Hermes, Cline, Roo Code, Aider, and similar coding agents.

## Why

AI coding agents work better when a repository tells them:

- What stack the project uses.
- Which commands install, run, test, and build the project.
- Which files and directories should not be edited.
- Which framework conventions should be followed.
- Which agent instruction files should exist in the repo.

SkillMint creates that setup with one command.

## Install

From source:

```bash
python -m pip install -e .
```

Later, when published:

```bash
pip install skillmint
```

## Usage

Inside any project, run:

```bash
skillmint
```

SkillMint will:

1. Scan the current project.
2. Detect the stack.
3. Show recommended AI skills.
4. Ask what you want to install.
5. Generate agent instruction files.
6. Copy or generate skills into the project.

## Generated files

SkillMint can create:

```text
AGENTS.md
CLAUDE.md
.cursor/rules/project.mdc
.github/copilot-instructions.md
.ai/skills/<stack>/SKILL.md
```

For Flutter projects, SkillMint can install the official Flutter agent skills from:

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
