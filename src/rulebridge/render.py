from __future__ import annotations

from .models import CommandDocument, RuleDocument, SkillDocument, SourceContext


def render_rule_bundle(source: SourceContext, heading: str) -> str:
    parts = [f"# {heading}", "", f"Project: {source.config.project.name}", ""]
    if source.rules:
        parts.append("## Rules")
        parts.append("")
        for rule in source.rules:
            origin = f"pack:{rule.pack_name}" if rule.source == "pack" else "project"
            parts.extend([
                f"### {rule.title}",
                "",
                f"Source: `{rule.path}` ({origin})",
                "",
                rule.content.strip(),
                "",
            ])
    if source.skills:
        parts.append("## Skills")
        parts.append("")
        for skill in source.skills:
            origin = f"pack:{skill.pack_name}" if skill.source == "pack" else "project"
            parts.append(f"- `{skill.name}` from `{skill.path}` ({origin})")
        parts.append("")
    if source.commands:
        parts.append("## Commands")
        parts.append("")
        for command in source.commands:
            origin = f"pack:{command.pack_name}" if command.source == "pack" else "project"
            parts.append(f"- `/{command.name}` from `{command.path}` ({origin})")
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def cursor_frontmatter(rule: RuleDocument) -> str:
    desc = rule.title.replace('"', "'")
    return f"---\ndescription: \"{desc}\"\nalwaysApply: true\n---\n\n"


def codebuddy_frontmatter(rule: RuleDocument, provider: str) -> str:
    desc = rule.title.replace('"', "'")
    return (
        "---\n"
        f"description: \"{desc}\"\n"
        "alwaysApply: true\n"
        "enabled: true\n"
        f"provider: {provider}\n"
        "---\n\n"
    )


def skill_index(skills: list[SkillDocument]) -> str:
    if not skills:
        return ""
    lines = ["## Available Skills", ""]
    for skill in skills:
        lines.append(f"- `{skill.name}`: `{skill.path}`")
    return "\n".join(lines) + "\n"


def command_index(commands: list[CommandDocument]) -> str:
    if not commands:
        return ""
    lines = ["## Available Commands", ""]
    for command in commands:
        lines.append(f"- `/{command.name}`: `{command.path}`")
    return "\n".join(lines) + "\n"
