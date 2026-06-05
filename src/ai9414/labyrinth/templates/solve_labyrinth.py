"""Starter code for the labyrinth DFS exercise.

Implement ``solve_dfs(labyrinth)``. The maze is a dict with "rows", "cols",
"grid" (list of strings; '#' = wall), "start" [row, col] and "exit" [row, col].

Return:
    {"algorithm": "dfs", "status": "found"|"not_found", "trace": [...],
     "path": [[r, c], ...], "visited_order": [[r, c], ...]}

Each trace event: {"step", "action", "cell": [r, c], "parent": [r, c]|None,
"depth", "stack": [[r, c], ...]}. Actions: start, expand, backtrack, found, fail.
Move order is up, right, down, left.
"""

from __future__ import annotations

from typing import Any

Cell = tuple[int, int]


def neighbours(labyrinth: dict[str, Any], cell: Cell) -> list[Cell]:
    r, c = cell
    grid, rows, cols = labyrinth["grid"], labyrinth["rows"], labyrinth["cols"]
    out: list[Cell] = []
    for nr, nc in [(r - 1, c), (r, c + 1), (r + 1, c), (r, c - 1)]:
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != "#":
            out.append((nr, nc))
    return out


def solve_dfs(labyrinth: dict[str, Any]) -> dict[str, Any]:
    start = (int(labyrinth["start"][0]), int(labyrinth["start"][1]))
    _ = neighbours
    # TODO: run iterative DFS from start to exit and record the trace.
    return {
        "algorithm": "dfs",
        "status": "error",
        "message": "Implement solve_dfs with a full depth-first search of the maze.",
        "trace": [{"step": 0, "action": "start", "cell": [start[0], start[1]], "parent": None, "depth": 0, "stack": [[start[0], start[1]]]}],
        "path": [],
        "visited_order": [[start[0], start[1]]],
    }
