# SkillMint

**Make any codebase AI-agent ready with one command.**

SkillMint is a lightweight Python CLI that detects your project stack and installs practical AI skills, rules, and instruction files for coding agents.

It helps Claude Code, Cursor, GitHub Copilot, Codex, Hermes, Cline, Roo Code, Aider, and similar AI coding agents understand your repository before they edit it.

## Why SkillMint?

AI coding agents work better when your repository clearly explains:

- What stack and framework the project uses.
- Which commands install, run, test, and build the project.
- Which files and directories should not be edited.
- Which framework conventions should be followed.
- Which instruction files should exist for different AI tools.

SkillMint creates that setup automatically.

## Install

SkillMint is available on PyPI:

```bash
pip install skillmint
```

Verify the installation:

```bash
skillmint --version
```

## Quick start

Run SkillMint inside any project directory:

```bash
cd your-project
skillmint
```

SkillMint will:

1. Scan the current project.
2. Detect the stack and framework.
3. Show recommended AI skills.
4. Ask what you want to install.
5. Generate AI instruction files.
6. Copy or generate skills into the project.

For non-interactive usage:

```bash
skillmint --yes
```

To avoid downloading external skills and only generate local skills:

```bash
skillmint --no-external
```

To scan another directory:

```bash
skillmint --root /path/to/project
```

## Generated files

Depending on your project, SkillMint can generate:

```text
AGENTS.md
CLAUDE.md
.cursor/rules/project.mdc
.github/copilot-instructions.md
.ai/skills/<stack>/SKILL.md
```

These files give AI coding agents clear project-specific context and safer editing rules.

## Supported stacks

SkillMint currently supports detection and skill generation for:

- Flutter / Dart
- React
- Node.js / JavaScript / TypeScript
- Next.js
- Vue
- Nuxt
- Svelte / SvelteKit
- Angular
- Python
- FastAPI
- Django
- Flask
- Laravel / PHP
- Go
- Rust
- Docker
- GitHub Actions

## Trusted external skills

For supported ecosystems, SkillMint can suggest trusted external skill sources, such as:

- Flutter official skills: `https://github.com/flutter/skills`
- Dart official skills: `https://github.com/dart-lang/skills`

External downloads require confirmation. SkillMint does not silently download external skills in the normal interactive flow.

## Example

Inside a React project:

```bash
skillmint
```

SkillMint may generate:

```text
AGENTS.md
CLAUDE.md
.cursor/rules/project.mdc
.github/copilot-instructions.md
.ai/skills/react/SKILL.md
```

The generated instructions include common commands, stack-specific rules, files to avoid, and guidance for AI-assisted edits.

## Development

Clone the repository:

```bash
git clone https://github.com/asimawdah/SkillMint.git
cd SkillMint
```

Install locally with development dependencies:

```bash
python -m pip install -e .[dev]
```

Run tests:

```bash
pytest -q
```

Run the CLI locally:

```bash
python -m skillmint --version
python -m skillmint --root .
```

## Project goals

SkillMint is designed to stay:

- Simple: one command should be enough for the main flow.
- Lightweight: no heavy runtime dependencies.
- Safe: clear confirmation before external downloads.
- Practical: generated files should be readable and easy to review.
- Agent-friendly: useful for modern AI coding workflows.

## License

MIT
