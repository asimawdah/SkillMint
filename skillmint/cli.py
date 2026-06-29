from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional

from . import __version__
from .detectors import detect
from .generators import generate_all, preview_generated_skills
from .installer import install_skills
from .instruction_bundle import DEFAULT_INSTRUCTIONS_DIR, planned_instruction_bundle_outputs, validate_instruction_bundle_dir, write_instruction_bundle
from .ui import UI


INSTRUCTION_FILE_PATHS = [
    "AGENTS.md",
    "CLAUDE.md",
    ".cursor/rules/project.mdc",
    ".github/copilot-instructions.md",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skillmint",
        description="One command to prepare project instruction files.",
    )
    parser.add_argument("--version", action="store_true", help="Show SkillMint version and exit.")
    parser.add_argument("--yes", "-y", action="store_true", help="Accept defaults without prompting.")
    parser.add_argument("--no-external", action="store_true", help="Do not download external skills; generate local skills instead.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing SkillMint-generated files instead of skipping them.")
    parser.add_argument("--dry-run", action="store_true", help="Preview planned SkillMint changes without writing files.")
    parser.add_argument("--root", default=".", help="Project directory. Defaults to current directory.")
    parser.add_argument("--instructions-dir", default=DEFAULT_INSTRUCTIONS_DIR, help="Folder for the generated instruction bundle.")
    return parser


def planned_skill_outputs(detections, selected_stack_ids: List[str], *, no_external: bool) -> List[str]:
    selected_ids = set(selected_stack_ids)
    selected = [d.stack for d in detections if d.id in selected_ids]
    planned: List[str] = []
    for stack in selected:
        local_path = f".ai/skills/{stack.id}/SKILL.md"
        if stack.external_skills and not no_external:
            for external in stack.external_skills:
                planned.append(f"{external.name} -> {external.install_path} (external, requires confirmation in a real run)")
            planned.append(f"{stack.name} local fallback -> {local_path}")
        else:
            planned.append(local_path)
    return planned


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(__version__)
        return 0

    root = Path(args.root).resolve()
    ui = UI(assume_yes=args.yes or args.dry_run)
    ui.print_header()

    if not root.exists() or not root.is_dir():
        print(f"Project root does not exist or is not a directory: {root}")
        return 2

    try:
        validate_instruction_bundle_dir(root, args.instructions_dir)
    except ValueError as exc:
        print(f"Invalid --instructions-dir: {exc}")
        return 2

    detections = detect(root)
    ui.show_detections(detections)
    if not detections:
        print("Supported markers include pubspec.yaml, package.json, composer.json, go.mod, Dockerfile, and GitHub workflows.")
        return 1

    ui.show_recommended_skills(detections)
    selected_stack_ids = ui.choose_stacks(detections)
    if not selected_stack_ids:
        print("Nothing selected. No files were changed.")
        return 0

    ui.show_skill_previews(preview_generated_skills(detections, selected_stack_ids))

    if args.dry_run:
        print("\nDry run. No files were changed.\n")
        ui.summary("Would generate instruction files", INSTRUCTION_FILE_PATHS)
        ui.summary("Would generate instruction bundle", planned_instruction_bundle_outputs(args.instructions_dir))
        ui.summary("Would install skills", planned_skill_outputs(detections, selected_stack_ids, no_external=args.no_external))
        print("Run without --dry-run to write these files.")
        return 0

    should_generate = ui.confirm("Generate instruction files?", default=True)
    install_external = False
    has_external = any(d.stack.external_skills for d in detections if d.id in selected_stack_ids)
    if has_external and not args.no_external:
        install_external = ui.confirm(
            "Download external trusted skills when available?",
            default=True,
            non_interactive_default=False,
        )

    written_files = []
    written_bundle_files = []
    skipped_generated: List[str] = []
    if should_generate:
        written_files = generate_all(
            root,
            detections,
            selected_stack_ids,
            overwrite=args.force,
            skipped=skipped_generated,
        )
        written_bundle_files = write_instruction_bundle(
            root,
            detections,
            selected_stack_ids,
            output_dir=args.instructions_dir,
            overwrite=args.force,
            skipped=skipped_generated,
        )

    install_result = install_skills(
        root,
        detections,
        selected_stack_ids,
        install_external=install_external,
        overwrite=args.force,
    )

    print("\nDone.\n")
    ui.summary("Generated instruction files", [str(p.relative_to(root)) for p in written_files])
    ui.summary("Generated instruction bundle", [str(p.relative_to(root)) for p in written_bundle_files])
    ui.summary("Installed skills", install_result.installed)
    ui.summary("Skipped", skipped_generated + install_result.skipped)
    ui.summary("Fallbacks / warnings", install_result.failed)
    print("Your project instruction setup is ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
