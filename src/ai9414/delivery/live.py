"""Live-solver wiring for the office delivery DFS demo.

Delivery reuses the labyrinth grid contract (validators + grid-DFS trace
builder), rendered as an office floor (app_type "delivery").
"""

from __future__ import annotations

from importlib import resources

from ai9414.core.solve import LiveSpec
from ai9414.labyrinth.student import validate_labyrinth_payload, validate_labyrinth_solver_result
from ai9414.labyrinth.trace import build_labyrinth_trace_from_result


def _load_stub() -> str:
    return resources.files("ai9414.delivery.templates").joinpath("solve_delivery.py").read_text(encoding="utf-8")


def build_live_spec() -> LiveSpec:
    return LiveSpec(
        entry="solve_dfs",
        problem_key="labyrinth",
        stub=_load_stub(),
        validate_payload=validate_labyrinth_payload,
        validate_result=validate_labyrinth_solver_result,
        build_trace=lambda lab, result: build_labyrinth_trace_from_result(lab, result, app_type="delivery"),
    )
