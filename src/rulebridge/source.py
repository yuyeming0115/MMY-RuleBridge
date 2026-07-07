from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import (
    CommandDocument,
    Diagnostic,
    PackConfig,
    RuleBridgeConfig,
    RuleDocument,
    Severity,
    SkillDocument,
    SourceContext,
)

CONFIG_DIR = ".ai-agent"
CONFIG_FILE = "rulebridge.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or {}


def title_from_markdown(path: Path, content: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or path.stem
    return path.stem.replace("-", " ").replace("_", " ").title()


def load_rule(path: Path, ai_dir: Path, source: str = "project", pack_name: str | None = None) -> RuleDocument:
    content = path.read_text(encoding="utf-8")
    rel = path.relative_to(ai_dir) if path.is_relative_to(ai_dir) else path
    return RuleDocument(
        name=path.stem,
        title=title_from_markdown(path, content),
        path=rel,
        content=content.strip() + "\n",
        source=source,  # type: ignore[arg-type]
        pack_name=pack_name,
    )


def load_skill(path: Path, ai_dir: Path, source: str = "project", pack_name: str | None = None) -> SkillDocument:
    content = path.read_text(encoding="utf-8")
    name = path.parent.name
    rel = path.relative_to(ai_dir) if path.is_relative_to(ai_dir) else path
    return SkillDocument(
        name=name,
        path=rel,
        content=content.strip() + "\n",
        source=source,  # type: ignore[arg-type]
        pack_name=pack_name,
    )


def load_command(path: Path, ai_dir: Path, source: str = "project", pack_name: str | None = None) -> CommandDocument:
    content = path.read_text(encoding="utf-8")
    rel = path.relative_to(ai_dir) if path.is_relative_to(ai_dir) else path
    return CommandDocument(
        name=path.stem,
        path=rel,
        content=content.strip() + "\n",
        source=source,  # type: ignore[arg-type]
        pack_name=pack_name,
    )


def load_project_rules(ai_dir: Path, config: RuleBridgeConfig, diagnostics: list[Diagnostic]) -> list[RuleDocument]:
    rules_dir = ai_dir / "rules"
    rules: list[RuleDocument] = []
    if config.rules.include:
        for item in config.rules.include:
            path = ai_dir / item
            if not path.exists():
                diagnostics.append(Diagnostic(severity=Severity.ERROR, message=f"Referenced rule does not exist: {item}", path=path))
                continue
            rules.append(load_rule(path, ai_dir))
        return rules

    if not rules_dir.exists():
        return rules
    for path in sorted(rules_dir.glob("*.md")):
        rules.append(load_rule(path, ai_dir))
    return rules


def load_project_skills(ai_dir: Path) -> list[SkillDocument]:
    skills_dir = ai_dir / "skills"
    if not skills_dir.exists():
        return []
    return [load_skill(path, ai_dir) for path in sorted(skills_dir.glob("*/SKILL.md"))]


def load_project_commands(ai_dir: Path) -> list[CommandDocument]:
    commands_dir = ai_dir / "commands"
    if not commands_dir.exists():
        return []
    return [load_command(path, ai_dir) for path in sorted(commands_dir.glob("*.md"))]


def load_packs(ai_dir: Path, diagnostics: list[Diagnostic]) -> tuple[list[PackConfig], list[RuleDocument], list[SkillDocument], list[CommandDocument]]:
    packs_dir = ai_dir / "packs"
    pack_configs: list[PackConfig] = []
    rules: list[RuleDocument] = []
    skills: list[SkillDocument] = []
    commands: list[CommandDocument] = []
    if not packs_dir.exists():
        return pack_configs, rules, skills, commands

    for pack_file in sorted(packs_dir.glob("*/pack.yaml")):
        try:
            pack = PackConfig.model_validate(load_yaml(pack_file))
        except Exception as exc:  # pragma: no cover - pydantic text varies
            diagnostics.append(Diagnostic(severity=Severity.ERROR, message=f"Invalid pack config: {exc}", path=pack_file))
            continue
        pack_configs.append(pack)
        if not pack.enabled:
            continue
        pack_dir = pack_file.parent
        for rule_path in sorted((pack_dir / "rules").glob("*.md")):
            rules.append(load_rule(rule_path, ai_dir, source="pack", pack_name=pack.name))
        for skill_path in sorted((pack_dir / "skills").glob("*/SKILL.md")):
            skills.append(load_skill(skill_path, ai_dir, source="pack", pack_name=pack.name))
        for command_path in sorted((pack_dir / "commands").glob("*.md")):
            commands.append(load_command(command_path, ai_dir, source="pack", pack_name=pack.name))
    return pack_configs, rules, skills, commands


def load_source(root: Path | str = ".") -> SourceContext:
    root_path = Path(root).resolve()
    ai_dir = root_path / CONFIG_DIR
    diagnostics: list[Diagnostic] = []
    config_path = ai_dir / CONFIG_FILE

    if config_path.exists():
        try:
            config = RuleBridgeConfig.model_validate(load_yaml(config_path))
        except Exception as exc:
            config = RuleBridgeConfig()
            diagnostics.append(Diagnostic(severity=Severity.ERROR, message=f"Invalid {CONFIG_DIR}/{CONFIG_FILE}: {exc}", path=config_path))
    else:
        config = RuleBridgeConfig()
        diagnostics.append(Diagnostic(severity=Severity.ERROR, message=f"Missing {CONFIG_DIR}/{CONFIG_FILE}", path=config_path))

    packs, pack_rules, pack_skills, pack_commands = load_packs(ai_dir, diagnostics)
    project_rules = load_project_rules(ai_dir, config, diagnostics)
    project_skills = load_project_skills(ai_dir)
    project_commands = load_project_commands(ai_dir)

    return SourceContext(
        root=root_path,
        ai_dir=ai_dir,
        config=config,
        rules=[*pack_rules, *project_rules],
        skills=[*pack_skills, *project_skills],
        commands=[*pack_commands, *project_commands],
        packs=packs,
        diagnostics=diagnostics,
    )
