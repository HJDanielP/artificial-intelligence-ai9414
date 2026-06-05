"""Live-solver wiring for the reasoning-with-uncertainty demo.

Unlike the other demos, the student defines three belief-update functions; the
existing ``build_uncertainty_trace_from_problem`` drives them over the scenario.
"""

from __future__ import annotations

from importlib import resources
from typing import Any

from ai9414.core.errors import AI9414Error
from ai9414.core.solve import LiveSpec, require_fn
from ai9414.uncertainty.models import UncertaintyProblem
from ai9414.uncertainty.student import validate_uncertainty_payload
from ai9414.uncertainty.trace import build_uncertainty_trace_from_problem


def _load_stub() -> str:
    return (
        resources.files("ai9414.uncertainty.templates")
        .joinpath("solve_uncertainty.py")
        .read_text(encoding="utf-8")
    )


def _run(namespace: dict[str, Any], problem: dict[str, Any], options: dict[str, Any]):
    predict_fn = require_fn(namespace, "predict_belief")
    update_fn = require_fn(namespace, "update_belief")
    step_fn = require_fn(namespace, "bayes_filter_step")
    try:
        validated = validate_uncertainty_payload(problem)
        model = UncertaintyProblem.model_validate(validated)
    except Exception as exc:  # noqa: BLE001
        raise AI9414Error(code="invalid_action_payload", message=f"Invalid uncertainty payload: {exc}") from exc

    try:
        return build_uncertainty_trace_from_problem(
            model,
            title=model.title or "Live Python Bayes filter",
            subtitle="Trace returned by your Python Bayes filter.",
            predict_fn=predict_fn,
            update_fn=update_fn,
            bayes_step_fn=step_fn,
            trace_id="uncertainty-live",
        )
    except (NotImplementedError, ValueError) as exc:
        raise AI9414Error(code="invalid_solver_result", message=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise AI9414Error(
            code="solver_runtime_error",
            message=f"Your belief functions raised an exception: {exc}",
            details={"exception_type": type(exc).__name__},
        ) from exc


def build_live_spec() -> LiveSpec:
    return LiveSpec(entry="bayes_filter_step", problem_key="uncertainty_problem", stub=_load_stub(), run=_run)
