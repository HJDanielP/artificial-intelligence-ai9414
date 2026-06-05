"""Live-solver wiring for the CSP map-colouring demo."""

from __future__ import annotations

from importlib import resources
from typing import Any

from ai9414.core.errors import AI9414Error
from ai9414.core.solve import LiveSpec, call_solver, require_fn
from ai9414.csp.models import CspProblem
from ai9414.csp.student import validate_csp_payload, validate_csp_solver_result
from ai9414.csp.trace import build_csp_trace_from_events


def _load_stub() -> str:
    return resources.files("ai9414.csp.templates").joinpath("solve_csp.py").read_text(encoding="utf-8")


def _run(namespace: dict[str, Any], problem: dict[str, Any], options: dict[str, Any]):
    fn = require_fn(namespace, "solve_csp")
    try:
        validated_problem = validate_csp_payload(problem)
        problem_model = CspProblem.model_validate(validated_problem)
    except Exception as exc:  # noqa: BLE001
        raise AI9414Error(code="invalid_action_payload", message=f"Invalid CSP payload: {exc}") from exc

    result = call_solver(fn, validated_problem, dict(options))

    try:
        validated = validate_csp_solver_result(result)
    except ValueError as exc:
        raise AI9414Error(code="invalid_solver_result", message=str(exc)) from exc

    return build_csp_trace_from_events(
        problem_model,
        events=validated["events"],
        status=validated["status"],
        assignment=validated["assignment"],
        stats=validated["stats"],
        title=problem_model.title or "Live Python CSP",
        subtitle="Trace returned by your Python CSP solver.",
        trace_id="csp-live",
        live_trace=True,
    )


def build_live_spec() -> LiveSpec:
    return LiveSpec(entry="solve_csp", problem_key="csp_problem", stub=_load_stub(), run=_run)
