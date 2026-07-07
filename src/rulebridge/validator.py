from __future__ import annotations

import re
from pathlib import Path

from .adapters import ADAPTERS
from .generator import resolve_targets
from .models import Diagnostic, GeneratedFile, Severity, SourceContext

SECRET_KEYWORDS = [
    "api_key",
    "apikey",
    "token",
    "secret",
    "password",
    "passwd",
    "cookie",
    "authorization",
    "private_key",
    "client_secret",
]

SENSITIVE_PATTERNS = [".env", ".pem", ".key", ".p12", ".pfx"]
SUPPORTED_HOOK_EVENTS = {"before_commit", "before_push"}
SECRET_FIELD_RE = re.compile(r"(?i)(key|token|secret|password|passwd|authorization)")


def contains_sensitive_assignment(content: str, keyword: str) -> bool:
    pattern = rf"(?im)^\s*[\"']?{re.escape(keyword)}[\"']?\s*[:=]"
    return re.search(pattern, content) is not None


def path_inside(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def validate_targets(source: SourceContext, target: str | None = None) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for name in resolve_targets(source, target):
        if name not in ADAPTERS:
            diagnostics.append(Diagnostic(severity=Severity.ERROR, message=f"Unsupported target: {name}"))
    return diagnostics


def validate_generated_paths(source: SourceContext, files: list[GeneratedFile]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for file in files:
        full_path = source.root / file.path
        if not path_inside(source.root, full_path):
            diagnostics.append(Diagnostic(severity=Severity.ERROR, message=f"Generated path escapes project root: {file.path}", path=full_path))
    return diagnostics


def scan_sensitive_content(source: SourceContext) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    documents = [*source.rules, *source.skills, *source.commands]
    for doc in documents:
        lowered_path = str(doc.path).lower()
        for pattern in SENSITIVE_PATTERNS:
            if lowered_path.endswith(pattern) or pattern in lowered_path:
                diagnostics.append(Diagnostic(severity=Severity.WARN, message=f"Sensitive-looking source path: {doc.path}", path=source.ai_dir / doc.path))
                break
        for keyword in SECRET_KEYWORDS:
            if contains_sensitive_assignment(doc.content, keyword):
                diagnostics.append(Diagnostic(severity=Severity.WARN, message=f"Sensitive-looking assignment for '{keyword}' found in {doc.path}", path=source.ai_dir / doc.path))
                break
    return diagnostics


def validate_hooks(source: SourceContext) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for hook in source.hooks:
        if hook.event not in SUPPORTED_HOOK_EVENTS:
            diagnostics.append(Diagnostic(severity=Severity.WARN, message=f"Unsupported hook event '{hook.event}' will not generate a Git hook", path=source.ai_dir / hook.path))
        if not hook.steps:
            diagnostics.append(Diagnostic(severity=Severity.WARN, message=f"Hook has no steps: {hook.path}", path=source.ai_dir / hook.path))
    return diagnostics


def validate_mcp_servers(source: SourceContext) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for server in source.mcp_servers:
        path = source.ai_dir / server.path
        if server.enabled and not server.command:
            diagnostics.append(Diagnostic(severity=Severity.ERROR, message=f"Enabled MCP server has no command: {server.name}", path=path))
        for key, value in server.env.items():
            if SECRET_FIELD_RE.search(key) and value and not value.startswith("${"):
                diagnostics.append(Diagnostic(severity=Severity.WARN, message=f"MCP env may contain inline secret: {server.name}.{key}", path=path))
        for item in [server.command, *server.args, *server.env.values()]:
            lowered = str(item).lower()
            if any(pattern in lowered for pattern in SENSITIVE_PATTERNS):
                diagnostics.append(Diagnostic(severity=Severity.WARN, message=f"MCP server references sensitive-looking path/value: {server.name}", path=path))
                break
    return diagnostics


def validate_source(source: SourceContext, target: str | None = None, files: list[GeneratedFile] | None = None) -> list[Diagnostic]:
    diagnostics = [*source.diagnostics]
    diagnostics.extend(validate_targets(source, target))
    diagnostics.extend(scan_sensitive_content(source))
    diagnostics.extend(validate_hooks(source))
    diagnostics.extend(validate_mcp_servers(source))
    if files is not None:
        diagnostics.extend(validate_generated_paths(source, files))
    return diagnostics


def has_errors(diagnostics: list[Diagnostic]) -> bool:
    return any(item.severity == Severity.ERROR for item in diagnostics)
