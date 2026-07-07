from __future__ import annotations

from pathlib import Path

from rulebridge.generator import render_files
from rulebridge.source import load_source
from rulebridge.validator import Severity, validate_source
from rulebridge.writer import START, desired_file_content, replace_managed_block


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def make_source(root: Path) -> None:
    write(
        root / ".ai-agent" / "rulebridge.yaml",
        """project:\n  name: Test Project\nrules:\n  include:\n    - rules/b.md\n    - rules/a.md\ntargets:\n  - codex\n  - claude\n  - cursor\n  - generic\n  - zcode\n  - trae\n  - codebuddy\n  - workbuddy\n""",
    )
    write(root / ".ai-agent" / "rules" / "a.md", "# A Rule\n\nA body.\n")
    write(root / ".ai-agent" / "rules" / "b.md", "# B Rule\n\nB body.\n")
    write(
        root / ".ai-agent" / "skills" / "demo" / "SKILL.md",
        """---\nname: demo\ndescription: Demo skill.\n---\n\n# Demo\n""",
    )


def test_load_source_respects_include_order(tmp_path: Path) -> None:
    make_source(tmp_path)
    source = load_source(tmp_path)
    assert [rule.name for rule in source.rules] == ["b", "a"]
    assert [skill.name for skill in source.skills] == ["demo"]


def test_default_rule_scan_when_no_include(tmp_path: Path) -> None:
    write(root := tmp_path / ".ai-agent" / "rulebridge.yaml", "project:\n  name: Test\n")
    write(tmp_path / ".ai-agent" / "rules" / "common.md", "# Common\n")
    source = load_source(tmp_path)
    assert [rule.name for rule in source.rules] == ["common"]


def test_pack_enabled_and_disabled(tmp_path: Path) -> None:
    make_source(tmp_path)
    write(
        tmp_path / ".ai-agent" / "packs" / "enabled" / "pack.yaml",
        "name: enabled\nenabled: true\n",
    )
    write(tmp_path / ".ai-agent" / "packs" / "enabled" / "rules" / "p.md", "# Pack Rule\n")
    write(
        tmp_path / ".ai-agent" / "packs" / "disabled" / "pack.yaml",
        "name: disabled\nenabled: false\n",
    )
    write(tmp_path / ".ai-agent" / "packs" / "disabled" / "rules" / "off.md", "# Off\n")
    source = load_source(tmp_path)
    assert [rule.name for rule in source.rules] == ["p", "b", "a"]


def test_render_target_paths(tmp_path: Path) -> None:
    make_source(tmp_path)
    source = load_source(tmp_path)
    paths = {str(file.path).replace("\\", "/") for file in render_files(source)}
    assert "AGENTS.md" in paths
    assert "CLAUDE.md" in paths
    assert ".cursor/rules/a.mdc" in paths
    assert ".zcode/skills/demo/SKILL.md" in paths
    assert ".trae/skills/demo/SKILL.md" in paths
    assert ".codebuddy-plugin/rules/a.md" in paths
    assert ".workbuddy-plugin/skills/demo/SKILL.md" in paths


def test_managed_block_replacement() -> None:
    existing = "intro\n<!-- rulebridge:start -->\nold\n<!-- rulebridge:end -->\noutro\n"
    replaced = replace_managed_block(existing, "new")
    assert replaced == "intro\n<!-- rulebridge:start -->\nnew\n<!-- rulebridge:end -->\noutro\n"


def test_existing_unmanaged_file_refuses_by_default(tmp_path: Path) -> None:
    make_source(tmp_path)
    source = load_source(tmp_path)
    file = next(item for item in render_files(source, "codex") if item.path.name == "AGENTS.md")
    desired, status = desired_file_content("manual content\n", file)
    assert desired is None
    assert status == "refuse"


def test_validate_reports_missing_rule_and_secret_keyword(tmp_path: Path) -> None:
    write(
        tmp_path / ".ai-agent" / "rulebridge.yaml",
        """rules:\n  include:\n    - rules/missing.md\n    - rules/security.md\ntargets:\n  - codex\n""",
    )
    write(tmp_path / ".ai-agent" / "rules" / "security.md", "# Security\n\ntoken: example-only\n")
    source = load_source(tmp_path)
    diagnostics = validate_source(source)
    assert any(item.severity == Severity.ERROR and "missing.md" in item.message.lower() for item in diagnostics)
    assert any(item.severity == Severity.WARN and "token" in item.message.lower() for item in diagnostics)


def test_new_managed_file_content_contains_markers(tmp_path: Path) -> None:
    make_source(tmp_path)
    source = load_source(tmp_path)
    file = next(item for item in render_files(source, "codex") if item.path.name == "AGENTS.md")
    desired, status = desired_file_content(None, file)
    assert status == "create"
    assert desired is not None
    assert desired.startswith(START)
