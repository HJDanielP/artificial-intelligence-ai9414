"""Live-solver wiring for the spatial graph DFS demo."""

from __future__ import annotations

from importlib import resources

from ai9414.core.solve import LiveSpec
from ai9414.graph_dfs.student import validate_graph_payload, validate_graph_solver_result
from ai9414.graph_dfs.trace import build_graph_dfs_trace_from_result


def _load_stub() -> str:
    return (
        resources.files("ai9414.graph_dfs.templates")
        .joinpath("solve_graph.py")
        .read_text(encoding="utf-8")
    )


def build_live_spec() -> LiveSpec:
    return LiveSpec(
        entry="solve_dfs",
        problem_key="graph",
        stub=_load_stub(),
        validate_payload=validate_graph_payload,
        validate_result=validate_graph_solver_result,
        build_trace=build_graph_dfs_trace_from_result,
    )
