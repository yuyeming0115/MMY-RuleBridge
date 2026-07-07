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
    rows = [[badge(item.severity.value, item.severity.value.lower()), esc(item.message), f"<code>{esc(item.path or '')}</code>"] for item in diagnostics]
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
        blocks.append(f"<details {'open' if index < 2 else ''}><summary><code>{esc(file.path)}</code></summary><pre>{esc(diff or '# no changes\n')}</pre></details>")
    return "".join(blocks)


def packs_html(packs) -> str:
    rows = [[esc(pack.name), badge("enabled" if pack.enabled else "disabled", "ok" if pack.enabled else "neutral"), esc(pack.title or ""), esc(", ".join(pack.targets)), esc(pack.license or "")] for pack in packs]
    return table(["Name", "State", "Title", "Targets", "License"], rows, "No packs found.")


def resources_html(source) -> str:
    rule_rows = [[esc(rule.name), esc(rule.title), f"<code>{esc(rule.path)}</code>", esc(rule.source), esc(rule.pack_name or "")] for rule in source.rules]
    skill_rows = [[esc(skill.name), f"<code>{esc(skill.path)}</code>", esc(skill.source), esc(skill.pack_name or "")] for skill in source.skills]
    command_rows = [[esc(command.name), f"<code>{esc(command.path)}</code>", esc(command.source), esc(command.pack_name or "")] for command in source.commands]
    hook_rows = [[esc(hook.event), esc(len(hook.steps)), esc(", ".join(hook.targets) or "all"), f"<code>{esc(hook.path)}</code>", esc(hook.source)] for hook in source.hooks]
    mcp_rows = [[esc(server.name), badge("enabled" if server.enabled else "disabled", "ok" if server.enabled else "neutral"), f"<code>{esc(server.command)}</code>", esc(", ".join(server.targets) or "all"), f"<code>{esc(server.path)}</code>", esc(server.source)] for server in source.mcp_servers]
    return f"""
<div class='resource-grid'>
  <section class='mini-card'><h3>Rules</h3>{table(['Name', 'Title', 'Path', 'Source', 'Pack'], rule_rows, 'No rules loaded.')}</section>
  <section class='mini-card'><h3>Skills</h3>{table(['Name', 'Path', 'Source', 'Pack'], skill_rows, 'No skills loaded.')}</section>
  <section class='mini-card'><h3>Commands</h3>{table(['Name', 'Path', 'Source', 'Pack'], command_rows, 'No commands loaded.')}</section>
  <section class='mini-card'><h3>Hooks</h3>{table(['Event', 'Steps', 'Targets', 'Path', 'Source'], hook_rows, 'No hooks loaded.')}</section>
  <section class='mini-card wide'><h3>MCP Servers</h3>{table(['Name', 'State', 'Command', 'Targets', 'Path', 'Source'], mcp_rows, 'No MCP servers loaded.')}</section>
</div>"""


def nav_chip(label: str, href: str, count: int | None = None) -> str:
    suffix = f"<span>{count}</span>" if count is not None else ""
    return f"<a class='nav-chip' href='#{href}'>{esc(label)}{suffix}</a>"


def top_stat(label: str, value: object, kind: str = "neutral") -> str:
    return f"<div class='top-stat {esc(kind)}'><b>{esc(value)}</b><span>{esc(label)}</span></div>"


def render_home(
    root: str,
    *,
    target: str | None = None,
    action: str = "inspect",
    force: bool = False,
    insert_managed_block: bool = False,
    theme: str = "dark",
) -> str:
    theme = "light" if theme == "light" else "dark"
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
    other_theme = "light" if theme == "dark" else "dark"
    theme_href = "?" + urlencode({"root": root, "target": target or "", "theme": other_theme, "action": "inspect"})

    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
<meta charset='utf-8'>
<title>RuleBridge Web</title>
<style>
:root {{ color-scheme: dark light; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif; background:var(--bg); color:var(--text); }}
body.theme-dark {{ --bg:#080a12; --bg2:#0d111c; --panel:#11131d; --panel2:#171a25; --card:#161922; --text:#f4f7fb; --muted:#8b93a7; --line:#292d3a; --input:#151823; --code:#07111f; --blue:#58a6ff; --blue2:#7c5cff; --green:#62d26f; --yellow:#f5a524; --red:#ff5c5c; --shadow:#0008; }}
body.theme-light {{ --bg:#eef2f7; --bg2:#f8fafc; --panel:#ffffff; --panel2:#f3f6fb; --card:#ffffff; --text:#0f172a; --muted:#64748b; --line:#d9e1ec; --input:#ffffff; --code:#eff6ff; --blue:#2563eb; --blue2:#7c3aed; --green:#16a34a; --yellow:#b45309; --red:#dc2626; --shadow:#0f172a14; }}
a {{ color:inherit; }}
.shell {{ min-height:100vh; background:radial-gradient(circle at top left, color-mix(in srgb, var(--blue) 14%, transparent), transparent 32rem), var(--bg); }}
.topnav {{ height:74px; display:grid; grid-template-columns:auto 1fr auto; gap:18px; align-items:center; padding:10px 16px; border-bottom:1px solid var(--line); background:color-mix(in srgb, var(--panel) 92%, transparent); position:sticky; top:0; z-index:5; backdrop-filter:blur(14px); box-shadow:0 10px 30px var(--shadow); }}
.brandbox {{ display:flex; align-items:center; gap:12px; min-width:250px; }}
.logo {{ width:48px; height:48px; display:grid; place-items:center; border-radius:14px; background:linear-gradient(135deg,var(--blue),var(--blue2)); box-shadow:0 0 28px color-mix(in srgb, var(--blue) 35%, transparent); font-size:26px; }}
.brand {{ font-size:22px; font-weight:900; line-height:1; }} .tagline {{ color:var(--muted); font-size:12px; margin-top:5px; }}
.toplinks {{ display:flex; gap:8px; align-items:center; flex-wrap:wrap; }}
.nav-chip {{ text-decoration:none; padding:9px 13px; border:1px solid transparent; color:var(--muted); border-radius:12px; font-weight:800; display:flex; gap:8px; align-items:center; }}
.nav-chip:hover {{ border-color:var(--line); background:var(--panel2); color:var(--text); }}
.nav-chip span {{ font-size:11px; color:var(--blue); background:color-mix(in srgb, var(--blue) 14%, transparent); padding:2px 7px; border-radius:999px; }}
.topstats {{ display:flex; gap:8px; align-items:center; }}
.top-stat {{ min-width:72px; text-align:center; padding:8px 10px; border:1px solid var(--line); border-radius:10px; background:var(--panel2); }}
.top-stat b {{ display:block; font-size:15px; }} .top-stat span {{ color:var(--muted); font-size:10px; }}
.top-stat.ok b {{ color:var(--green); }} .top-stat.warn b {{ color:var(--yellow); }} .top-stat.error b {{ color:var(--red); }}
.theme-link {{ text-decoration:none; padding:9px 12px; border:1px solid var(--line); border-radius:10px; color:var(--text); background:var(--panel2); font-weight:800; }}
.workspace {{ display:grid; grid-template-columns:430px 1fr; min-height:calc(100vh - 74px); }}
.left-panel {{ border-right:1px solid var(--line); background:color-mix(in srgb, var(--panel) 88%, transparent); padding:16px; }}
.main-grid {{ padding:16px; display:grid; grid-template-columns:repeat(12,minmax(0,1fr)); gap:14px; align-content:start; }}
.card {{ grid-column:span 12; background:color-mix(in srgb, var(--card) 95%, transparent); border:1px solid var(--line); border-radius:0; padding:16px; box-shadow:0 14px 34px var(--shadow); }}
.card.half {{ grid-column:span 6; }} .card h2 {{ margin:0 0 14px; font-size:16px; }}
.panel-section {{ border-bottom:1px solid var(--line); padding:0 0 20px; margin-bottom:20px; }} .panel-section:last-child {{ border-bottom:0; }}
.panel-section h2 {{ margin:0 0 12px; font-size:15px; }}
label {{ font-size:12px; color:var(--muted); font-weight:800; display:block; margin:10px 0; }}
input[type=text], select {{ width:100%; padding:12px; border:1px solid var(--line); border-radius:9px; margin-top:7px; background:var(--input); color:var(--text); outline:none; }}
.check {{ color:var(--text); font-weight:600; }}
.btn-row {{ display:flex; gap:8px; flex-wrap:wrap; }}
button {{ padding:9px 13px; border:1px solid color-mix(in srgb, var(--blue) 55%, var(--line)); border-radius:10px; background:linear-gradient(135deg,var(--blue),var(--blue2)); color:white; font-weight:900; cursor:pointer; box-shadow:0 0 18px color-mix(in srgb, var(--blue) 20%, transparent); }}
button.secondary {{ background:var(--panel2); color:var(--text); border-color:var(--line); box-shadow:none; }}
button.warn {{ background:color-mix(in srgb, var(--yellow) 18%, transparent); border-color:var(--yellow); color:var(--yellow); box-shadow:none; }}
button.danger {{ background:color-mix(in srgb, var(--red) 18%, transparent); border-color:var(--red); color:var(--red); box-shadow:none; }}
.monitor {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }}
.monitor .metric {{ min-height:72px; }}
.metrics {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:10px; }}
.metric {{ background:var(--panel2); border:1px solid var(--line); border-radius:12px; padding:12px; }}
.metric span {{ color:var(--muted); font-size:11px; font-weight:800; text-transform:uppercase; }} .metric b {{ display:block; font-size:24px; margin-top:4px; }}
.badge {{ display:inline-flex; align-items:center; border:1px solid var(--line); border-radius:999px; padding:3px 9px; font-size:12px; font-weight:900; background:var(--panel2); color:var(--blue); }}
.badge.ok {{ color:var(--green); border-color:color-mix(in srgb, var(--green) 45%, var(--line)); background:color-mix(in srgb, var(--green) 12%, transparent); }}
.badge.warn {{ color:var(--yellow); border-color:color-mix(in srgb, var(--yellow) 45%, var(--line)); background:color-mix(in srgb, var(--yellow) 12%, transparent); }}
.badge.error {{ color:var(--red); border-color:color-mix(in srgb, var(--red) 45%, var(--line)); background:color-mix(in srgb, var(--red) 12%, transparent); }}
.badge.neutral {{ color:var(--muted); }}
.resource-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }} .mini-card {{ border:1px solid var(--line); background:var(--panel2); padding:13px; }} .mini-card.wide {{ grid-column:span 2; }} .mini-card h3 {{ margin:0 0 10px; }}
.table-wrap {{ overflow:auto; border:1px solid var(--line); border-radius:8px; }} table {{ width:100%; border-collapse:collapse; font-size:13px; }} th {{ color:var(--muted); background:color-mix(in srgb, var(--panel) 70%, var(--bg)); text-align:left; font-size:11px; text-transform:uppercase; letter-spacing:.04em; }} th,td {{ border-bottom:1px solid var(--line); padding:9px 10px; vertical-align:top; }} tr:hover td {{ background:color-mix(in srgb, var(--blue) 7%, transparent); }}
code {{ background:var(--code); color:var(--blue); padding:2px 6px; border-radius:6px; }} pre {{ background:#020617; color:#d1fae5; padding:12px; border-radius:10px; overflow:auto; max-height:420px; }}
details {{ border:1px solid var(--line); border-radius:10px; padding:10px; margin:10px 0; background:var(--panel2); }} summary {{ cursor:pointer; font-weight:900; }} .muted {{ color:var(--muted); }}
@media (max-width:1200px) {{ .workspace {{ grid-template-columns:1fr; }} .left-panel {{ border-right:0; border-bottom:1px solid var(--line); }} .card.half {{ grid-column:span 12; }} }}
@media (max-width:780px) {{ .topnav {{ grid-template-columns:1fr; height:auto; }} .topstats {{ flex-wrap:wrap; }} .resource-grid {{ grid-template-columns:1fr; }} .mini-card.wide {{ grid-column:span 1; }} }}
</style>
<script>function setAction(name){{document.getElementById('action').value=name; if(name==='sync'&&!confirm('确认要写入生成文件吗？建议先 Dry Run。'))return false; document.getElementById('mainform').submit();}}</script>
</head>
<body class='theme-{esc(theme)}'><div class='shell'>
<form id='mainform' method='get' action='/'>
<input type='hidden' id='action' name='action' value='inspect'>
<input type='hidden' name='theme' value='{esc(theme)}'>
<header class='topnav'>
  <div class='brandbox'><div class='logo'>🌉</div><div><div class='brand'>RuleBridge</div><div class='tagline'>AI Agent 配置桥接控制台</div></div></div>
  <nav class='toplinks'>{nav_chip('Dashboard','dashboard')}{nav_chip('Operations','operations')}{nav_chip('Resources','resources',len(source.rules)+len(source.skills)+len(source.commands)+len(source.hooks)+len(source.mcp_servers))}{nav_chip('Generated','generated',len(info['files']))}{nav_chip('Diagnostics','diagnostics',len(diagnostics))}{nav_chip('Packs','packs',len(packs))}{nav_chip('Results','results')}</nav>
  <div class='topstats'>{top_stat('Rules',len(source.rules))}{top_stat('Errors',counts['ERROR'],'error')}{top_stat('Warnings',counts['WARN'],'warn')}{badge(status_label,overall)}<a class='theme-link' href='{esc(theme_href)}'>{'浅色' if theme == 'dark' else '深色'}</a></div>
</header>
<div class='workspace'>
  <aside class='left-panel'>
    <section class='panel-section'><h2>Project Settings</h2><label>Project Root <input type='text' name='root' value='{esc(root)}'></label><label>Target <select name='target'>{options}</select></label>{checkbox('force','force overwrite',force)}{checkbox('insert_managed_block','insert managed block',insert_managed_block)}</section>
    <section id='operations' class='panel-section'><h2>Operations</h2><p class='muted'>Safe Checks</p><div class='btn-row'><button type='button' class='secondary' onclick="setAction('inspect')">Inspect</button><button type='button' onclick="setAction('validate')">Validate</button><button type='button' onclick="setAction('doctor')">Doctor</button></div><p class='muted'>Preview</p><div class='btn-row'><button type='button' onclick="setAction('diff')">Preview Diff</button><button type='button' class='warn' onclick="setAction('dry-run')">Dry Run Sync</button></div><p class='muted'>Write</p><button type='button' class='danger' onclick="setAction('sync')">Sync</button></section>
    <section class='panel-section'><h2>Monitor</h2><div class='monitor'><div class='metric'><span>Action</span><b>{esc(action)}</b></div><div class='metric'><span>Status</span><b>{status_label}</b></div><div class='metric'><span>Files</span><b>{len(info['files'])}</b></div><div class='metric'><span>Packs</span><b>{enabled_packs}/{len(packs)}</b></div></div></section>
  </aside>
</form>
  <main class='main-grid'>
    <section id='dashboard' class='card'><h2>Dashboard</h2><div class='metrics'><div class='metric'><span>Project</span><b>{esc(source.config.project.name)}</b></div><div class='metric'><span>Rules</span><b>{len(source.rules)}</b></div><div class='metric'><span>Skills</span><b>{len(source.skills)}</b></div><div class='metric'><span>Commands</span><b>{len(source.commands)}</b></div><div class='metric'><span>Hooks</span><b>{len(source.hooks)}</b></div><div class='metric'><span>MCP Servers</span><b>{len(source.mcp_servers)}</b></div><div class='metric'><span>Generated Files</span><b>{len(info['files'])}</b></div><div class='metric'><span>Errors</span><b>{counts['ERROR']}</b></div><div class='metric'><span>Warnings</span><b>{counts['WARN']}</b></div></div></section>
    <section id='resources' class='card'><h2>Resources</h2>{resources_html(source)}</section>
    <section id='generated' class='card half'><h2>Generated Files</h2>{generated_files_table(info['files'])}</section>
    <section id='diagnostics' class='card half'><h2>Diagnostics</h2>{diagnostics_html(diagnostics)}</section>
    <section id='packs' class='card half'><h2>Packs</h2>{packs_html(packs)}</section>
    <section id='results' class='card'><h2>Results</h2><h3>Write Results</h3>{write_results_html(write_results)}<h3>Diff Preview</h3>{diff_html(diff_items)}</section>
  </main>
</div></div></body></html>"""


class RuleBridgeHandler(BaseHTTPRequestHandler):
    server_version = "RuleBridgeWeb/0.1"

    def do_GET(self) -> None:  # noqa: N802
        params = parse_qs(urlparse(self.path).query)
        root = params.get("root", [str(self.server.root)])[0]
        target = params.get("target", [""])[0] or None
        action = params.get("action", ["inspect"])[0]
        force = params.get("force", [""])[0] == "1"
        insert_managed_block = params.get("insert_managed_block", [""])[0] == "1"
        theme = params.get("theme", ["dark"])[0]
        try:
            body = render_home(root, target=target, action=action, force=force, insert_managed_block=insert_managed_block, theme=theme).encode("utf-8")
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
