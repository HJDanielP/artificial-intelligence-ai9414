"""Starter code for the spatial graph BFS exercise.

Implement ``solve_bfs`` below. The app passes the current graph in, runs your
function, validates the result, and replays your trace in the browser — there
is nothing else to wire up.

The graph dictionary looks like:
    {
        "nodes": [{"id": "S", "x": 0.1, "y": 0.2}, ...],
        "edges": [{"u": "S", "v": "A"}, ...],
        "start": "S",
        "goal": "G",
    }

``solve_bfs`` must return:
    {
        "algorithm": "bfs",
        "status": "found" | "not_found",
        "trace": [ ... trace events ... ],
        "path": ["S", "A", "G"],            # empty list when not_found
        "visited_order": ["S", "A", "B", "G"],
    }

Each trace event is a dict:
    {"step": 0, "action": "start", "node": "S", "parent": None,
     "depth": 0, "route": ["S"]}

Trace actions: "start", "expand", "found", "fail".
- start:  emit once at the start node
- expand: emit when BFS discovers a new node (route = path from start to it)
- found:  emit once when the goal is reached
- fail:   emit once if the frontier empties with no goal path
"""

from __future__ import annotations

from collections import deque
from typing import Any


def build_adjacency(graph: dict[str, Any]) -> dict[str, list[str]]:
    """Build a sorted adjacency list from the graph dictionary."""

    adjacency: dict[str, list[str]] = {str(node["id"]): [] for node in graph["nodes"]}
    for edge in graph["edges"]:
        left, right = str(edge["u"]), str(edge["v"])
        adjacency[left].append(right)
        adjacency[right].append(left)
    for node_id in adjacency:
        adjacency[node_id].sort()
    return adjacency


def reconstruct_path(parents: dict[str, str | None], goal: str) -> list[str]:
    """Reconstruct the path from the start node to ``goal``."""

    path: list[str] = []
    current: str | None = goal
    while current is not None:
        path.append(current)
        current = parents[current]
    path.reverse()
    return path


def make_event(
    step: int,
    action: str,
    node: str | None,
    parent: str | None,
    depth: int,
    route: list[str],
) -> dict[str, Any]:
    """Build one trace event in the format the replay expects."""

    return {
        "step": step,
        "action": action,
        "node": node,
        "parent": parent,
        "depth": depth,
        "route": list(route),
    }


def solve_bfs(graph: dict[str, Any]) -> dict[str, Any]:
    """Solve the graph with breadth-first search. Replace the TODO with BFS."""

    start = str(graph["start"])
    goal = str(graph["goal"])
    adjacency = build_adjacency(graph)
    _ = (goal, adjacency, deque)  # available helpers; remove once you use them

    # TODO: replace the placeholder below with a complete iterative BFS.
    trace = [make_event(0, "start", start, None, 0, [start])]
    return {
        "algorithm": "bfs",
        "status": "error",
        "message": "Replace the placeholder in solve_bfs with your BFS implementation.",
        "trace": trace,
        "path": [],
        "visited_order": [start],
    }
