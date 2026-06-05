"""In-process execution of student solver code for the live workflow.

The browser's embedded editor (or a ``--solver`` file passed to ``ai9414
serve``) posts Python source to ``POST /api/{demo}/solve``. This module runs
that code in a fresh namespace, validates the returned result with the demo's
existing ``validate_*`` helpers, and converts it into a unified ``TraceBundle``
so the frontend can replay it exactly like a reference example.

Security: this executes the student's own code on their own machine over
localhost only. It is not sandboxed, which is equivalent to the previous
``python solve_X.py`` workflow.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ai9414.core.errors import AI9414Error
from ai9414.core.registry import resolve_demo_spec


@dataclass(frozen=True)
class LiveSpec:
    """Wire one demo's student-solver contract to its validators and trace builder.

    Most demos use the default flow (single-argument solver returning a result
    dict, converted by ``build_trace(problem, result)``). Demos whose solver
    takes extra arguments (``options``), define several functions (uncertainty),
    or reuse an existing server-side trace builder provide a ``run`` override.
    """

    entry: str
    """Name of the function the student must define, e.g. ``solve_bfs``."""

    problem_key: str = "problem"
    """Request field that carries the problem (e.g. ``graph``, ``labyrinth``)."""

    stub: str = ""
    """Starter code shown in the embedded editor."""

    # --- Default flow (used when `run` is None) ---
    validate_payload: Callable[[dict[str, Any]], dict[str, Any]] | None = None
    validate_result: Callable[[dict[str, Any]], dict[str, Any]] | None = None
    build_trace: Callable[[dict[str, Any], dict[str, Any]], Any] | None = None

    # --- Override: full control over solving + trace building ---
    run: Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], Any] | None = None
    """``(namespace, problem, options) -> TraceBundle``. Takes precedence."""


# Cache of built LiveSpecs, keyed by canonical registry name (e.g. "graph-bfs").
# Specs are produced lazily by each demo's ``live_factory`` (see registry).
LIVE_SPECS: dict[str, LiveSpec] = {}

_PRELOADED_SOLVER: Path | None = None


def set_preloaded_solver(path: str | Path | None) -> None:
    """Remember a ``--solver`` file to use when the request carries no code."""

    global _PRELOADED_SOLVER
    _PRELOADED_SOLVER = Path(path).expanduser().resolve() if path else None


def get_spec(demo: str) -> LiveSpec:
    demo_spec = resolve_demo_spec(demo)
    cached = LIVE_SPECS.get(demo_spec.name)
    if cached is not None:
        return cached
    if demo_spec.live_factory is None:
        raise AI9414Error(
            code="unsupported_action",
            message=f"Live Python solving is not available for '{demo}' yet.",
        )
    live_spec = demo_spec.live_factory()
    LIVE_SPECS[demo_spec.name] = live_spec
    return live_spec


def get_stub(demo: str) -> dict[str, Any]:
    """Return the starter code for a demo's embedded editor."""

    spec = get_spec(demo)
    return {"ok": True, "entry": spec.entry, "code": spec.stub}


def _load_namespace_from_code(code: str) -> dict[str, Any]:
    namespace: dict[str, Any] = {}
    try:
        compiled = compile(code, "<student-solver>", "exec")
        exec(compiled, namespace)  # noqa: S102 - intentional, local student code
    except SyntaxError as exc:
        raise AI9414Error(
            code="solver_syntax_error",
            message=f"Your solver has a syntax error: {exc.msg} (line {exc.lineno}).",
            details={"line": exc.lineno, "offset": exc.offset},
        ) from exc
    except Exception as exc:  # noqa: BLE001 - surface any import-time failure
        raise AI9414Error(
            code="solver_import_error",
            message=f"Your solver failed to load: {exc}",
            details={"exception_type": type(exc).__name__},
        ) from exc
    return namespace


def _load_namespace_from_module(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AI9414Error(
            code="solver_file_not_found",
            message=f"Solver file '{path}' does not exist.",
        )
    module_spec = importlib.util.spec_from_file_location("ai9414_student_solver", path)
    if module_spec is None or module_spec.loader is None:
        raise AI9414Error(
            code="solver_import_error",
            message=f"Could not import solver file '{path}'.",
        )
    module = importlib.util.module_from_spec(module_spec)
    try:
        module_spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001
        raise AI9414Error(
            code="solver_import_error",
            message=f"Solver file failed to import: {exc}",
            details={"exception_type": type(exc).__name__},
        ) from exc
    return vars(module)


def run_student_solver(demo: str, request: dict[str, Any]) -> dict[str, Any]:
    """Execute student code for ``demo`` capturing stdout.

    Returns ``{"trace": <bundle dict>, "stdout": <captured prints>}``. On a
    structured error, the captured stdout is attached to ``error.details`` so
    the editor console can show whatever the solver printed before it failed.
    """

    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            trace = _execute_solver(demo, request)
    except AI9414Error as exc:
        exc.details = {**(exc.details or {}), "stdout": buffer.getvalue()}
        raise
    return {"trace": trace, "stdout": buffer.getvalue()}


def _execute_solver(demo: str, request: dict[str, Any]) -> dict[str, Any]:
    """Execute student code for ``demo`` and return a TraceBundle payload dict."""

    spec = get_spec(demo)

    code = request.get("code")
    if isinstance(code, str) and code.strip():
        namespace = _load_namespace_from_code(code)
    elif _PRELOADED_SOLVER is not None:
        namespace = _load_namespace_from_module(_PRELOADED_SOLVER)
    else:
        raise AI9414Error(
            code="invalid_action_payload",
            message="No solver code provided and no --solver file was loaded.",
        )

    problem = request.get(spec.problem_key)
    if not isinstance(problem, dict):
        raise AI9414Error(
            code="invalid_action_payload",
            message=f"Request must include a '{spec.problem_key}' object.",
        )
    options = request.get("options") or {}

    if spec.run is not None:
        bundle = spec.run(namespace, problem, options)
        return bundle.model_dump()

    # Default flow: single-argument solver returning a result dict.
    solver_fn = require_fn(namespace, spec.entry)
    try:
        validated_problem = spec.validate_payload(problem)
    except Exception as exc:  # noqa: BLE001
        raise AI9414Error(
            code="invalid_action_payload",
            message=f"Invalid {spec.problem_key} payload: {exc}",
        ) from exc

    result = call_solver(solver_fn, validated_problem)

    try:
        validated_result = spec.validate_result(result)
    except ValueError as exc:
        raise AI9414Error(code="invalid_solver_result", message=str(exc)) from exc

    bundle = spec.build_trace(validated_problem, validated_result)
    return bundle.model_dump()


def require_fn(namespace: dict[str, Any], name: str):
    """Fetch a callable the student must define, or raise a clear error."""

    fn = namespace.get(name)
    if not callable(fn):
        raise AI9414Error(
            code="solver_missing_function",
            message=f"Your code must define a function named '{name}'.",
        )
    return fn


def call_solver(fn, *args):
    """Call a student function, mapping any exception to a structured error.

    The real Python traceback (student frames only) is attached so the editor
    console can show native output, like running ``python solve.py``.
    """

    try:
        return fn(*args)
    except AI9414Error:
        raise
    except Exception as exc:  # noqa: BLE001
        raise AI9414Error(
            code="solver_runtime_error",
            message=f"{type(exc).__name__}: {exc}",
            details={"exception_type": type(exc).__name__, "traceback": _student_traceback(exc)},
        ) from exc


def _student_traceback(exc: BaseException) -> str:
    """Format a traceback limited to the student's own frames (drops our exec)."""

    frames = traceback.extract_tb(exc.__traceback__)
    student = [f for f in frames if f.filename in ("<student-solver>", "<string>") or "student" in f.filename]
    chosen = student or frames
    lines = ["Traceback (most recent call last):"]
    lines.extend(traceback.format_list(chosen))
    lines.append(f"{type(exc).__name__}: {exc}")
    return "".join(line if line.endswith("\n") else line + "\n" for line in lines)
