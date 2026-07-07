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


def checkbox(name: str, checked: bool = False) -> str:
    return f'<label><input type="checkbox" name="{name}" value="1" {"checked" if checked else ""}> {name}</label>'


def diagnostics_html(diagnostics) -> str:
    if not diagnostics:
        return "<p class='ok'>No diagnostics.</p>"
    rows = "".join(
        f"<tr><td class='{esc(item.severity.value.lower())}'>{esc(item.severity.value)}</td><td>{esc(item.message)}</td><td>{esc(item.path or '')}</td></tr>"
        for item in diagnostics
    )
    return f"<table><tr><th>Severity</th><th>Message</th><th>Path</th></tr>{rows}</table>"


def write_results_html(results) -> str:
    if not results:
        return ""
    rows = "".join(f"<tr><td>{esc(item.status)}</td><td>{esc(item.path)}</td><td>{esc(item.message)}</td></tr>" for item in results)
    return f"<h2>Write Results</h2><table><tr><th>Status</th><th>Path</th><th>Message</th></tr>{rows}</table>"


def generated_files_html(files) -> str:
    if not files:
        return "<p>No generated files.</p>"
    items = "".join(f"<li><code>{esc(file.path)}</code></li>" for file in files)
    return f"<ul>{items}</ul>"


def diff_html(diff_items) -> str:
    if not diff_items:
        return ""
    blocks = []
    for file, diff in diff_items:
        blocks.append(f"<h3>{esc(file.path)}</h3><pre>{esc(diff or '# no changes\n')}</pre>")
    return "<h2>Diff Preview</h2>" + "".join(blocks)


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

    targets = ["", *info["targets"]]
    options = "".join(
        f'<option value="{esc(name)}" {"selected" if (target or "") == name else ""}>{esc(name or "all targets")}</option>'
        for name in targets
    )
    packs = info["packs"]
    pack_items = "".join(f"<li>{esc(pack.name)} — {'enabled' if pack.enabled else 'disabled'}</li>" for pack in packs) or "<li>No packs</li>"
    query_base = {"root": root, "target": target or "", "force": "1" if force else "", "insert_managed_block": "1" if insert_managed_block else ""}

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>RuleBridge Web</title>
<style>
body {{ font-family: system-ui, -apple-system, Segoe UI, sans-serif; margin: 24px; background: #f6f7f9; color: #1f2937; }}
main {{ max-width: 1180px; margin: auto; }}
.card {{ background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 18px; margin: 16px 0; box-shadow: 0 1px 2px #0001; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }}
.metric {{ background: #f9fafb; border-radius: 10px; padding: 12px; }}
.metric b {{ display:block; font-size: 24px; }}
input[type=text], select {{ width: 100%; padding: 8px; border: 1px solid #d1d5db; border-radius: 8px; }}
button {{ padding: 9px 12px; margin: 4px; border: 0; border-radius: 8px; background: #2563eb; color: white; cursor: pointer; }}
button.warn {{ background: #b45309; }}
button.danger {{ background: #dc2626; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ border-bottom: 1px solid #e5e7eb; padding: 8px; text-align: left; vertical-align: top; }}
pre {{ background: #111827; color: #d1fae5; padding: 12px; border-radius: 10px; overflow: auto; }}
.error {{ color: #dc2626; font-weight: 700; }} .warn {{ color: #b45309; font-weight: 700; }} .info {{ color: #2563eb; font-weight: 700; }} .ok {{ color: #059669; }}
</style>
<script>function setAction(name){{document.getElementById('action').value=name; if(name==='sync'&&!confirm('确认要写入生成文件吗？建议先 Dry Run。'))return false; document.getElementById('mainform').submit();}}</script>
</head>
<body><main>
<h1>RuleBridge Web</h1>
<p>本地可视化面板。默认只建议操作你信任的项目目录。</p>
<div class="card">
<form id="mainform" method="get" action="/">
<input type="hidden" id="action" name="action" value="inspect">
<label>Project Root <input type="text" name="root" value="{esc(root)}"></label><br><br>
<label>Target <select name="target">{options}</select></label><br><br>
{checkbox('force', force)} {checkbox('insert_managed_block', insert_managed_block)}<br><br>
<button type="button" onclick="setAction('inspect')">Inspect</button>
<button type="button" onclick="setAction('validate')">Validate</button>
<button type="button" onclick="setAction('doctor')">Doctor</button>
<button type="button" onclick="setAction('diff')">Preview Diff</button>
<button type="button" class="warn" onclick="setAction('dry-run')">Dry Run Sync</button>
<button type="button" class="danger" onclick="setAction('sync')">Sync</button>
</form>
</div>
<div class="card">
<h2>Project Overview</h2>
<div class="grid">
<div class="metric">Project<b>{esc(source.config.project.name)}</b></div>
<div class="metric">Rules<b>{len(source.rules)}</b></div>
<div class="metric">Skills<b>{len(source.skills)}</b></div>
<div class="metric">Commands<b>{len(source.commands)}</b></div>
<div class="metric">Hooks<b>{len(source.hooks)}</b></div>
<div class="metric">MCP Servers<b>{len(source.mcp_servers)}</b></div>
</div>
<h3>Packs</h3><ul>{pack_items}</ul>
</div>
<div class="card"><h2>Diagnostics</h2>{diagnostics_html(diagnostics)}</div>
<div class="card"><h2>Generated Files</h2>{generated_files_html(info['files'])}</div>
<div class="card">{write_results_html(write_results)}{diff_html(diff_items)}</div>
</main></body></html>"""


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
