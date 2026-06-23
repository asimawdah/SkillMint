# Trusted External Skill Sources

SkillForge should only auto-suggest external skills from trusted or clearly labeled sources.

## Confirmed sources

### Flutter

- Source: https://github.com/flutter/skills
- Maintainer: Flutter organization
- Use for: Flutter projects
- Install path: `.ai/skills/flutter`

### Dart

- Source: https://github.com/dart-lang/skills
- Maintainer: Dart organization
- Use for: Dart projects and Flutter projects
- Install path: `.ai/skills/dart`

### Expo

- Source: https://github.com/expo/skills
- Maintainer: Expo organization
- Use for: Expo and React Native projects
- Install path: `.ai/skills/expo`
- Source subdirectory: `plugins/expo`

### OpenAI plugins

- Source: https://github.com/openai/plugins
- Maintainer: OpenAI organization
- Use for: Codex plugin and skill examples
- Candidate subdirectories:
  - `plugins/build-web-apps`
  - `plugins/build-ios-apps`
  - `plugins/build-macos-apps`

### GitHub Awesome Copilot

- Source: https://github.com/github/awesome-copilot
- Maintainer: GitHub organization
- Use for: Copilot instructions, prompts, and chatmode examples

## Policy

- Prefer first-party sources.
- Show the source URL before downloading.
- Require confirmation before cloning external skills.
- Copy only the needed subdirectory when possible.
- Generate a local fallback skill if download fails.
