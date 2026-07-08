from __future__ import annotations

from pathlib import Path
from typing import Any

from .adapters import list_targets
from .initializer import init_source
from .pack import list_packs, pack_content_diff, set_pack_enabled
from .service import doctor_project, inspect_project, preview_diff, sync_project
from .validator import validate_source


def diagnostic_to_dict(item) -> dict[str, Any]:
    return {"severity": item.severity.value, "message": item.message, "path": str(item.path or "")}


def generated_file_to_dict(item) -> dict[str, Any]:
    return {"path": str(item.path), "managed": item.managed}


def write_result_to_dict(item) -> dict[str, Any]:
    return {"path": str(item.path), "status": item.status, "message": item.message}


def pack_to_dict(pack) -> dict[str, Any]:
    return {
        "name": pack.name,
        "title": pack.title or "",
        "description": pack.description or "",
        "enabled": pack.enabled,
        "targets": pack.targets,
        "license": pack.license or "",
    }


def source_to_dict(source) -> dict[str, Any]:
    return {
        "root": str(source.root),
        "project": source.config.project.model_dump(),
        "profile": source.config.profile or "",
        "targets": source.config.targets,
        "rules": [
            {"name": rule.name, "title": rule.title, "path": str(rule.path), "source": rule.source, "pack": rule.pack_name or ""}
            for rule in source.rules
        ],
        "skills": [
            {"name": skill.name, "path": str(skill.path), "source": skill.source, "pack": skill.pack_name or ""}
            for skill in source.skills
        ],
        "commands": [
            {"name": command.name, "path": str(command.path), "source": command.source, "pack": command.pack_name or ""}
            for command in source.commands
        ],
        "hooks": [
            {"name": hook.name, "event": hook.event, "path": str(hook.path), "steps": len(hook.steps), "targets": hook.targets, "source": hook.source, "pack": hook.pack_name or ""}
            for hook in source.hooks
        ],
        "mcpServers": [
            {"name": server.name, "enabled": server.enabled, "command": server.command, "targets": server.targets, "path": str(server.path), "source": server.source, "pack": server.pack_name or ""}
            for server in source.mcp_servers
        ],
    }


def inspect_api(root: str | Path, target: str | None = None) -> dict[str, Any]:
    info = inspect_project(root, target)
    return {
        "ok": True,
        "source": source_to_dict(info["source"]),
        "targets": info["targets"],
        "packs": [pack_to_dict(pack) for pack in info["packs"]],
        "files": [generated_file_to_dict(file) for file in info["files"]],
        "diagnostics": [diagnostic_to_dict(item) for item in info["diagnostics"]],
    }


def validate_api(root: str | Path, target: str | None = None) -> dict[str, Any]:
    info = inspect_project(root, target)
    diagnostics = validate_source(info["source"], target, info["files"])
    return {"ok": True, "diagnostics": [diagnostic_to_dict(item) for item in diagnostics]}


def doctor_api(root: str | Path, target: str | None = None) -> dict[str, Any]:
    return {"ok": True, "diagnostics": [diagnostic_to_dict(item) for item in doctor_project(root, target)]}


def diff_api(root: str | Path, target: str | None = None, *, force: bool = False, insert_managed_block: bool = False) -> dict[str, Any]:
    diagnostics, diffs = preview_diff(root, target, force=force, insert_managed_block=insert_managed_block)
    return {
        "ok": True,
        "diagnostics": [diagnostic_to_dict(item) for item in diagnostics],
        "diffs": [{"file": generated_file_to_dict(file), "diff": diff} for file, diff in diffs],
    }


def sync_api(root: str | Path, target: str | None = None, *, dry_run: bool = False, force: bool = False, insert_managed_block: bool = False) -> dict[str, Any]:
    diagnostics, results = sync_project(root, target, dry_run=dry_run, force=force, insert_managed_block=insert_managed_block)
    return {
        "ok": True,
        "diagnostics": [diagnostic_to_dict(item) for item in diagnostics],
        "results": [write_result_to_dict(item) for item in results],
    }


def init_api(root: str | Path, *, force: bool = False) -> dict[str, Any]:
    result = init_source(root, force=force)
    return {
        "ok": True,
        "written": result.written,
        "skipped": result.skipped,
        "files": [{"path": str(item.path), "status": item.status} for item in result.files],
    }


def targets_api() -> dict[str, Any]:
    return {"ok": True, "targets": list_targets()}


def packs_api(root: str | Path) -> dict[str, Any]:
    packs, diagnostics = list_packs(Path(root).resolve())
    return {"ok": True, "packs": [pack_to_dict(pack) for pack in packs], "diagnostics": [diagnostic_to_dict(item) for item in diagnostics]}


def pack_diff_api(root: str | Path, name: str) -> dict[str, Any]:
    diff, diagnostic = pack_content_diff(Path(root).resolve(), name)
    return {"ok": diagnostic is None or not diagnostic.is_error, "diff": diff, "diagnostics": [] if diagnostic is None else [diagnostic_to_dict(diagnostic)]}


def pack_set_api(root: str | Path, name: str, enabled: bool) -> dict[str, Any]:
    diagnostic = set_pack_enabled(Path(root).resolve(), name, enabled)
    return {"ok": not diagnostic.is_error, "diagnostics": [diagnostic_to_dict(diagnostic)]}
