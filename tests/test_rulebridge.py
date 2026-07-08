from __future__ import annotations

from pathlib import Path

from rulebridge.api import diff_api, inspect_api, sync_api, targets_api
from rulebridge.cli import app
from rulebridge.doctor import doctor_source
from rulebridge.generator import render_files
from rulebridge.pack import set_pack_enabled
from rulebridge.service import inspect_project, preview_diff, sync_project
from rulebridge.source import load_source
from rulebridge.web import asset_text, render_home
from rulebridge.validator import Severity, validate_source
from rulebridge.writer import START, desired_file_content, replace_managed_block


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def make_source(root: Path) -> None:
    write(
        root / ".ai-agent" / "rulebridge.yaml",
        """project:\n  name: Test Project\nrules:\n  include:\n    - rules/b.md\n    - rules/a.md\ntargets:\n  - codex\n  - claude\n  - cursor\n  - generic\n  - git\n  - mcp\n  - zcode\n  - trae\n  - codebuddy\n  - workbuddy\n""",
    )
    write(root / ".ai-agent" / "rules" / "a.md", "# A Rule\n\nA body.\n")
    write(root / ".ai-agent" / "rules" / "b.md", "# B Rule\n\nB body.\n")
    write(
        root / ".ai-agent" / "skills" / "demo" / "SKILL.md",
        """---\nname: demo\ndescription: Demo skill.\n---\n\n# Demo\n""",
    )
    write(
        root / ".ai-agent" / "commands" / "review.md",
        """---\ndescription: Review a scope.\nargument-hint: "[scope]"\n---\n\nReview $ARGUMENTS.\n""",
    )
    write(
        root / ".ai-agent" / "hooks" / "before_commit.yaml",
        """event: before_commit\nsteps:\n  - type: command\n    run: git status --short\n  - type: secret_scan\ntargets:\n  - git\n  - codex\n""",
    )
    write(
        root / ".ai-agent" / "mcp" / "servers.yaml",
        """servers:\n  filesystem:\n    enabled: true\n    command: npx\n    args:\n      - -y\n      - "@modelcontextprotocol/server-filesystem"\n      - .\n    env:\n      NODE_ENV: production\n    targets:\n      - mcp\n      - codebuddy\n      - workbuddy\n  disabled:\n    enabled: false\n    command: python\n""",
    )


def test_load_source_respects_include_order(tmp_path: Path) -> None:
    make_source(tmp_path)
    source = load_source(tmp_path)
    assert [rule.name for rule in source.rules] == ["b", "a"]
    assert [skill.name for skill in source.skills] == ["demo"]
    assert [command.name for command in source.commands] == ["review"]
    assert [hook.event for hook in source.hooks] == ["before_commit"]
    assert [server.name for server in source.mcp_servers] == ["filesystem", "disabled"]


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
    write(tmp_path / ".ai-agent" / "packs" / "enabled" / "commands" / "ship.md", "---\ndescription: Ship.\n---\n\nShip it.\n")
    write(tmp_path / ".ai-agent" / "packs" / "enabled" / "mcp" / "servers.yaml", "servers:\n  packfs:\n    enabled: true\n    command: npx\n")
    write(
        tmp_path / ".ai-agent" / "packs" / "disabled" / "pack.yaml",
        "name: disabled\nenabled: false\n",
    )
    write(tmp_path / ".ai-agent" / "packs" / "disabled" / "rules" / "off.md", "# Off\n")
    source = load_source(tmp_path)
    assert [rule.name for rule in source.rules] == ["p", "b", "a"]
    assert [command.name for command in source.commands] == ["ship", "review"]
    assert [server.name for server in source.mcp_servers] == ["packfs", "filesystem", "disabled"]


def test_render_target_paths(tmp_path: Path) -> None:
    make_source(tmp_path)
    source = load_source(tmp_path)
    paths = {str(file.path).replace("\\", "/") for file in render_files(source)}
    assert "AGENTS.md" in paths
    assert "CLAUDE.md" in paths
    assert ".cursor/rules/a.mdc" in paths
    assert ".zcode/skills/demo/SKILL.md" in paths
    assert ".zcode/commands/review.md" in paths
    assert ".claude/commands/review.md" in paths
    assert ".githooks/pre-commit" in paths
    assert ".mcp.json" in paths
    assert ".codebuddy-plugin/mcp.json" in paths
    assert ".workbuddy-plugin/mcp.json" in paths
    assert ".trae/skills/demo/SKILL.md" in paths
    assert ".codebuddy-plugin/rules/a.md" in paths
    assert ".workbuddy-plugin/skills/demo/SKILL.md" in paths


def test_mcp_json_excludes_disabled_servers(tmp_path: Path) -> None:
    make_source(tmp_path)
    source = load_source(tmp_path)
    file = next(item for item in render_files(source, "mcp") if item.path.name == ".mcp.json")
    assert '"filesystem"' in file.content
    assert '"disabled"' not in file.content


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


def test_validate_warns_for_inline_mcp_secret(tmp_path: Path) -> None:
    write(tmp_path / ".ai-agent" / "rulebridge.yaml", "targets:\n  - mcp\n")
    write(
        tmp_path / ".ai-agent" / "mcp" / "servers.yaml",
        """servers:\n  search:\n    enabled: true\n    command: python\n    env:\n      API_TOKEN: real-value\n""",
    )
    diagnostics = validate_source(load_source(tmp_path))
    assert any(item.severity == Severity.WARN and "inline secret" in item.message for item in diagnostics)


def test_new_managed_file_content_contains_markers(tmp_path: Path) -> None:
    make_source(tmp_path)
    source = load_source(tmp_path)
    file = next(item for item in render_files(source, "codex") if item.path.name == "AGENTS.md")
    desired, status = desired_file_content(None, file)
    assert status == "create"
    assert desired is not None
    assert desired.startswith(START)


def test_set_pack_enabled_toggles_pack_yaml(tmp_path: Path) -> None:
    write(tmp_path / ".ai-agent" / "packs" / "demo" / "pack.yaml", "name: demo\nenabled: false\n")
    diagnostic = set_pack_enabled(tmp_path, "demo", True)
    assert not diagnostic.is_error
    assert "enabled: true" in (tmp_path / ".ai-agent" / "packs" / "demo" / "pack.yaml").read_text(encoding="utf-8")


def test_list_commands_command_outputs_command(tmp_path: Path, capsys) -> None:
    make_source(tmp_path)
    assert app(["list-commands", "--root", str(tmp_path)]) == 0
    output = capsys.readouterr().out
    assert "review" in output
    assert "commands" in output


def test_list_hooks_command_outputs_hook(tmp_path: Path, capsys) -> None:
    make_source(tmp_path)
    assert app(["list-hooks", "--root", str(tmp_path)]) == 0
    output = capsys.readouterr().out
    assert "before_commit" in output
    assert "hooks" in output


def test_list_mcp_command_outputs_server(tmp_path: Path, capsys) -> None:
    make_source(tmp_path)
    assert app(["list-mcp", "--root", str(tmp_path)]) == 0
    output = capsys.readouterr().out
    assert "filesystem" in output
    assert "enabled" in output


def test_pack_list_command_outputs_pack(tmp_path: Path, capsys) -> None:
    write(tmp_path / ".ai-agent" / "packs" / "demo" / "pack.yaml", "name: demo\ntitle: Demo Pack\nenabled: true\n")
    assert app(["pack", "list", "--root", str(tmp_path)]) == 0
    output = capsys.readouterr().out
    assert "demo" in output
    assert "enabled" in output


def test_pack_diff_command_outputs_pack_content(tmp_path: Path, capsys) -> None:
    write(tmp_path / ".ai-agent" / "packs" / "demo" / "pack.yaml", "name: demo\nenabled: false\n")
    write(tmp_path / ".ai-agent" / "packs" / "demo" / "rules" / "review.md", "# Review\n\nCheck changes.\n")
    write(tmp_path / ".ai-agent" / "packs" / "demo" / "commands" / "ship.md", "---\ndescription: Ship.\n---\n\nShip.\n")
    write(tmp_path / ".ai-agent" / "packs" / "demo" / "mcp" / "servers.yaml", "servers:\n  demo:\n    command: npx\n")
    assert app(["pack", "diff", "demo", "--root", str(tmp_path)]) == 0
    output = capsys.readouterr().out
    normalized = output.replace("\\", "/")
    assert "packs/demo/rules/review.md" in normalized
    assert "packs/demo/commands/ship.md" in normalized
    assert "packs/demo/mcp/servers.yaml" in normalized
    assert "+# Review" in output


def test_doctor_reports_duplicate_rule_names_and_private_paths(tmp_path: Path) -> None:
    write(
        tmp_path / ".ai-agent" / "rulebridge.yaml",
        """project:\n  name: Test\ntargets:\n  - codex\n""",
    )
    write(tmp_path / ".ai-agent" / "rules" / "same.md", "# Same\n\nUse C:/Users/EDY/private.txt carefully.\n")
    write(tmp_path / ".ai-agent" / "mcp" / "servers.yaml", "servers:\n  same_mcp:\n    command: npx\n")
    write(tmp_path / ".ai-agent" / "packs" / "demo" / "pack.yaml", "name: demo\nenabled: true\n")
    write(tmp_path / ".ai-agent" / "packs" / "demo" / "rules" / "same.md", "# Pack Same\n")
    write(tmp_path / ".ai-agent" / "packs" / "demo" / "mcp" / "servers.yaml", "servers:\n  same_mcp:\n    command: npx\n")
    diagnostics = doctor_source(load_source(tmp_path))
    messages = [item.message for item in diagnostics]
    assert any("Duplicate rule name 'same'" in message for message in messages)
    assert any("Duplicate MCP server name 'same_mcp'" in message for message in messages)
    assert any("Private-looking local path" in message for message in messages)


def test_doctor_command_outputs_no_issues_for_clean_project(tmp_path: Path, capsys) -> None:
    make_source(tmp_path)
    assert app(["doctor", "--root", str(tmp_path), "--target", "codex"]) == 0
    output = capsys.readouterr().out
    assert "Doctor found no issues" in output


def test_service_preview_and_dry_run(tmp_path: Path) -> None:
    make_source(tmp_path)
    info = inspect_project(tmp_path, "codex")
    assert info["source"].config.project.name == "Test Project"
    diagnostics, diffs = preview_diff(tmp_path, "codex")
    assert not any(item.is_error for item in diagnostics)
    assert diffs
    diagnostics, results = sync_project(tmp_path, "codex", dry_run=True)
    assert not any(item.is_error for item in diagnostics)
    assert results[0].status == "dry-run"


def test_web_static_assets_are_available() -> None:
    index = asset_text("index.html")
    style = asset_text("style.css")
    script = asset_text("app.js")
    assert "RuleBridge Web" in index
    assert "Dashboard" in index
    assert "theme-dark" in style
    assert "theme-light" in style
    assert "Preview Diff" in index
    assert "Dry Run Sync" in index
    assert "/api/inspect" in script


def test_web_home_supports_light_theme(tmp_path: Path) -> None:
    make_source(tmp_path)
    html = render_home(str(tmp_path), target="codex", action="inspect", theme="light")
    assert "theme-light" in html


def test_api_inspect_and_diff_and_dry_run(tmp_path: Path) -> None:
    make_source(tmp_path)
    inspected = inspect_api(tmp_path, "codex")
    assert inspected["source"]["project"]["name"] == "Test Project"
    assert any(rule["title"] == "B Rule" for rule in inspected["source"]["rules"])
    assert any(server["name"] == "filesystem" for server in inspected["source"]["mcpServers"])
    assert "codex" in targets_api()["targets"]
    diffed = diff_api(tmp_path, "codex")
    assert diffed["diffs"]
    synced = sync_api(tmp_path, "codex", dry_run=True)
    assert synced["results"]
    assert synced["results"][0]["status"] == "dry-run"
