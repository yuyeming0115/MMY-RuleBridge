from __future__ import annotations

import argparse
from pathlib import Path

from .adapters import list_targets as adapter_names
from .doctor import doctor_source
from .generator import render_files
from .initializer import init_source
from .models import Diagnostic, Severity
from .pack import list_packs, pack_content_diff, set_pack_enabled
from .source import load_source
from .validator import has_errors, validate_source, validate_targets
from .web import run_web
from .writer import diff_for_file, write_files


def print_diagnostic(item: Diagnostic) -> None:
    path = f" {item.path}" if item.path else ""
    print(f"[{item.severity.value}] {item.message}{path}")


def abort_on_errors(diagnostics: list[Diagnostic]) -> None:
    for item in diagnostics:
        print_diagnostic(item)
    if has_errors(diagnostics):
        raise SystemExit(1)


def cmd_init(args: argparse.Namespace) -> int:
    result = init_source(args.root, force=args.force)
    for item in result.files:
        print(f"{item.status} {item.path}")
    print(f"Init complete: {result.written} written, {result.skipped} skipped.")
    return 0


def cmd_list_targets(args: argparse.Namespace) -> int:
    for name in adapter_names():
        print(name)
    return 0


def cmd_pack_list(args: argparse.Namespace) -> int:
    packs, diagnostics = list_packs(args.root.resolve())
    abort_on_errors(diagnostics)
    if not packs:
        print("No packs found.")
        return 0
    for pack in packs:
        state = "enabled" if pack.enabled else "disabled"
        title = pack.title or pack.name
        print(f"{pack.name}\t{state}\t{title}")
    return 0


def cmd_pack_enable(args: argparse.Namespace) -> int:
    diagnostic = set_pack_enabled(args.root.resolve(), args.name, True)
    print_diagnostic(diagnostic)
    return 1 if diagnostic.is_error else 0


def cmd_pack_disable(args: argparse.Namespace) -> int:
    diagnostic = set_pack_enabled(args.root.resolve(), args.name, False)
    print_diagnostic(diagnostic)
    return 1 if diagnostic.is_error else 0


def cmd_pack_diff(args: argparse.Namespace) -> int:
    output, diagnostic = pack_content_diff(args.root.resolve(), args.name)
    if diagnostic is not None:
        print_diagnostic(diagnostic)
        return 1 if diagnostic.is_error else 0
    print(output, end="")
    return 0


def cmd_list_rules(args: argparse.Namespace) -> int:
    source = load_source(args.root)
    abort_on_errors(source.diagnostics)
    for rule in source.rules:
        origin = f"pack:{rule.pack_name}" if rule.source == "pack" else "project"
        print(f"{rule.name}\t{rule.path}\t{origin}")
    return 0


def cmd_list_commands(args: argparse.Namespace) -> int:
    source = load_source(args.root)
    abort_on_errors(source.diagnostics)
    for command in source.commands:
        origin = f"pack:{command.pack_name}" if command.source == "pack" else "project"
        print(f"{command.name}\t{command.path}\t{origin}")
    return 0


def cmd_list_hooks(args: argparse.Namespace) -> int:
    source = load_source(args.root)
    abort_on_errors(source.diagnostics)
    for hook in source.hooks:
        origin = f"pack:{hook.pack_name}" if hook.source == "pack" else "project"
        targets = ",".join(hook.targets) if hook.targets else "all"
        print(f"{hook.event}\t{hook.path}\t{targets}\t{origin}")
    return 0


def cmd_list_mcp(args: argparse.Namespace) -> int:
    source = load_source(args.root)
    abort_on_errors(source.diagnostics)
    for server in source.mcp_servers:
        origin = f"pack:{server.pack_name}" if server.source == "pack" else "project"
        targets = ",".join(server.targets) if server.targets else "all"
        state = "enabled" if server.enabled else "disabled"
        print(f"{server.name}\t{state}\t{server.command}\t{targets}\t{origin}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    source = load_source(args.root)
    diagnostics = validate_source(source, args.target)
    if not diagnostics:
        print("[OK] configuration is valid")
        return 0
    abort_on_errors(diagnostics)
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    source = load_source(args.root)
    diagnostics = doctor_source(source, args.target)
    for item in diagnostics:
        print_diagnostic(item)
    return 1 if has_errors(diagnostics) else 0


def cmd_diff(args: argparse.Namespace) -> int:
    source = load_source(args.root)
    abort_on_errors([*source.diagnostics, *validate_targets(source, args.target)])
    files = render_files(source, args.target)
    abort_on_errors(validate_source(source, args.target, files))
    for file in files:
        output = diff_for_file(source.root, file, force=args.force, insert_managed_block=args.insert_managed_block)
        if output:
            print(output, end="")
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    source = load_source(args.root)
    abort_on_errors([*source.diagnostics, *validate_targets(source, args.target)])
    files = render_files(source, args.target)
    abort_on_errors(validate_source(source, args.target, files))
    results = write_files(source.root, files, dry_run=args.dry_run, force=args.force, insert_managed_block=args.insert_managed_block)
    for result in results:
        print(f"[{result.status}] {result.path} - {result.message}")
    return 0


def cmd_web(args: argparse.Namespace) -> int:
    run_web(args.root, host=args.host, port=args.port, open_browser=not args.no_open)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rulebridge", description="Bridge one .ai-agent source into multiple AI agent rule formats.")
    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser("init", help="Create a sample .ai-agent source directory.")
    init_parser.add_argument("--root", type=Path, default=Path("."), help="Project root directory.")
    init_parser.add_argument("--force", action="store_true", help="Overwrite sample source files if they already exist.")
    init_parser.set_defaults(func=cmd_init)

    targets_parser = sub.add_parser("list-targets", help="List supported target adapters.")
    targets_parser.set_defaults(func=cmd_list_targets)

    pack_parser = sub.add_parser("pack", help="Manage optional rule and skill packs.")
    pack_sub = pack_parser.add_subparsers(dest="pack_command", required=True)

    pack_list_parser = pack_sub.add_parser("list", help="List available packs.")
    pack_list_parser.add_argument("--root", type=Path, default=Path("."), help="Project root directory.")
    pack_list_parser.set_defaults(func=cmd_pack_list)

    pack_enable_parser = pack_sub.add_parser("enable", help="Enable a pack by name.")
    pack_enable_parser.add_argument("name", help="Pack name.")
    pack_enable_parser.add_argument("--root", type=Path, default=Path("."), help="Project root directory.")
    pack_enable_parser.set_defaults(func=cmd_pack_enable)

    pack_disable_parser = pack_sub.add_parser("disable", help="Disable a pack by name.")
    pack_disable_parser.add_argument("name", help="Pack name.")
    pack_disable_parser.add_argument("--root", type=Path, default=Path("."), help="Project root directory.")
    pack_disable_parser.set_defaults(func=cmd_pack_disable)

    pack_diff_parser = pack_sub.add_parser("diff", help="Show rules and skills provided by a pack.")
    pack_diff_parser.add_argument("name", help="Pack name.")
    pack_diff_parser.add_argument("--root", type=Path, default=Path("."), help="Project root directory.")
    pack_diff_parser.set_defaults(func=cmd_pack_diff)

    rules_parser = sub.add_parser("list-rules", help="List loaded rules.")
    rules_parser.add_argument("--root", type=Path, default=Path("."), help="Project root directory.")
    rules_parser.set_defaults(func=cmd_list_rules)

    commands_parser = sub.add_parser("list-commands", help="List loaded commands.")
    commands_parser.add_argument("--root", type=Path, default=Path("."), help="Project root directory.")
    commands_parser.set_defaults(func=cmd_list_commands)

    hooks_parser = sub.add_parser("list-hooks", help="List loaded hooks.")
    hooks_parser.add_argument("--root", type=Path, default=Path("."), help="Project root directory.")
    hooks_parser.set_defaults(func=cmd_list_hooks)

    mcp_parser = sub.add_parser("list-mcp", help="List loaded MCP servers.")
    mcp_parser.add_argument("--root", type=Path, default=Path("."), help="Project root directory.")
    mcp_parser.set_defaults(func=cmd_list_mcp)

    validate_parser = sub.add_parser("validate", help="Validate source configuration without writing files.")
    validate_parser.add_argument("--root", type=Path, default=Path("."), help="Project root directory.")
    validate_parser.add_argument("--target", help="Only validate one target adapter.")
    validate_parser.set_defaults(func=cmd_validate)

    doctor_parser = sub.add_parser("doctor", help="Run deeper diagnostics for safety and maintainability.")
    doctor_parser.add_argument("--root", type=Path, default=Path("."), help="Project root directory.")
    doctor_parser.add_argument("--target", help="Only inspect one target adapter.")
    doctor_parser.set_defaults(func=cmd_doctor)

    diff_parser = sub.add_parser("diff", help="Show unified diff for generated files.")
    diff_parser.add_argument("--root", type=Path, default=Path("."), help="Project root directory.")
    diff_parser.add_argument("--target", help="Only process one target adapter.")
    diff_parser.add_argument("--force", action="store_true", help="Diff as if existing files can be overwritten.")
    diff_parser.add_argument("--insert-managed-block", action="store_true", help="Diff as if a managed block can be appended.")
    diff_parser.set_defaults(func=cmd_diff)

    sync_parser = sub.add_parser("sync", help="Generate target files from .ai-agent source.")
    sync_parser.add_argument("--root", type=Path, default=Path("."), help="Project root directory.")
    sync_parser.add_argument("--target", help="Only process one target adapter.")
    sync_parser.add_argument("--dry-run", action="store_true", help="Show writes without changing files.")
    sync_parser.add_argument("--force", action="store_true", help="Overwrite existing generated files.")
    sync_parser.add_argument("--insert-managed-block", action="store_true", help="Append a managed block to existing Markdown files.")
    sync_parser.set_defaults(func=cmd_sync)

    web_parser = sub.add_parser("web", help="Start the local RuleBridge Web UI.")
    web_parser.add_argument("--root", type=Path, default=Path("."), help="Project root directory.")
    web_parser.add_argument("--host", default="127.0.0.1", help="Host to bind. Keep 127.0.0.1 for local-only use.")
    web_parser.add_argument("--port", type=int, default=8765, help="Port to bind.")
    web_parser.add_argument("--no-open", action="store_true", help="Do not open the browser automatically.")
    web_parser.set_defaults(func=cmd_web)

    return parser


def app(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
