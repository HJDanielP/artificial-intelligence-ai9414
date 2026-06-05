"""Live-solver wiring for the spatial graph BFS demo.

Connects the student-facing validators and the result→trace converter into a
:class:`~ai9414.core.solve.LiveSpec` consumed by ``POST /api/graph-bfs/solve``.
"""

from __future__ import annotations

from importlib import resources

from ai9414.core.solve import LiveSpec
from ai9414.graph_bfs.student import (
    validate_graph_bfs_solver_result,
    validate_graph_payload,
)
from ai9414.graph_bfs.trace import build_graph_bfs_trace_from_result


def _load_stub() -> str:
    return (
        resources.files("ai9414.graph_bfs.templates")
        .joinpath("solve_graph.py")
        .read_text(encoding="utf-8")
    )


def build_live_spec() -> LiveSpec:
    return LiveSpec(
        entry="solve_bfs",
        validate_payload=validate_graph_payload,
        validate_result=validate_graph_bfs_solver_result,
        build_trace=build_graph_bfs_trace_from_result,
        problem_key="graph",
        stub=_load_stub(),
    )
