from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field


class Severity(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class Diagnostic(BaseModel):
    severity: Severity
    message: str
    path: Path | None = None

    @property
    def is_error(self) -> bool:
        return self.severity == Severity.ERROR


class ProjectConfig(BaseModel):
    name: str = "RuleBridge Project"
    type: str = "ai-agent-config"


class RulesConfig(BaseModel):
    include: list[str] = Field(default_factory=list)


class RuleBridgeConfig(BaseModel):
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    rules: RulesConfig = Field(default_factory=RulesConfig)
    targets: list[str] = Field(default_factory=lambda: ["codex", "claude", "cursor", "generic"])
    profile: str | None = None


class RuleDocument(BaseModel):
    name: str
    title: str
    path: Path
    content: str
    source: Literal["project", "pack"] = "project"
    pack_name: str | None = None


class SkillDocument(BaseModel):
    name: str
    path: Path
    content: str
    source: Literal["project", "pack"] = "project"
    pack_name: str | None = None


class CommandDocument(BaseModel):
    name: str
    path: Path
    content: str
    source: Literal["project", "pack"] = "project"
    pack_name: str | None = None


class HookSpec(BaseModel):
    name: str
    event: str
    path: Path
    steps: list[dict[str, Any]] = Field(default_factory=list)
    targets: list[str] = Field(default_factory=list)
    source: Literal["project", "pack"] = "project"
    pack_name: str | None = None


class PackConfig(BaseModel):
    name: str
    title: str | None = None
    description: str | None = None
    enabled: bool = False
    priority: str | None = None
    targets: list[str] = Field(default_factory=list)
    source: dict[str, Any] = Field(default_factory=dict)
    license: str | None = None


class SourceContext(BaseModel):
    root: Path
    ai_dir: Path
    config: RuleBridgeConfig
    rules: list[RuleDocument] = Field(default_factory=list)
    skills: list[SkillDocument] = Field(default_factory=list)
    commands: list[CommandDocument] = Field(default_factory=list)
    hooks: list[HookSpec] = Field(default_factory=list)
    packs: list[PackConfig] = Field(default_factory=list)
    diagnostics: list[Diagnostic] = Field(default_factory=list)


class GeneratedFile(BaseModel):
    path: Path
    content: str
    managed: bool = True


class RenderContext(BaseModel):
    source: SourceContext
    targets: list[str]
