"""Starter code for the spatial graph uniform-cost search exercise.

Implement ``solve_ucs(graph)`` using a cost-ordered priority queue (heapq).

Return:
    {"algorithm": "ucs", "status": "found"|"not_found", "trace": [...],
     "path": [...], "best_cost": <float|None>, "visited_order": [...]}

Trace events: start, expand, consider_edge, relax, found, fail. Each carries
"step", "action", "node", "parent", "depth", "path_cost", "current_path",
"current_cost", "best_path", "best_cost", "considered_edge".
"""

from __future__ import annotations

from typing import Any


def solve_ucs(graph: dict[str, Any]) -> dict[str, Any]:
    # TODO: run uniform-cost search with heapq and record the trace.
    return {
        "algorithm": "ucs",
        "status": "error",
        "message": "Implement solve_ucs with a cost-ordered priority queue.",
        "trace": [],
        "path": [],
        "best_cost": None,
        "visited_order": [str(graph["start"])],
    }
