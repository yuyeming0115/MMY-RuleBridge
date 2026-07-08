from __future__ import annotations

import json
import mimetypes
import threading
import time as _time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

from . import api

ASSET_PACKAGE = "rulebridge.web_assets"


def asset_text(name: str) -> str:
    return resources.files(ASSET_PACKAGE).joinpath(name).read_text(encoding="utf-8")


def asset_bytes(name: str) -> bytes:
    return resources.files(ASSET_PACKAGE).joinpath(name).read_bytes()


def render_home(*_args, theme: str = "dark", **_kwargs) -> str:
    html = asset_text("index.html")
    theme = "light" if theme == "light" else "dark"
    return html.replace('class="theme-dark"', f'class="theme-{theme}"')


class RuleBridgeHandler(BaseHTTPRequestHandler):
    server_version = "RuleBridgeWeb/0.2"

    def do_GET(self) -> None:  # noqa: N802
        self.server.last_request = _time.time()  # type: ignore[attr-defined]
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            theme = parse_qs(parsed.query).get("theme", ["dark"])[0]
            self.send_text(render_home(theme=theme), "text/html; charset=utf-8")
            return
        if parsed.path.startswith("/static/"):
            self.serve_static(parsed.path.removeprefix("/static/"))
            return
        if parsed.path.startswith("/api/"):
            self.serve_api_get(parsed.path, parse_qs(parsed.query))
            return
        self.send_error(404, "Not found")

    def do_POST(self) -> None:  # noqa: N802
        self.server.last_request = _time.time()  # type: ignore[attr-defined]
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/api/"):
            self.send_error(404, "Not found")
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            payload = json.loads(raw or "{}")
        except json.JSONDecodeError as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=400)
            return
        self.serve_api_post(parsed.path, payload)

    def serve_static(self, name: str) -> None:
        if name not in {"style.css", "app.js"}:
            self.send_error(404, "Static asset not found")
            return
        content_type = mimetypes.guess_type(name)[0] or "application/octet-stream"
        self.send_bytes(asset_bytes(name), content_type)

    def serve_api_get(self, path: str, params: dict[str, list[str]]) -> None:
        root = params.get("root", [str(self.server.root)])[0]
        target = params.get("target", [""])[0] or None
        try:
            if path == "/api/inspect":
                self.send_json(api.inspect_api(root, target))
            elif path == "/api/validate":
                self.send_json(api.validate_api(root, target))
            elif path == "/api/doctor":
                self.send_json(api.doctor_api(root, target))
            elif path == "/api/targets":
                self.send_json(api.targets_api())
            elif path == "/api/packs":
                self.send_json(api.packs_api(root))
            else:
                self.send_error(404, "API endpoint not found")
        except Exception as exc:  # pragma: no cover - defensive server boundary
            self.send_json({"ok": False, "error": str(exc)}, status=500)

    def serve_api_post(self, path: str, payload: dict) -> None:
        root = payload.get("root", str(self.server.root))
        target = payload.get("target") or None
        force = bool(payload.get("force", False))
        insert_managed_block = bool(payload.get("insert_managed_block", False))
        try:
            if path == "/api/diff":
                self.send_json(api.diff_api(root, target, force=force, insert_managed_block=insert_managed_block))
            elif path == "/api/sync":
                self.send_json(api.sync_api(root, target, dry_run=bool(payload.get("dry_run", False)), force=force, insert_managed_block=insert_managed_block))
            elif path == "/api/init":
                self.send_json(api.init_api(root, force=force))
            elif path == "/api/pack/enable":
                self.send_json(api.pack_set_api(root, str(payload.get("name", "")), True))
            elif path == "/api/pack/disable":
                self.send_json(api.pack_set_api(root, str(payload.get("name", "")), False))
            elif path == "/api/pack/diff":
                self.send_json(api.pack_diff_api(root, str(payload.get("name", ""))))
            elif path == "/api/shutdown":
                self.send_json({"ok": True})
                import threading

                def _shutdown() -> None:
                    import time
                    time.sleep(0.2)
                    self.server.shutdown()

                threading.Thread(target=_shutdown, daemon=True).start()
            else:
                self.send_error(404, "API endpoint not found")
        except Exception as exc:  # pragma: no cover - defensive server boundary
            self.send_json({"ok": False, "error": str(exc)}, status=500)

    def send_text(self, text: str, content_type: str, status: int = 200) -> None:
        self.send_bytes(text.encode("utf-8"), content_type, status)

    def send_json(self, payload: dict, status: int = 200) -> None:
        self.send_bytes(json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8", status)

    def send_bytes(self, body: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        print("RuleBridge Web:", format % args)


def run_web(root: Path | str = ".", host: str = "127.0.0.1", port: int = 8765, open_browser: bool = True, idle_timeout: int = 300) -> None:
    """Start the RuleBridge web server.

    Args:
        root: Project root directory.
        host: Bind address (default 127.0.0.1).
        port: Bind port (default 8765).
        open_browser: Whether to auto-open browser.
        idle_timeout: Seconds of no requests before auto-shutdown. 0 disables.
    """
    server = ThreadingHTTPServer((host, port), RuleBridgeHandler)
    server.root = Path(root).resolve()  # type: ignore[attr-defined]
    server.last_request = _time.time()  # type: ignore[attr-defined]
    url = f"http://{host}:{port}/?{urlencode({'root': str(server.root)})}"
    print(f"RuleBridge Web running at {url}")
    if idle_timeout > 0:
        print(f"Idle timeout: {idle_timeout}s (auto-shutdown after no activity)")

    def _idle_watcher() -> None:
        while getattr(server, "_shutdown_requested", False) is False:
            _time.sleep(5)
            elapsed = _time.time() - server.last_request  # type: ignore[attr-defined]
            if elapsed >= idle_timeout:
                print(f"RuleBridge: no requests for {elapsed:.0f}s, shutting down.")
                server.shutdown()
                break

    if idle_timeout > 0:
        threading.Thread(target=_idle_watcher, daemon=True).start()

    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nRuleBridge Web stopped.")
    finally:
        server.server_close()
