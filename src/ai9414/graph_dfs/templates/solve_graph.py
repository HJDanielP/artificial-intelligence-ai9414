"""Starter code for the spatial graph DFS exercise.

Implement ``solve_dfs(graph)``. The app passes the current graph in, runs your
function, validates the result, and replays your trace.

Graph dict: {"nodes": [{"id": "S", ...}], "edges": [{"u": "S", "v": "A"}],
"start": "S", "goal": "G"}.

Return:
    {"algorithm": "dfs", "status": "found"|"not_found", "trace": [...],
     "path": [...], "visited_order": [...]}

Each trace event: {"step", "action", "node", "parent", "depth", "stack"},
where ``stack`` is the current DFS stack (path from start to the node).
Actions: start, expand, backtrack, found, fail.
"""

from __future__ import annotations

from typing import Any


def build_adjacency(graph: dict[str, Any]) -> dict[str, list[str]]:
    adj: dict[str, list[str]] = {str(n["id"]): [] for n in graph["nodes"]}
    for e in graph["edges"]:
        u, v = str(e["u"]), str(e["v"])
        adj[u].append(v)
        adj[v].append(u)
    for k in adj:
        adj[k].sort()
    return adj


def solve_dfs(graph: dict[str, Any]) -> dict[str, Any]:
    start = str(graph["start"])
    goal = str(graph["goal"])
    adjacency = build_adjacency(graph)
    _ = (goal, adjacency)

    # TODO: replace with a full iterative DFS that records the trace.
    return {
        "algorithm": "dfs",
        "status": "error",
        "message": "Implement solve_dfs with a full depth-first search.",
        "trace": [{"step": 0, "action": "start", "node": start, "parent": None, "depth": 0, "stack": [start]}],
        "path": [],
        "visited_order": [start],
    }
