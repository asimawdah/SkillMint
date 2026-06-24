from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional

from . import __version__
from .detectors import detect
from .generators import generate_all
from .installer import install_skills
from .ui import UI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skillmint",
        description="One command to make your codebase AI-agent ready.",
    )
    parser.add_argument("--version", action="store_true", help="Show SkillMint version and exit.")
    parser.add_argument("--yes", "-y", action="store_true", help="Accept defaults without prompting.")
    parser.add_argument("--no-external", action="store_true", help="Do not download external skills; generate local skills instead.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing SkillMint-generated files instead of skipping them.")
    parser.add_argument("--root", default=".", help="Project directory. Defaults to current directory.")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(__version__)
        return 0

    root = Path(args.root).resolve()
    ui = UI(assume_yes=args.yes)
    ui.print_header()

    if not root.exists() or not root.is_dir():
        print(f"Project root does not exist or is not a directory: {root}")
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

    should_generate = ui.confirm("Generate AI instruction files?", default=True)
    install_external = False
    has_external = any(d.stack.external_skills for d in detections if d.id in selected_stack_ids)
    if has_external and not args.no_external:
        install_external = ui.confirm(
            "Download external trusted skills when available?",
            default=True,
            non_interactive_default=False,
        )

    written_files = []
    skipped_generated: List[str] = []
    if should_generate:
        written_files = generate_all(
            root,
            detections,
            selected_stack_ids,
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
    ui.summary("Installed skills", install_result.installed)
    ui.summary("Skipped", skipped_generated + install_result.skipped)
    ui.summary("Fallbacks / warnings", install_result.failed)
    print("Your project is now AI-agent ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
