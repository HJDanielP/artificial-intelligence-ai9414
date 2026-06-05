"""Live-solver wiring for the STRIPS planning demo."""

from __future__ import annotations

from importlib import resources
from typing import Any

from ai9414.core.errors import AI9414Error
from ai9414.core.solve import LiveSpec, call_solver, require_fn
from ai9414.strips.models import StripsProblem
from ai9414.strips.solver import validate_action_plan
from ai9414.strips.student import validate_strips_payload, validate_strips_solver_result
from ai9414.strips.trace import build_strips_trace_from_validated_plan


def _load_stub() -> str:
    return (
        resources.files("ai9414.strips.templates")
        .joinpath("solve_strips.py")
        .read_text(encoding="utf-8")
    )


def _run(namespace: dict[str, Any], problem: dict[str, Any], options: dict[str, Any]):
    fn = require_fn(namespace, "solve_strips")
    try:
        validated_problem = validate_strips_payload(problem)
        problem_model = StripsProblem.model_validate(validated_problem)
    except Exception as exc:  # noqa: BLE001
        raise AI9414Error(code="invalid_action_payload", message=f"Invalid STRIPS payload: {exc}") from exc

    result = call_solver(fn, validated_problem)

    try:
        validated = validate_strips_solver_result(result)
        validated_plan = validate_action_plan(problem_model, validated["plan"])
    except ValueError as exc:
        raise AI9414Error(code="invalid_solver_result", message=str(exc)) from exc

    return build_strips_trace_from_validated_plan(
        problem_model,
        plan=validated_plan,
        status=validated["status"],
        stats=validated["stats"],
        title=problem_model.title or "Live Python STRIPS",
        subtitle="Trace returned by your Python planner.",
        trace_id="strips-live",
    )


def build_live_spec() -> LiveSpec:
    return LiveSpec(entry="solve_strips", problem_key="strips_problem", stub=_load_stub(), run=_run)
