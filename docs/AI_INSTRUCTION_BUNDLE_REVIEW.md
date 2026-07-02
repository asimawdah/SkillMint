# AI Instruction Bundle Review Policy

Use this policy before generated SkillMint instruction bundles are trusted by CI, setup scripts, or AI coding agents.

## Review goals

Generated instruction bundles are meant to speed up project onboarding, but they should not become an unchecked automation input. Every bundle should be reviewed for project fit, validation coverage, path safety, and manifest integrity before broad edits are delegated to another tool.

## Required gates

1. **Detection review**
   - Read `STACKS.md` and confirm every selected stack matches real project files.
   - If `MANIFEST.json` sets `summary.requires_detection_review` to `true`, manually confirm each item in `summary.low_confidence_stack_ids` before automation uses the bundle.
   - Remove or regenerate stale stack selections before using the bundle for code changes.

2. **Validation review**
   - Read `COMMANDS.md` and confirm the listed commands are safe for the current repository.
   - If `summary.requires_validation_review` is `true`, add or document validation commands before broad scripted edits.
   - Prefer running `skillmint --verify-instructions` and at least one project-level test/check command before committing generated bundle changes.

3. **Integrity review**
   - Verify `MANIFEST.json` uses the expected schema version documented in `docs/AI_INSTRUCTION_BUNDLE.md`.
   - Confirm `integrity.hash_algorithm` is `sha256`.
   - Confirm every `file_hashes` value is a lowercase 64-character SHA-256 hex digest.
   - Run `skillmint --verify-instructions` after copying, editing, or regenerating bundle files.

4. **Path safety review**
   - Keep instruction bundles inside the selected project root.
   - Prefer direct project-relative folders such as `.ai/instructions` or `docs/project-ai`.
   - Do not use ambiguous `.` / `..` output segments, project-root output targets, existing files as output folders, or paths containing control characters.

5. **Automation consumption review**
   - Treat `MANIFEST.json` as the machine entrypoint and `README.md` as the human entrypoint.
   - Scripts should read `entrypoints` and `files_by_role` instead of guessing filenames.
   - Stop automation when verification fails, when hashes do not match, or when low-confidence detections require manual review.

## Safe review command sequence

```bash
skillmint --dry-run
skillmint --yes
skillmint --verify-instructions
cat .ai/instructions/NEXT_STEPS.md
```

For a custom bundle folder:

```bash
skillmint --yes --instructions-dir docs/project-ai
skillmint --verify-instructions --instructions-dir docs/project-ai
```

## Pull request checklist

Use this checklist when a PR adds or updates generated instruction bundles:

- [ ] `STACKS.md` matches the real project structure.
- [ ] `COMMANDS.md` contains only safe, expected project commands.
- [ ] `NEXT_STEPS.md` documents detection or validation gaps when present.
- [ ] `MANIFEST.json` schema, entrypoints, role paths, summary metadata, and hashes are valid.
- [ ] `skillmint --verify-instructions` passes for the committed bundle.
- [ ] The PR description mentions whether detection or validation review is required.
