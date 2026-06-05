"""Starter code for the spatial graph A* search exercise.

Implement ``solve_astar(graph)``: a priority queue ordered by f = g + h, where
h is the straight-line distance to the goal (use ``heuristic_to_goal``).

Return:
    {"algorithm": "astar", "status": "found"|"not_found", "trace": [...],
     "path": [...], "best_cost": <float|None>, "visited_order": [...]}

Trace events: start, expand, consider_edge, relax, found, fail. A* entries also
carry "heuristic" and "priority".
"""

from __future__ import annotations

from typing import Any


def solve_astar(graph: dict[str, Any]) -> dict[str, Any]:
    # TODO: run A* with f = g + h and record the trace.
    return {
        "algorithm": "astar",
        "status": "error",
        "message": "Implement solve_astar with an f = g + h priority queue.",
        "trace": [],
        "path": [],
        "best_cost": None,
        "visited_order": [str(graph["start"])],
    }
