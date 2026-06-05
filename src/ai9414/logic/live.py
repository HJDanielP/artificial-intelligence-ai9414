"""Live-solver wiring for the propositional logic DPLL demo."""

from __future__ import annotations

from importlib import resources
from typing import Any

from ai9414.core.errors import AI9414Error
from ai9414.core.solve import LiveSpec, call_solver, require_fn
from ai9414.logic.student import validate_dpll_solver_result, validate_logic_payload
from ai9414.logic.trace import build_logic_trace_from_result


def _load_stub() -> str:
    return resources.files("ai9414.logic.templates").joinpath("solve_dpll.py").read_text(encoding="utf-8")


def _run(namespace: dict[str, Any], problem: dict[str, Any], options: dict[str, Any]):
    fn = require_fn(namespace, "solve_dpll")
    try:
        validated_problem = validate_logic_payload(problem)
    except Exception as exc:  # noqa: BLE001
        raise AI9414Error(code="invalid_action_payload", message=f"Invalid logic payload: {exc}") from exc

    result = call_solver(fn, validated_problem, dict(options))

    try:
        validated = validate_dpll_solver_result(result)
    except ValueError as exc:
        raise AI9414Error(code="invalid_solver_result", message=str(exc)) from exc

    return build_logic_trace_from_result(validated_problem, validated)


def build_live_spec() -> LiveSpec:
    return LiveSpec(entry="solve_dpll", problem_key="logic_problem", stub=_load_stub(), run=_run)
