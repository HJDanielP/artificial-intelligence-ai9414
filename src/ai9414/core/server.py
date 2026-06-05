"""FastAPI servers and launcher helpers.

Two app factories share one set of route handlers:

- :func:`create_app` builds the unified multi-demo application used by
  ``ai9414 serve``. Routes are namespaced under ``/api/{demo}/...`` and the
  demo instance is resolved lazily from :mod:`ai9414.core.registry`.
- :func:`create_fastapi_app` builds a single-demo application (used by the test
  suite and by ``ai9414 demo X``). Routes are unprefixed (``/api/...``) and
  bound to one instance.

Both serve the same single-page frontend from ``ai9414.frontend`` (preferring
the built ``web`` bundle, falling back to the legacy ``student`` assets while
the new frontend is being built out).
"""

from __future__ import annotations

import socket
import webbrowser
from importlib import resources
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from ai9414.core import solve as solve_module
from ai9414.core.errors import AI9414Error
from ai9414.core.registry import get_demo, list_demos, resolve_demo_spec


class NoCacheStaticFiles(StaticFiles):
    """Serve bundled demo assets without browser caching during local teaching runs."""

    async def get_response(self, path: str, scope: dict[str, Any]):  # type: ignore[override]
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-store"
        return response


def find_free_port(host: str = "127.0.0.1") -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return int(sock.getsockname()[1])


def _frontend_dir(*, prefer_web: bool) -> Path:
    """Return the directory of frontend assets to serve.

    The unified app serves the built Svelte SPA (``web``); the single-demo app
    serves the legacy ``student`` shell, which targets the unprefixed routes the
    SPA does not use. Each falls back to the other if its preferred bundle is
    absent (e.g. before the first ``npm run build``).
    """

    root = Path(str(resources.files("ai9414.frontend")))
    web = root / "web"
    student = root / "student"
    order = (web, student) if prefer_web else (student, web)
    for candidate in order:
        if (candidate / "index.html").exists():
            return candidate
    return order[0]


def _mount_frontend(api: FastAPI, *, prefer_web: bool) -> None:
    directory = _frontend_dir(prefer_web=prefer_web)

    # Built Vite bundles reference hashed files under /assets; the legacy
    # student shell loads /assets/style.css and /assets/app.js. Either way the
    # asset folder lives next to index.html, so serve it from there.
    #
    # NoCacheStaticFiles sends Cache-Control: no-store so a frontend edit is
    # picked up on a normal browser refresh during local teaching runs. The
    # built SPA already content-hashes its filenames, but the legacy shell's
    # app.js / style.css keep stable names and would otherwise be cached.
    assets_dir = directory / "assets"
    if assets_dir.exists():
        api.mount("/assets", NoCacheStaticFiles(directory=str(assets_dir)), name="assets")
    else:
        # Legacy student shell keeps style.css / app.js at the package root.
        api.mount("/assets", NoCacheStaticFiles(directory=str(directory)), name="assets")

    index_path = directory / "index.html"

    @api.get("/", include_in_schema=False)
    def index() -> HTMLResponse:
        # Read per request so a frontend rebuild (new hashed asset names) is
        # picked up without restarting the server, and send no-store so the
        # unhashed index entry itself is never served stale from cache.
        return HTMLResponse(
            index_path.read_text(encoding="utf-8"),
            headers={"Cache-Control": "no-store"},
        )


# --- Shared route handlers ---------------------------------------------------


def _handle_action(app_instance: Any, request: dict[str, Any]) -> JSONResponse:
    payload = app_instance.handle_action(request)
    status_code = 200 if payload.get("ok", True) else 400
    return JSONResponse(payload, status_code=status_code)


def _handle_solve(demo_name: str, request: dict[str, Any]) -> JSONResponse:
    try:
        result = solve_module.run_student_solver(demo_name, request)
    except AI9414Error as exc:
        return JSONResponse(exc.to_payload(), status_code=400)
    return JSONResponse({"ok": True, "trace": result["trace"], "stdout": result.get("stdout", "")})


def _handle_stub(demo_name: str) -> JSONResponse:
    try:
        return JSONResponse(solve_module.get_stub(demo_name))
    except AI9414Error as exc:
        return JSONResponse(exc.to_payload(), status_code=400)


# --- Single-demo app (tests, `ai9414 demo X`) --------------------------------


def create_fastapi_app(app_instance: Any) -> FastAPI:
    api = FastAPI(title=app_instance.app_title)
    _mount_frontend(api, prefer_web=False)

    demo_name = _demo_name_for(app_instance)

    @api.get("/api/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "app_type": app_instance.app_type,
            "session_id": app_instance.session_id,
        }

    @api.get("/api/manifest")
    def manifest() -> dict[str, Any]:
        return app_instance.build_manifest()

    @api.get("/api/state")
    def state() -> dict[str, Any]:
        return app_instance.build_state_payload()

    @api.get("/api/trace")
    def trace() -> dict[str, Any]:
        return app_instance.get_trace_payload()

    @api.get("/api/examples")
    def examples() -> dict[str, Any]:
        return {"ok": True, "examples": app_instance.list_examples()}

    @api.get("/api/errors")
    def errors() -> dict[str, Any]:
        return app_instance.get_recent_errors()

    @api.get("/api/stub")
    def stub() -> JSONResponse:
        return _handle_stub(demo_name)

    @api.post("/api/action")
    def action(request: dict[str, Any]) -> JSONResponse:
        return _handle_action(app_instance, request)

    @api.post("/api/solve")
    def solve(request: dict[str, Any]) -> JSONResponse:
        return _handle_solve(demo_name, request)

    return api


def _demo_name_for(app_instance: Any) -> str:
    """Best-effort canonical demo name for a single instance (for solve/stub)."""

    try:
        return resolve_demo_spec(app_instance.app_type).name
    except AI9414Error:
        return app_instance.app_type


# --- Unified multi-demo app (`ai9414 serve`) ---------------------------------


def _resolve_or_404(demo: str) -> Any:
    try:
        return get_demo(demo)
    except AI9414Error as exc:
        raise _http_404(exc) from exc


def _http_404(exc: AI9414Error):
    from fastapi import HTTPException

    return HTTPException(status_code=404, detail=exc.to_payload())


def create_app() -> FastAPI:
    api = FastAPI(title="ai9414")
    _mount_frontend(api, prefer_web=True)

    @api.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @api.get("/api/demos")
    def demos() -> dict[str, Any]:
        return {"ok": True, "demos": list_demos()}

    @api.get("/api/{demo}/manifest")
    def manifest(demo: str) -> dict[str, Any]:
        return _resolve_or_404(demo).build_manifest()

    @api.get("/api/{demo}/state")
    def state(demo: str) -> dict[str, Any]:
        return _resolve_or_404(demo).build_state_payload()

    @api.get("/api/{demo}/trace")
    def trace(demo: str) -> dict[str, Any]:
        return _resolve_or_404(demo).get_trace_payload()

    @api.get("/api/{demo}/examples")
    def examples(demo: str) -> dict[str, Any]:
        return {"ok": True, "examples": _resolve_or_404(demo).list_examples()}

    @api.get("/api/{demo}/errors")
    def errors(demo: str) -> dict[str, Any]:
        return _resolve_or_404(demo).get_recent_errors()

    @api.get("/api/{demo}/stub")
    def stub(demo: str) -> JSONResponse:
        _resolve_or_404(demo)
        return _handle_stub(resolve_demo_spec(demo).name)

    @api.post("/api/{demo}/action")
    def action(demo: str, request: dict[str, Any]) -> JSONResponse:
        return _handle_action(_resolve_or_404(demo), request)

    @api.post("/api/{demo}/solve")
    def solve(demo: str, request: dict[str, Any]) -> JSONResponse:
        _resolve_or_404(demo)
        return _handle_solve(resolve_demo_spec(demo).name, request)

    return api


# --- Launcher ----------------------------------------------------------------


class AppLauncher:
    """Launch a local FastAPI app and open the browser.

    Pass either a single ``app_instance`` (legacy single-demo launch) or a
    prebuilt ``fastapi_app`` (the unified ``ai9414 serve`` application).
    """

    def __init__(
        self,
        app_instance: Any,
        *,
        host: str = "127.0.0.1",
        port: int | None = None,
        open_browser: bool = True,
        fastapi_app: FastAPI | None = None,
    ) -> None:
        self.app_instance = app_instance
        self.fastapi_app = fastapi_app
        self.host = host
        self.port = port or find_free_port(host)
        self.open_browser = open_browser
        self.url = f"http://{self.host}:{self.port}"

    def start(self) -> None:
        self._log_startup()
        self._open_browser_if_possible()
        app = self.fastapi_app if self.fastapi_app is not None else create_fastapi_app(self.app_instance)
        uvicorn.run(app, host=self.host, port=self.port, log_level="warning")

    def _log_startup(self) -> None:
        if self.app_instance is not None:
            loaded_name = (
                self.app_instance.config_name or self.app_instance.example_name or "default"
            )
            print(f"app name: {self.app_instance.app_title}")
            print(f"mode: {self.app_instance.mode}")
            print(f"execution mode: {self.app_instance.execution_mode}")
            print(f"localhost url: {self.url}")
            print(f"example or config loaded: {loaded_name}")
        else:
            print("app name: ai9414 (all demos)")
            print(f"localhost url: {self.url}")

    def _open_browser_if_possible(self) -> None:
        if not self.open_browser:
            return
        try:
            opened = webbrowser.open(self.url)
        except Exception as exc:  # pragma: no cover - platform-specific guard
            raise AI9414Error(
                code="browser_open_failed",
                message=(
                    "Could not open the browser automatically. "
                    f"Open this URL manually: {self.url}"
                ),
                details={"exception_type": type(exc).__name__, "url": self.url},
            ) from exc
        if not opened:
            print(f"Could not open the browser automatically. Open this URL manually: {self.url}")


def launch_app(app_instance: Any, *, host: str = "127.0.0.1", port: int | None = None) -> None:
    launcher = AppLauncher(app_instance, host=host, port=port)
    launcher.start()


def launch_unified(
    *,
    host: str = "127.0.0.1",
    port: int | None = None,
    open_browser: bool = True,
) -> None:
    """Launch the unified multi-demo ``ai9414 serve`` application."""

    launcher = AppLauncher(
        None,
        host=host,
        port=port,
        open_browser=open_browser,
        fastapi_app=create_app(),
    )
    launcher.start()
