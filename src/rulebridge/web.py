from __future__ import annotations

import html
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

from .service import doctor_project, inspect_project, preview_diff, sync_project
from .validator import validate_source


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def severity_counts(diagnostics) -> dict[str, int]:
    counts = {"ERROR": 0, "WARN": 0, "INFO": 0}
    for item in diagnostics:
        counts[item.severity.value] = counts.get(item.severity.value, 0) + 1
    return counts


def status_kind(diagnostics) -> str:
    counts = severity_counts(diagnostics)
    if counts["ERROR"]:
        return "error"
    if counts["WARN"]:
        return "warn"
    return "ok"


def badge(text: object, kind: str = "info") -> str:
    return f"<span class='badge {esc(kind)}'>{esc(text)}</span>"


def checkbox(name: str, label: str, checked: bool = False) -> str:
    return f"<label class='check'><input type='checkbox' name='{name}' value='1' {'checked' if checked else ''}> {esc(label)}</label>"


def category_for_path(path: object) -> str:
    value = str(path).replace("\\", "/")
    if value == "AGENTS.md":
        return "codex"
    if value == "CLAUDE.md" or value.startswith(".claude/"):
        return "claude"
    if value.startswith(".cursor/"):
        return "cursor"
    if value.startswith(".zcode/"):
        return "zcode"
    if value.startswith(".trae/"):
        return "trae"
    if value.startswith(".githooks/"):
        return "git"
    if value == ".mcp.json":
        return "mcp"
    if value.startswith(".codebuddy-plugin/"):
        return "codebuddy"
    if value.startswith(".workbuddy-plugin/"):
        return "workbuddy"
    return "generic"


def table(headers: list[str], rows: list[list[object]], empty: str) -> str:
    if not rows:
        return f"<p class='muted'>{esc(empty)}</p>"
    head = "".join(f"<th>{esc(item)}</th>" for item in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f"<div class='table-wrap'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def diagnostics_html(diagnostics) -> str:
    rows = [
        [badge(item.severity.value, item.severity.value.lower()), esc(item.message), f"<code>{esc(item.path or '')}</code>"]
        for item in diagnostics
    ]
    return table(["Severity", "Message", "Path"], rows, "No diagnostics.")


def generated_files_table(files) -> str:
    rows = [
        [f"<code>{esc(file.path)}</code>", badge(category_for_path(file.path), "neutral"), badge("managed" if file.managed else "unmanaged", "ok" if file.managed else "warn")]
        for file in files
    ]
    return table(["Path", "Category", "Mode"], rows, "No generated files.")


def write_results_html(results) -> str:
    rows = [[badge(item.status, "ok" if item.status in {"create", "update", "dry-run"} else "warn"), f"<code>{esc(item.path)}</code>", esc(item.message)] for item in results]
    return table(["Status", "Path", "Message"], rows, "No write results yet.")


def diff_html(diff_items) -> str:
    if not diff_items:
        return "<p class='muted'>No diff preview yet.</p>"
    blocks = []
    for index, (file, diff) in enumerate(diff_items):
        blocks.append(
            f"<details {'open' if index < 2 else ''}><summary><code>{esc(file.path)}</code></summary><pre>{esc(diff or '# no changes\n')}</pre></details>"
        )
    return "".join(blocks)


def packs_html(packs) -> str:
    rows = [
        [esc(pack.name), badge("enabled" if pack.enabled else "disabled", "ok" if pack.enabled else "neutral"), esc(pack.title or ""), esc(", ".join(pack.targets)), esc(pack.license or "")]
        for pack in packs
    ]
    return table(["Name", "State", "Title", "Targets", "License"], rows, "No packs found.")


def resources_html(source) -> str:
    rule_rows = [[esc(rule.name), esc(rule.title), f"<code>{esc(rule.path)}</code>", esc(rule.source), esc(rule.pack_name or "")] for rule in source.rules]
    skill_rows = [[esc(skill.name), f"<code>{esc(skill.path)}</code>", esc(skill.source), esc(skill.pack_name or "")] for skill in source.skills]
    command_rows = [[esc(command.name), f"<code>{esc(command.path)}</code>", esc(command.source), esc(command.pack_name or "")] for command in source.commands]
    hook_rows = [[esc(hook.event), esc(len(hook.steps)), esc(", ".join(hook.targets) or "all"), f"<code>{esc(hook.path)}</code>", esc(hook.source)] for hook in source.hooks]
    mcp_rows = [[esc(server.name), badge("enabled" if server.enabled else "disabled", "ok" if server.enabled else "neutral"), f"<code>{esc(server.command)}</code>", esc(", ".join(server.targets) or "all"), f"<code>{esc(server.path)}</code>", esc(server.source)] for server in source.mcp_servers]
    return f"""
<div class='subgrid'>
  <section class='subcard'><h3>Rules</h3>{table(['Name', 'Title', 'Path', 'Source', 'Pack'], rule_rows, 'No rules loaded.')}</section>
  <section class='subcard'><h3>Skills</h3>{table(['Name', 'Path', 'Source', 'Pack'], skill_rows, 'No skills loaded.')}</section>
  <section class='subcard'><h3>Commands</h3>{table(['Name', 'Path', 'Source', 'Pack'], command_rows, 'No commands loaded.')}</section>
  <section class='subcard'><h3>Hooks</h3>{table(['Event', 'Steps', 'Targets', 'Path', 'Source'], hook_rows, 'No hooks loaded.')}</section>
  <section class='subcard wide'><h3>MCP Servers</h3>{table(['Name', 'State', 'Command', 'Targets', 'Path', 'Source'], mcp_rows, 'No MCP servers loaded.')}</section>
</div>"""


def nav_item(label: str, href: str, count: int | None = None) -> str:
    suffix = f"<span>{count}</span>" if count is not None else ""
    return f"<a href='#{href}'>{esc(label)}{suffix}</a>"


def render_home(
    root: str,
    *,
    target: str | None = None,
    action: str = "inspect",
    force: bool = False,
    insert_managed_block: bool = False,
) -> str:
    info = inspect_project(root, target or None)
    source = info["source"]
    diagnostics = list(info["diagnostics"])
    diff_items = []
    write_results = []

    if action == "validate":
        diagnostics = validate_source(source, target or None, info["files"])
    elif action == "doctor":
        diagnostics = doctor_project(root, target or None)
    elif action == "diff":
        diagnostics, diff_items = preview_diff(root, target or None, force=force, insert_managed_block=insert_managed_block)
    elif action == "dry-run":
        diagnostics, write_results = sync_project(root, target or None, dry_run=True, force=force, insert_managed_block=insert_managed_block)
    elif action == "sync":
        diagnostics, write_results = sync_project(root, target or None, dry_run=False, force=force, insert_managed_block=insert_managed_block)

    counts = severity_counts(diagnostics)
    overall = status_kind(diagnostics)
    status_label = "ERROR" if overall == "error" else "WARN" if overall == "warn" else "OK"
    targets = ["", *info["targets"]]
    options = "".join(f"<option value='{esc(name)}' {'selected' if (target or '') == name else ''}>{esc(name or 'all targets')}</option>" for name in targets)
    packs = info["packs"]
    enabled_packs = sum(1 for pack in packs if pack.enabled)

    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
<meta charset='utf-8'>
<title>RuleBridge Web</title>
<style>
:root {{ --bg:#0f172a; --panel:#111827; --card:#ffffff; --muted:#64748b; --line:#e5e7eb; --blue:#2563eb; --green:#059669; --yellow:#b45309; --red:#dc2626; }}
* {{ box-sizing: border-box; }}
body {{ margin:0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; background:#f3f4f6; color:#111827; }}
.app {{ display:grid; grid-template-columns:260px 1fr; min-height:100vh; }}
.sidebar {{ background:linear-gradient(180deg,#111827,#0f172a); color:white; padding:22px; position:sticky; top:0; height:100vh; }}
.brand {{ font-size:24px; font-weight:800; margin-bottom:4px; }}
.tagline {{ color:#cbd5e1; font-size:13px; margin-bottom:24px; }}
.nav a {{ display:flex; justify-content:space-between; align-items:center; color:#e5e7eb; text-decoration:none; padding:10px 12px; border-radius:10px; margin:4px 0; }}
.nav a:hover {{ background:#1f2937; }}
.nav span {{ background:#334155; padding:2px 8px; border-radius:999px; font-size:12px; }}
.content {{ padding:20px 28px 48px; }}
.topbar {{ background:white; border:1px solid var(--line); border-radius:18px; padding:16px; display:grid; grid-template-columns:1.2fr 1.8fr 0.8fr auto; gap:12px; align-items:end; box-shadow:0 1px 3px #0000000d; position:sticky; top:12px; z-index:2; }}
label {{ font-size:12px; color:var(--muted); font-weight:700; display:block; }}
input[type=text], select {{ width:100%; padding:10px 12px; border:1px solid #d1d5db; border-radius:10px; margin-top:6px; background:white; }}
.card {{ background:white; border:1px solid var(--line); border-radius:18px; padding:18px; margin-top:18px; box-shadow:0 1px 3px #0000000d; }}
.card h2 {{ margin:0 0 14px; }}
.metrics {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; }}
.metric {{ background:linear-gradient(180deg,#f8fafc,#fff); border:1px solid var(--line); border-radius:14px; padding:14px; }}
.metric span {{ color:var(--muted); font-size:12px; font-weight:700; }}
.metric b {{ display:block; font-size:26px; margin-top:4px; }}
.ops {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:14px; }}
.opgroup {{ border:1px solid var(--line); border-radius:14px; padding:14px; background:#f9fafb; }}
.opgroup h3 {{ margin:0 0 10px; }}
button {{ padding:10px 12px; margin:4px 4px 4px 0; border:0; border-radius:10px; background:var(--blue); color:white; font-weight:700; cursor:pointer; }}
button.secondary {{ background:#475569; }} button.warn {{ background:var(--yellow); }} button.danger {{ background:var(--red); }}
.check {{ display:block; margin-top:8px; color:#374151; font-weight:500; }}
.badge {{ display:inline-flex; align-items:center; border-radius:999px; padding:3px 9px; font-size:12px; font-weight:800; background:#e0e7ff; color:#3730a3; }}
.badge.ok {{ background:#dcfce7; color:#166534; }} .badge.warn {{ background:#fef3c7; color:#92400e; }} .badge.error {{ background:#fee2e2; color:#991b1b; }} .badge.neutral {{ background:#e5e7eb; color:#374151; }} .badge.info {{ background:#dbeafe; color:#1d4ed8; }}
.subgrid {{ display:grid; grid-template-columns:1fr; gap:14px; }}
.subcard {{ border:1px solid var(--line); border-radius:14px; padding:14px; background:#fbfdff; }}
.table-wrap {{ overflow:auto; border:1px solid var(--line); border-radius:12px; }}
table {{ width:100%; border-collapse:collapse; font-size:14px; }}
th {{ background:#f8fafc; color:#475569; text-align:left; font-size:12px; text-transform:uppercase; letter-spacing:.03em; }}
th, td {{ border-bottom:1px solid var(--line); padding:9px 10px; vertical-align:top; }}
tr:hover td {{ background:#f9fafb; }}
code {{ background:#f1f5f9; padding:2px 5px; border-radius:6px; }}
pre {{ background:#0b1220; color:#d1fae5; padding:12px; border-radius:12px; overflow:auto; max-height:420px; }}
details {{ border:1px solid var(--line); border-radius:12px; padding:10px 12px; margin:10px 0; background:#fff; }}
summary {{ cursor:pointer; font-weight:700; }}
.muted {{ color:var(--muted); }}
@media (max-width: 900px) {{ .app {{ grid-template-columns:1fr; }} .sidebar {{ position:relative; height:auto; }} .topbar {{ grid-template-columns:1fr; position:relative; top:0; }} }}
</style>
<script>function setAction(name){{document.getElementById('action').value=name; if(name==='sync'&&!confirm('确认要写入生成文件吗？建议先 Dry Run。'))return false; document.getElementById('mainform').submit();}}</script>
</head>
<body><div class='app'>
<aside class='sidebar'>
  <div class='brand'>RuleBridge</div>
  <div class='tagline'>AI Agent 配置桥接控制台</div>
  <nav class='nav'>
    {nav_item('Dashboard', 'dashboard')}
    {nav_item('Operations', 'operations')}
    {nav_item('Resources', 'resources', len(source.rules)+len(source.skills)+len(source.commands)+len(source.hooks)+len(source.mcp_servers))}
    {nav_item('Generated Files', 'generated', len(info['files']))}
    {nav_item('Diagnostics', 'diagnostics', len(diagnostics))}
    {nav_item('Packs', 'packs', len(packs))}
    {nav_item('Results', 'results')}
  </nav>
</aside>
<main class='content'>
<form id='mainform' method='get' action='/'>
<input type='hidden' id='action' name='action' value='inspect'>
<section class='topbar'>
  <div><label>Project</label><strong>{esc(source.config.project.name)}</strong><div class='muted'>{esc(action)}</div></div>
  <label>Project Root <input type='text' name='root' value='{esc(root)}'></label>
  <label>Target <select name='target'>{options}</select></label>
  <div>{badge(status_label, overall)}</div>
</section>
<section id='dashboard' class='card'>
  <h2>Dashboard</h2>
  <div class='metrics'>
    <div class='metric'><span>Rules</span><b>{len(source.rules)}</b></div>
    <div class='metric'><span>Skills</span><b>{len(source.skills)}</b></div>
    <div class='metric'><span>Commands</span><b>{len(source.commands)}</b></div>
    <div class='metric'><span>Hooks</span><b>{len(source.hooks)}</b></div>
    <div class='metric'><span>MCP Servers</span><b>{len(source.mcp_servers)}</b></div>
    <div class='metric'><span>Generated Files</span><b>{len(info['files'])}</b></div>
    <div class='metric'><span>Errors</span><b>{counts['ERROR']}</b></div>
    <div class='metric'><span>Warnings</span><b>{counts['WARN']}</b></div>
    <div class='metric'><span>Packs Enabled</span><b>{enabled_packs}/{len(packs)}</b></div>
  </div>
</section>
<section id='operations' class='card'>
  <h2>Operations</h2>
  <div class='ops'>
    <div class='opgroup'><h3>Safe Checks</h3><button type='button' onclick="setAction('inspect')">Inspect</button><button type='button' onclick="setAction('validate')">Validate</button><button type='button' onclick="setAction('doctor')">Doctor</button></div>
    <div class='opgroup'><h3>Preview</h3><button type='button' onclick="setAction('diff')">Preview Diff</button><button type='button' class='warn' onclick="setAction('dry-run')">Dry Run Sync</button></div>
    <div class='opgroup'><h3>Write</h3><p class='muted'>会写入项目目录内生成文件。</p><button type='button' class='danger' onclick="setAction('sync')">Sync</button></div>
    <div class='opgroup'><h3>Options</h3>{checkbox('force', 'force overwrite', force)}{checkbox('insert_managed_block', 'insert managed block', insert_managed_block)}</div>
  </div>
</section>
</form>
<section id='resources' class='card'><h2>Resources</h2>{resources_html(source)}</section>
<section id='generated' class='card'><h2>Generated Files</h2>{generated_files_table(info['files'])}</section>
<section id='diagnostics' class='card'><h2>Diagnostics</h2>{diagnostics_html(diagnostics)}</section>
<section id='packs' class='card'><h2>Packs</h2>{packs_html(packs)}</section>
<section id='results' class='card'><h2>Results</h2><h3>Write Results</h3>{write_results_html(write_results)}<h3>Diff Preview</h3>{diff_html(diff_items)}</section>
</main></div></body></html>"""


class RuleBridgeHandler(BaseHTTPRequestHandler):
    server_version = "RuleBridgeWeb/0.1"

    def do_GET(self) -> None:  # noqa: N802
        params = parse_qs(urlparse(self.path).query)
        root = params.get("root", [str(self.server.root)])[0]
        target = params.get("target", [""])[0] or None
        action = params.get("action", ["inspect"])[0]
        force = params.get("force", [""])[0] == "1"
        insert_managed_block = params.get("insert_managed_block", [""])[0] == "1"
        try:
            body = render_home(root, target=target, action=action, force=force, insert_managed_block=insert_managed_block).encode("utf-8")
            status = 200
        except Exception as exc:  # pragma: no cover - defensive server boundary
            body = f"<h1>RuleBridge Web Error</h1><pre>{esc(exc)}</pre>".encode("utf-8")
            status = 500
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        print("RuleBridge Web:", format % args)


def run_web(root: Path | str = ".", host: str = "127.0.0.1", port: int = 8765, open_browser: bool = True) -> None:
    server = ThreadingHTTPServer((host, port), RuleBridgeHandler)
    server.root = Path(root).resolve()  # type: ignore[attr-defined]
    url = f"http://{host}:{port}/?{urlencode({'root': str(server.root)})}"
    print(f"RuleBridge Web running at {url}")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nRuleBridge Web stopped.")
    finally:
        server.server_close()
