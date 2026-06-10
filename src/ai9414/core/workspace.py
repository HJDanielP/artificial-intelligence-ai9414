"""On-disk workspace for student solver drafts.

The embedded editor autosaves to the browser's ``localStorage`` for instant
crash/refresh safety, but students also want a *real* ``.py`` file they can open
in an IDE, submit, or feed back through ``ai9414 serve --solver path.py``. This
module owns that file: one ``solve_<demo>.py`` per demo under a workspace
directory (default ``./ai9414-solutions`` in the current working directory).

We deliberately do **not** write into the installed package directory: site
``site-packages`` is often read-only and is wiped on reinstall, so a student's
work would be lost. A cwd-relative folder is visible and easy to find instead.
"""

from __future__ import annotations

from pathlib import Path

_DEFAULT_DIRNAME = "ai9414-solutions"
_workspace_dir: Path | None = None


def set_workspace_dir(path: str | Path | None) -> None:
    """Override the workspace directory (called from ``serve --workspace``)."""

    global _workspace_dir
    _workspace_dir = Path(path).expanduser() if path else None


def workspace_dir() -> Path:
    """Resolve the active workspace directory (not created until a write)."""

    if _workspace_dir is not None:
        return _workspace_dir
    return Path.cwd() / _DEFAULT_DIRNAME


def draft_path(demo: str) -> Path:
    """Path of the on-disk draft file for ``demo`` (``solve_<demo>.py``)."""

    return workspace_dir() / f"solve_{demo}.py"


def read_draft(demo: str) -> dict[str, object]:
    """Return the saved draft for ``demo`` (empty string if none yet)."""

    path = draft_path(demo)
    code = path.read_text(encoding="utf-8") if path.exists() else ""
    return {"ok": True, "code": code, "path": str(path)}


def write_draft(demo: str, code: str) -> dict[str, object]:
    """Persist ``code`` to ``solve_<demo>.py``, creating the workspace dir."""

    path = draft_path(demo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(code, encoding="utf-8")
    return {"ok": True, "path": str(path)}
