"""Starter code for the spatial graph greedy best-first search exercise.

Implement ``solve_gbfs(graph)``: a priority queue ordered only by the heuristic
h (straight-line distance to the goal, via ``heuristic_to_goal``).

Return:
    {"algorithm": "gbfs", "status": "found"|"not_found", "trace": [...],
     "path": [...], "visited_order": [...]}

Trace events: start, expand, consider_edge, enqueue, found, fail. Entries carry
"heuristic" (and "path_cost"/"current_path" for the replay).
"""

from __future__ import annotations

from typing import Any


def solve_gbfs(graph: dict[str, Any]) -> dict[str, Any]:
    # TODO: run greedy best-first search ordered by the heuristic.
    return {
        "algorithm": "gbfs",
        "status": "error",
        "message": "Implement solve_gbfs ordered by the heuristic to the goal.",
        "trace": [],
        "path": [],
        "path_cost": None,
        "visited_order": [str(graph["start"])],
    }
