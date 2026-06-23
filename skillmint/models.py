from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class ExternalSkill:
    id: str
    name: str
    url: str
    install_path: str
    trusted: bool = False
    subdirectory: str = ""


@dataclass(frozen=True)
class StackDefinition:
    id: str
    name: str
    commands: Dict[str, str] = field(default_factory=dict)
    rules: List[str] = field(default_factory=list)
    directories: List[str] = field(default_factory=list)
    avoid: List[str] = field(default_factory=list)
    external_skills: List[ExternalSkill] = field(default_factory=list)


@dataclass
class Detection:
    stack: StackDefinition
    confidence: int
    reasons: List[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        return self.stack.id

    @property
    def name(self) -> str:
        return self.stack.name
