from __future__ import annotations

import sys
from typing import Iterable, List, Optional

from .models import Detection


class UI:
    def __init__(self, *, assume_yes: bool = False) -> None:
        self.assume_yes = assume_yes
        self.interactive = sys.stdin.isatty()

    def print_header(self) -> None:
        print("\nSkillForge")
        print("One command to make your codebase AI-agent ready.\n")

    def show_detections(self, detections: List[Detection]) -> None:
        if not detections:
            print("No supported stack detected in this directory.\n")
            return
        print("Detected project stack:\n")
        for index, detection in enumerate(detections, start=1):
            reasons = "; ".join(detection.reasons)
            print(f"  {index}. {detection.name} ({detection.confidence}% confidence)")
            if reasons:
                print(f"     {reasons}")
        print()

    def show_recommended_skills(self, detections: List[Detection]) -> None:
        print("Recommended AI skills:\n")
        for detection in detections:
            stack = detection.stack
            if stack.external_skills:
                for external in stack.external_skills:
                    trust = "official/trusted" if external.trusted else "external"
                    print(f"  - {external.name} [{trust}]")
                    print(f"    Source: {external.url}")
                    print(f"    Install path: {external.install_path}")
            else:
                print(f"  - {stack.name} local skill")
                print(f"    Install path: .ai/skills/{stack.id}/SKILL.md")
        print()

    def confirm(self, question: str, default: bool = True, *, non_interactive_default: Optional[bool] = None) -> bool:
        suffix = "[Y/n]" if default else "[y/N]"
        if self.assume_yes:
            print(f"{question} {suffix}: yes")
            return True
        if not self.interactive:
            value = default if non_interactive_default is None else non_interactive_default
            print(f"{question} {suffix}: {'yes' if value else 'no'}")
            return value
        answer = input(f"{question} {suffix}: ").strip().lower()
        if not answer:
            return default
        return answer in {"y", "yes"}

    def choose_stacks(self, detections: List[Detection]) -> List[str]:
        if not detections:
            return []
        if self.assume_yes or not self.interactive:
            selected = [d.id for d in detections]
            print("Selected stacks: all detected stacks\n")
            return selected
        answer = input("Install skills for all detected stacks? [Y/n]: ").strip().lower()
        if answer in {"", "y", "yes"}:
            return [d.id for d in detections]

        print("Enter numbers separated by commas, for example: 1,3")
        selected_raw = input("Stacks to install: ").strip()
        indexes = set()
        for part in selected_raw.split(","):
            part = part.strip()
            if part.isdigit():
                indexes.add(int(part))
        selected = []
        for index, detection in enumerate(detections, start=1):
            if index in indexes:
                selected.append(detection.id)
        return selected

    def summary(self, title: str, items: Iterable[str]) -> None:
        items = list(items)
        if not items:
            return
        print(f"{title}:")
        for item in items:
            print(f"  - {item}")
        print()
