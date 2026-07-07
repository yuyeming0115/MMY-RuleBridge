from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from .generator import render_files
from .models import Diagnostic, Severity, SourceContext
from .validator import has_errors, validate_source, validate_targets
from .writer import END, START

PRIVATE_PATH_RE = re.compile(r"(?i)([a-z]:\\\\|[a-z]:/|/users/|\\\\users\\\\|/home/)")


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def check_duplicate_rules(source: SourceContext) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    by_name: dict[str, list[str]] = defaultdict(list)
    by_body: dict[str, list[str]] = defaultdict(list)
    for rule in source.rules:
        by_name[rule.name].append(str(rule.path))
        normalized = normalize_text(rule.content)
        if normalized:
            by_body[normalized].append(str(rule.path))

    for name, paths in by_name.items():
        if len(paths) > 1:
            diagnostics.append(Diagnostic(severity=Severity.WARN, message=f"Duplicate rule name '{name}': {', '.join(paths)}"))
    for paths in by_body.values():
        if len(paths) > 1:
            diagnostics.append(Diagnostic(severity=Severity.WARN, message=f"Duplicate rule content: {', '.join(paths)}"))
    return diagnostics


def check_duplicate_skills(source: SourceContext) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    by_name: dict[str, list[str]] = defaultdict(list)
    for skill in source.skills:
        by_name[skill.name].append(str(skill.path))
    for name, paths in by_name.items():
        if len(paths) > 1:
            diagnostics.append(Diagnostic(severity=Severity.WARN, message=f"Duplicate skill name '{name}': {', '.join(paths)}"))
    return diagnostics


def check_duplicate_commands(source: SourceContext) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    by_name: dict[str, list[str]] = defaultdict(list)
    for command in source.commands:
        by_name[command.name].append(str(command.path))
    for name, paths in by_name.items():
        if len(paths) > 1:
            diagnostics.append(Diagnostic(severity=Severity.WARN, message=f"Duplicate command name '{name}': {', '.join(paths)}"))
    return diagnostics


def check_duplicate_hooks(source: SourceContext) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    by_event: dict[str, list[str]] = defaultdict(list)
    for hook in source.hooks:
        by_event[hook.event].append(str(hook.path))
    for event, paths in by_event.items():
        if len(paths) > 1:
            diagnostics.append(Diagnostic(severity=Severity.WARN, message=f"Duplicate hook event '{event}': {', '.join(paths)}"))
    return diagnostics


def check_duplicate_mcp_servers(source: SourceContext) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    by_name: dict[str, list[str]] = defaultdict(list)
    for server in source.mcp_servers:
        by_name[server.name].append(str(server.path))
    for name, paths in by_name.items():
        if len(paths) > 1:
            diagnostics.append(Diagnostic(severity=Severity.WARN, message=f"Duplicate MCP server name '{name}': {', '.join(paths)}"))
    return diagnostics


def check_private_paths(source: SourceContext) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for doc in [*source.rules, *source.skills, *source.commands]:
        if PRIVATE_PATH_RE.search(doc.content):
            diagnostics.append(Diagnostic(severity=Severity.WARN, message=f"Private-looking local path found in {doc.path}", path=source.ai_dir / doc.path))
    for hook in source.hooks:
        for step in hook.steps:
            if PRIVATE_PATH_RE.search(str(step.get("run", ""))) or PRIVATE_PATH_RE.search(str(step.get("message", ""))):
                diagnostics.append(Diagnostic(severity=Severity.WARN, message=f"Private-looking local path found in {hook.path}", path=source.ai_dir / hook.path))
                break
    for server in source.mcp_servers:
        for value in [server.command, *server.args, *server.env.values()]:
            if PRIVATE_PATH_RE.search(str(value)):
                diagnostics.append(Diagnostic(severity=Severity.WARN, message=f"Private-looking local path found in MCP server {server.name}", path=source.ai_dir / server.path))
                break
    return diagnostics


def check_pack_review_status(source: SourceContext) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for pack in source.packs:
        if pack.enabled and pack.license == "review-required":
            diagnostics.append(Diagnostic(severity=Severity.WARN, message=f"Enabled pack still requires license/source review: {pack.name}"))
    return diagnostics


def check_target_usefulness(source: SourceContext, target: str | None = None) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    targets = [target] if target else list(source.config.targets)
    if not source.rules:
        for name in targets:
            if name in {"codex", "claude", "cursor", "generic", "codebuddy", "workbuddy"}:
                diagnostics.append(Diagnostic(severity=Severity.INFO, message=f"Target '{name}' has no rules to render"))
    if not source.skills:
        for name in targets:
            if name in {"zcode", "trae", "codebuddy", "workbuddy"}:
                diagnostics.append(Diagnostic(severity=Severity.INFO, message=f"Target '{name}' has no skills to render"))
    if not source.commands:
        for name in targets:
            if name in {"zcode", "claude", "codex", "generic"}:
                diagnostics.append(Diagnostic(severity=Severity.INFO, message=f"Target '{name}' has no commands to render"))
    if not source.hooks:
        for name in targets:
            if name in {"git", "claude", "codex", "generic"}:
                diagnostics.append(Diagnostic(severity=Severity.INFO, message=f"Target '{name}' has no hooks to render"))
    if not source.mcp_servers:
        for name in targets:
            if name in {"mcp", "codebuddy", "workbuddy", "claude", "codex", "generic"}:
                diagnostics.append(Diagnostic(severity=Severity.INFO, message=f"Target '{name}' has no MCP servers to render"))
    return diagnostics


def check_existing_outputs(source: SourceContext, target: str | None = None) -> list[Diagnostic]:
    diagnostics = validate_targets(source, target)
    if has_errors(diagnostics):
        return diagnostics
    for file in render_files(source, target):
        full_path = source.root / file.path
        if not full_path.exists():
            continue
        text = full_path.read_text(encoding="utf-8")
        if file.managed:
            if START not in text or END not in text:
                diagnostics.append(Diagnostic(severity=Severity.WARN, message=f"Existing generated Markdown has no managed block: {file.path}", path=full_path))
        else:
            diagnostics.append(Diagnostic(severity=Severity.INFO, message=f"Existing generated artifact may require --force to replace: {file.path}", path=full_path))
    return diagnostics


def doctor_source(source: SourceContext, target: str | None = None) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    diagnostics.extend(validate_source(source, target))
    if has_errors(diagnostics):
        return diagnostics
    diagnostics.extend(check_duplicate_rules(source))
    diagnostics.extend(check_duplicate_skills(source))
    diagnostics.extend(check_duplicate_commands(source))
    diagnostics.extend(check_duplicate_hooks(source))
    diagnostics.extend(check_duplicate_mcp_servers(source))
    diagnostics.extend(check_private_paths(source))
    diagnostics.extend(check_pack_review_status(source))
    diagnostics.extend(check_target_usefulness(source, target))
    diagnostics.extend(check_existing_outputs(source, target))
    if not diagnostics:
        diagnostics.append(Diagnostic(severity=Severity.INFO, message="Doctor found no issues"))
    return diagnostics
