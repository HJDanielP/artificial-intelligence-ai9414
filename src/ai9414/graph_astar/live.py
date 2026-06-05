"""Live-solver wiring for the spatial graph A* demo."""

from __future__ import annotations

from importlib import resources

from ai9414.core.solve import LiveSpec
from ai9414.graph_astar.student import validate_graph_payload, validate_graph_astar_solver_result
from ai9414.graph_weighted_trace import build_weighted_trace_from_result


def _load_stub() -> str:
    return resources.files("ai9414.graph_astar.templates").joinpath("solve_graph.py").read_text(encoding="utf-8")


def build_live_spec() -> LiveSpec:
    return LiveSpec(
        entry="solve_astar",
        problem_key="graph",
        stub=_load_stub(),
        validate_payload=validate_graph_payload,
        validate_result=validate_graph_astar_solver_result,
        build_trace=lambda graph, result: build_weighted_trace_from_result(graph, result, algorithm="astar"),
    )
