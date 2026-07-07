from __future__ import annotations

import re
from pathlib import Path

from .models import Diagnostic, PackConfig, Severity
from .source import CONFIG_DIR, load_yaml


def pack_file(root: Path, name: str) -> Path:
    return root / CONFIG_DIR / "packs" / name / "pack.yaml"


def list_pack_files(root: Path) -> list[Path]:
    packs_dir = root / CONFIG_DIR / "packs"
    if not packs_dir.exists():
        return []
    return sorted(packs_dir.glob("*/pack.yaml"))


def list_packs(root: Path) -> tuple[list[PackConfig], list[Diagnostic]]:
    packs: list[PackConfig] = []
    diagnostics: list[Diagnostic] = []
    for path in list_pack_files(root):
        try:
            packs.append(PackConfig.model_validate(load_yaml(path)))
        except Exception as exc:  # pragma: no cover - pydantic text varies
            diagnostics.append(Diagnostic(severity=Severity.ERROR, message=f"Invalid pack config: {exc}", path=path))
    return packs, diagnostics


def set_pack_enabled(root: Path, name: str, enabled: bool) -> Diagnostic:
    path = pack_file(root, name)
    if not path.exists():
        return Diagnostic(severity=Severity.ERROR, message=f"Pack does not exist: {name}", path=path)

    text = path.read_text(encoding="utf-8")
    replacement = f"enabled: {'true' if enabled else 'false'}"
    if re.search(r"(?m)^\s*enabled\s*:", text):
        text = re.sub(r"(?m)^\s*enabled\s*:.*$", replacement, text, count=1)
    else:
        suffix = "" if text.endswith("\n") else "\n"
        text = f"{text}{suffix}{replacement}\n"
    path.write_text(text, encoding="utf-8", newline="\n")
    state = "enabled" if enabled else "disabled"
    return Diagnostic(severity=Severity.INFO, message=f"Pack {state}: {name}", path=path)
