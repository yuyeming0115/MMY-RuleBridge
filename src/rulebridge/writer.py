from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path

from .models import GeneratedFile
from .validator import path_inside

START = "<!-- rulebridge:start -->"
END = "<!-- rulebridge:end -->"


@dataclass(frozen=True)
class WriteResult:
    path: Path
    status: str
    message: str


def with_managed_block(content: str) -> str:
    return f"{START}\n{content.rstrip()}\n{END}\n"


def replace_managed_block(existing: str, content: str) -> str | None:
    start = existing.find(START)
    end = existing.find(END)
    if start == -1 or end == -1 or end < start:
        return None
    end += len(END)
    replacement = with_managed_block(content).rstrip()
    return existing[:start] + replacement + existing[end:]


def desired_file_content(existing: str | None, generated: GeneratedFile, *, force: bool = False, insert_managed_block: bool = False) -> tuple[str | None, str]:
    if existing is None:
        return (with_managed_block(generated.content) if generated.managed else generated.content, "create")

    if force:
        return (with_managed_block(generated.content) if generated.managed else generated.content, "overwrite")

    if generated.managed:
        replaced = replace_managed_block(existing, generated.content)
        if replaced is not None:
            return replaced, "update"
        if insert_managed_block:
            separator = "\n" if existing.endswith("\n") else "\n\n"
            return existing + separator + with_managed_block(generated.content), "insert"
        return None, "refuse"

    return None, "refuse"


def diff_for_file(root: Path, generated: GeneratedFile, *, force: bool = False, insert_managed_block: bool = False) -> str:
    full_path = root / generated.path
    existing = full_path.read_text(encoding="utf-8") if full_path.exists() else None
    desired, status = desired_file_content(existing, generated, force=force, insert_managed_block=insert_managed_block)
    if desired is None:
        return f"# {generated.path}: skipped ({status}; use --force or --insert-managed-block)\n"
    old = existing or ""
    return "".join(
        difflib.unified_diff(
            old.splitlines(keepends=True),
            desired.splitlines(keepends=True),
            fromfile=str(generated.path),
            tofile=str(generated.path),
        )
    )


def write_file(root: Path, generated: GeneratedFile, *, dry_run: bool = False, force: bool = False, insert_managed_block: bool = False) -> WriteResult:
    full_path = root / generated.path
    if not path_inside(root, full_path):
        return WriteResult(generated.path, "error", "path escapes project root")
    existing = full_path.read_text(encoding="utf-8") if full_path.exists() else None
    desired, status = desired_file_content(existing, generated, force=force, insert_managed_block=insert_managed_block)
    if desired is None:
        return WriteResult(generated.path, "skipped", "existing file has no managed block; use --force or --insert-managed-block")
    if dry_run:
        return WriteResult(generated.path, "dry-run", f"would {status}")
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(desired, encoding="utf-8", newline="\n")
    return WriteResult(generated.path, status, status)


def write_files(root: Path, files: list[GeneratedFile], *, dry_run: bool = False, force: bool = False, insert_managed_block: bool = False) -> list[WriteResult]:
    return [write_file(root, file, dry_run=dry_run, force=force, insert_managed_block=insert_managed_block) for file in files]
