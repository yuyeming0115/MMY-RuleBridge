from __future__ import annotations

from pathlib import Path
from typing import Any

from .adapters import list_targets
from .doctor import doctor_source
from .generator import render_files
from .models import Diagnostic, GeneratedFile, SourceContext
from .pack import list_packs
from .source import load_source
from .validator import has_errors, validate_source, validate_targets
from .writer import WriteResult, diff_for_file, write_files


def load_project(root: Path | str) -> SourceContext:
    return load_source(root)


def inspect_project(root: Path | str, target: str | None = None) -> dict[str, Any]:
    source = load_source(root)
    files: list[GeneratedFile] = []
    diagnostics = [*source.diagnostics, *validate_targets(source, target)]
    if not has_errors(diagnostics):
        files = render_files(source, target)
        diagnostics = validate_source(source, target, files)
    packs, pack_diagnostics = list_packs(source.root)
    diagnostics.extend(pack_diagnostics)
    return {
        "source": source,
        "targets": list_targets(),
        "packs": packs,
        "files": files,
        "diagnostics": diagnostics,
    }


def preview_diff(
    root: Path | str,
    target: str | None = None,
    *,
    force: bool = False,
    insert_managed_block: bool = False,
) -> tuple[list[Diagnostic], list[tuple[GeneratedFile, str]]]:
    source = load_source(root)
    diagnostics = [*source.diagnostics, *validate_targets(source, target)]
    if has_errors(diagnostics):
        return diagnostics, []
    files = render_files(source, target)
    diagnostics = validate_source(source, target, files)
    if has_errors(diagnostics):
        return diagnostics, []
    return diagnostics, [
        (file, diff_for_file(source.root, file, force=force, insert_managed_block=insert_managed_block))
        for file in files
    ]


def sync_project(
    root: Path | str,
    target: str | None = None,
    *,
    dry_run: bool = False,
    force: bool = False,
    insert_managed_block: bool = False,
) -> tuple[list[Diagnostic], list[WriteResult]]:
    source = load_source(root)
    diagnostics = [*source.diagnostics, *validate_targets(source, target)]
    if has_errors(diagnostics):
        return diagnostics, []
    files = render_files(source, target)
    diagnostics = validate_source(source, target, files)
    if has_errors(diagnostics):
        return diagnostics, []
    return diagnostics, write_files(source.root, files, dry_run=dry_run, force=force, insert_managed_block=insert_managed_block)


def doctor_project(root: Path | str, target: str | None = None) -> list[Diagnostic]:
    return doctor_source(load_source(root), target)
