"""Starter code for the office delivery DFS exercise.

Same contract as the labyrinth: implement ``solve_dfs(layout)`` over an office
grid (dict with "rows", "cols", "grid", "start" [row, col], "exit" [row, col]).
'#' is a wall. Return a DFS result the app replays on the office floor.

Return:
    {"algorithm": "dfs", "status": "found"|"not_found", "trace": [...],
     "path": [[r, c], ...], "visited_order": [[r, c], ...]}

Trace events: {"step", "action", "cell", "parent", "depth", "stack"};
actions start, expand, backtrack, found, fail. Try the action order configured
for the demo (straight/left/right) for a faithful trace.
"""

from __future__ import annotations

from typing import Any


def solve_dfs(layout: dict[str, Any]) -> dict[str, Any]:
    start = (int(layout["start"][0]), int(layout["start"][1]))
    # TODO: run DFS from the robot to the delivery location and record the trace.
    return {
        "algorithm": "dfs",
        "status": "error",
        "message": "Implement solve_dfs to route the robot to the delivery location.",
        "trace": [{"step": 0, "action": "start", "cell": [start[0], start[1]], "parent": None, "depth": 0, "stack": [[start[0], start[1]]]}],
        "path": [],
        "visited_order": [[start[0], start[1]]],
    }
