from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import (
    CommandDocument,
    Diagnostic,
    HookSpec,
    McpServerSpec,
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


def load_hook(path: Path, ai_dir: Path, source: str = "project", pack_name: str | None = None) -> HookSpec:
    data = load_yaml(path)
    rel = path.relative_to(ai_dir) if path.is_relative_to(ai_dir) else path
    event = data.get("event") or path.stem
    return HookSpec(
        name=path.stem,
        event=event,
        path=rel,
        steps=data.get("steps", []),
        targets=data.get("targets", []),
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


def load_project_hooks(ai_dir: Path, diagnostics: list[Diagnostic]) -> list[HookSpec]:
    hooks_dir = ai_dir / "hooks"
    if not hooks_dir.exists():
        return []
    hooks: list[HookSpec] = []
    for path in sorted([*hooks_dir.glob("*.yaml"), *hooks_dir.glob("*.yml")]):
        try:
            hooks.append(load_hook(path, ai_dir))
        except Exception as exc:
            diagnostics.append(Diagnostic(severity=Severity.ERROR, message=f"Invalid hook config: {exc}", path=path))
    return hooks


def load_mcp_servers(path: Path, ai_dir: Path, diagnostics: list[Diagnostic], source: str = "project", pack_name: str | None = None) -> list[McpServerSpec]:
    if not path.exists():
        return []
    data = load_yaml(path)
    raw_servers = data.get("servers", {})
    if not isinstance(raw_servers, dict):
        diagnostics.append(Diagnostic(severity=Severity.ERROR, message="MCP servers must be a mapping", path=path))
        return []
    rel = path.relative_to(ai_dir) if path.is_relative_to(ai_dir) else path
    servers: list[McpServerSpec] = []
    for name, raw in raw_servers.items():
        if not isinstance(raw, dict):
            diagnostics.append(Diagnostic(severity=Severity.ERROR, message=f"Invalid MCP server config: {name}", path=path))
            continue
        servers.append(
            McpServerSpec(
                name=str(name),
                command=str(raw.get("command", "")),
                args=[str(item) for item in raw.get("args", [])],
                env={str(key): str(value) for key, value in raw.get("env", {}).items()},
                enabled=bool(raw.get("enabled", True)),
                targets=[str(item) for item in raw.get("targets", [])],
                path=rel,
                source=source,  # type: ignore[arg-type]
                pack_name=pack_name,
            )
        )
    return servers


def load_project_mcp(ai_dir: Path, diagnostics: list[Diagnostic]) -> list[McpServerSpec]:
    return load_mcp_servers(ai_dir / "mcp" / "servers.yaml", ai_dir, diagnostics)


def load_packs(ai_dir: Path, diagnostics: list[Diagnostic]) -> tuple[list[PackConfig], list[RuleDocument], list[SkillDocument], list[CommandDocument], list[HookSpec], list[McpServerSpec]]:
    packs_dir = ai_dir / "packs"
    pack_configs: list[PackConfig] = []
    rules: list[RuleDocument] = []
    skills: list[SkillDocument] = []
    commands: list[CommandDocument] = []
    hooks: list[HookSpec] = []
    mcp_servers: list[McpServerSpec] = []
    if not packs_dir.exists():
        return pack_configs, rules, skills, commands, hooks, mcp_servers

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
        for hook_path in sorted([*(pack_dir / "hooks").glob("*.yaml"), *(pack_dir / "hooks").glob("*.yml")]):
            try:
                hooks.append(load_hook(hook_path, ai_dir, source="pack", pack_name=pack.name))
            except Exception as exc:
                diagnostics.append(Diagnostic(severity=Severity.ERROR, message=f"Invalid pack hook config: {exc}", path=hook_path))
        mcp_servers.extend(load_mcp_servers(pack_dir / "mcp" / "servers.yaml", ai_dir, diagnostics, source="pack", pack_name=pack.name))
    return pack_configs, rules, skills, commands, hooks, mcp_servers


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

    packs, pack_rules, pack_skills, pack_commands, pack_hooks, pack_mcp_servers = load_packs(ai_dir, diagnostics)
    project_rules = load_project_rules(ai_dir, config, diagnostics)
    project_skills = load_project_skills(ai_dir)
    project_commands = load_project_commands(ai_dir)
    project_hooks = load_project_hooks(ai_dir, diagnostics)
    project_mcp_servers = load_project_mcp(ai_dir, diagnostics)

    return SourceContext(
        root=root_path,
        ai_dir=ai_dir,
        config=config,
        rules=[*pack_rules, *project_rules],
        skills=[*pack_skills, *project_skills],
        commands=[*pack_commands, *project_commands],
        hooks=[*pack_hooks, *project_hooks],
        mcp_servers=[*pack_mcp_servers, *project_mcp_servers],
        packs=packs,
        diagnostics=diagnostics,
    )
