"""Trace construction for the spatial graph DFS demo."""

from __future__ import annotations

import copy
from typing import Any

from ai9414.core.models import TraceBundle, TraceStep, TraceSummary
from ai9414.graph_dfs.models import GraphDfsExample, SpatialGraphDefinition
from ai9414.graph_dfs.solver import ALGORITHM_LABEL, ALGORITHM_NOTE, _edge_id, solve_graph_dfs


def _layout_tree(nodes: list[dict[str, Any]]) -> dict[str, tuple[float, float]]:
    children: dict[str | None, list[str]] = {}
    depth_map: dict[str, int] = {}
    order_map: dict[str, int] = {}
    for node in nodes:
        children.setdefault(node["parent"], []).append(node["tree_id"])
        depth_map[node["tree_id"]] = int(node["depth"])
        order_map[node["tree_id"]] = int(node["order"])

    for siblings in children.values():
        siblings.sort(key=lambda tree_id: order_map[tree_id])

    x_positions: dict[str, float] = {}
    cursor = 0

    def assign(tree_id: str) -> float:
        nonlocal cursor
        branch = children.get(tree_id, [])
        if not branch:
            cursor += 1
            x_positions[tree_id] = float(cursor)
            return x_positions[tree_id]
        child_positions = [assign(child_id) for child_id in branch]
        x_positions[tree_id] = sum(child_positions) / len(child_positions)
        return x_positions[tree_id]

    for root_id in children.get(None, []):
        assign(root_id)

    max_x = max(x_positions.values(), default=1.0)
    max_depth = max(depth_map.values(), default=0)
    return {
        tree_id: (
            0.08 + ((x - 1) / max(max_x - 1, 1)) * 0.84,
            0.12 + (depth_map[tree_id] / max(max_depth, 1)) * 0.76,
        )
        for tree_id, x in x_positions.items()
    }


def build_blank_graph_dfs_bundle(graph: SpatialGraphDefinition) -> TraceBundle:
    initial_state = {
        "example_title": "Generated graph",
        "example_subtitle": "Generate a graph, then use Solve with Python to run DFS on the same graph.",
        "algorithm_label": ALGORITHM_LABEL,
        "algorithm_note": ALGORITHM_NOTE,
        "goal_label": "Find any path from start to goal",
        "graph": graph.model_dump(),
        "tree": {
            "nodes": [
                {
                    "tree_id": "t0",
                    "graph_node": graph.start,
                    "parent": None,
                    "depth": 0,
                    "path_cost": 0,
                    "status": "active",
                    "order": 0,
                    "x": 0.5,
                    "y": 0.12,
                }
            ]
        },
        "search": {
            "active_tree_node": "t0",
            "active_tree_path": ["t0"],
            "current_graph_path": [graph.start],
            "visited_order": [graph.start],
            "dead_end_nodes": [],
            "final_graph_path": [],
            "explored_graph_edges": [],
            "explored_count": 1,
            "current_depth": 0,
            "status": "searching",
            "found": False,
        },
    }
    return TraceBundle(
        app_type="graph_dfs",
        trace_id="graph-dfs-empty",
        is_complete=True,
        initial_state=initial_state,
        summary=TraceSummary(step_count=0, result="ready"),
        steps=[],
    )


def build_graph_dfs_trace_from_definition(
    graph: SpatialGraphDefinition,
    *,
    title: str,
    subtitle: str,
) -> TraceBundle:
    result = solve_graph_dfs(graph)
    all_tree_nodes = (
        result.raw_steps[-1].snapshot["tree"]["nodes"]
        if result.raw_steps
        else result.initial_state["tree"]["nodes"]
    )
    layout = _layout_tree(all_tree_nodes)

    initial_state = copy.deepcopy(result.initial_state)
    initial_state["example_title"] = title
    initial_state["example_subtitle"] = subtitle
    for node in initial_state["tree"]["nodes"]:
        node["x"], node["y"] = layout[node["tree_id"]]

    steps: list[TraceStep] = []
    for index, raw_step in enumerate(result.raw_steps):
        snapshot = copy.deepcopy(raw_step.snapshot)
        for node in snapshot["tree"]["nodes"]:
            node["x"], node["y"] = layout[node["tree_id"]]
        steps.append(
            TraceStep(
                index=index,
                event_type=raw_step.event_type,
                label=raw_step.label,
                annotation=raw_step.annotation,
                teaching_note=raw_step.teaching_note,
                state_patch=snapshot,
            )
        )

    return TraceBundle(
        app_type="graph_dfs",
        trace_id=result.trace_id,
        is_complete=True,
        initial_state=initial_state,
        summary=TraceSummary(step_count=len(steps), result=result.status),
        steps=steps,
    )


def build_graph_dfs_trace_from_result(
    graph: dict[str, Any],
    result: dict[str, Any],
) -> TraceBundle:
    """Convert a student DFS result (start/expand/backtrack/found/fail events
    with ``stack``) into a replayable TraceBundle. Ported from the former JS
    ``buildGraphDfsTraceFromBackend``."""

    graph_def = SpatialGraphDefinition.model_validate(graph)
    start = graph_def.start
    trace = result.get("trace", [])

    tree_nodes: dict[str, dict[str, Any]] = {}
    visible: list[str] = []
    tree_id_by_node: dict[str, str] = {}
    dead_ends: list[str] = []
    dead_end_set: set[str] = set()
    visited_order: list[str] = [start]
    active_tree_path: list[str] = ["t0"]
    explored: list[str] = []
    current_graph_path: list[str] = [start]
    current_tree_id: str | None = "t0"
    final_graph_path: list[str] = []
    status = "searching"
    counter = 1

    tree_nodes["t0"] = {
        "tree_id": "t0", "graph_node": start, "parent": None, "depth": 0,
        "path_cost": 0, "status": "active", "order": 0, "x": 0.5, "y": 0.12,
    }
    visible.append("t0")
    tree_id_by_node[start] = "t0"

    def add_edge(a: str, b: str) -> None:
        eid = _edge_id(a, b)
        if eid not in explored:
            explored.append(eid)

    def set_active_path(route: list[str]) -> None:
        active_tree_path.clear()
        for node in route:
            tid = tree_id_by_node.get(node)
            if tid:
                active_tree_path.append(tid)

    def snapshot() -> dict[str, Any]:
        return {
            "tree": {"nodes": [copy.deepcopy(tree_nodes[t]) for t in visible]},
            "search": {
                "active_tree_node": current_tree_id,
                "active_tree_path": list(active_tree_path),
                "current_graph_path": list(current_graph_path),
                "visited_order": list(visited_order),
                "dead_end_nodes": list(dead_ends),
                "final_graph_path": list(final_graph_path),
                "explored_graph_edges": [e.split("--") for e in explored],
                "explored_count": len(visited_order),
                "current_depth": max(len(current_graph_path) - 1, 0),
                "status": status,
                "found": bool(final_graph_path),
            },
        }

    raw_steps: list[dict[str, Any]] = []
    for step in trace:
        action = step.get("action")
        node_id = step.get("node") if isinstance(step.get("node"), str) else None
        parent = step.get("parent") if isinstance(step.get("parent"), str) else None
        stack = list(step.get("stack") or [])
        depth = int(step.get("depth") or 0)

        if action == "start":
            current_graph_path = stack or [start]
            status = "searching"
        elif action == "expand":
            parent_id = tree_id_by_node.get(parent)
            tid = f"t{counter}"
            counter += 1
            tree_nodes[tid] = {
                "tree_id": tid, "graph_node": node_id, "parent": parent_id, "depth": depth,
                "path_cost": depth, "status": "active", "order": len(visible), "x": 0.0, "y": 0.0,
            }
            visible.append(tid)
            if node_id is not None:
                tree_id_by_node[node_id] = tid
            if parent and node_id:
                add_edge(parent, node_id)
            current_graph_path = stack
            if node_id is not None and node_id not in visited_order:
                visited_order.append(node_id)
            set_active_path(current_graph_path)
            current_tree_id = tid
            if parent_id and parent_id in tree_nodes:
                tree_nodes[parent_id]["status"] = "expanded"
            status = "searching"
        elif action == "backtrack":
            current_graph_path = stack
            set_active_path(current_graph_path)
            bt = tree_id_by_node.get(node_id)
            if bt and bt in tree_nodes:
                tree_nodes[bt]["status"] = "backtracked"
            if node_id and node_id not in dead_end_set:
                dead_end_set.add(node_id)
                dead_ends.append(node_id)
            current_tree_id = active_tree_path[-1] if active_tree_path else "t0"
            if current_tree_id in tree_nodes:
                tree_nodes[current_tree_id]["status"] = "active"
            status = "backtracking"
        elif action == "found":
            if node_id is not None and node_id not in tree_id_by_node:
                parent_id = tree_id_by_node.get(parent)
                tid = f"t{counter}"
                counter += 1
                tree_nodes[tid] = {
                    "tree_id": tid, "graph_node": node_id, "parent": parent_id, "depth": depth,
                    "path_cost": depth, "status": "final", "order": len(visible), "x": 0.0, "y": 0.0,
                }
                visible.append(tid)
                tree_id_by_node[node_id] = tid
            current_graph_path = stack
            final_graph_path = list(stack)
            active_tree_path.clear()
            for node in current_graph_path:
                tid = tree_id_by_node.get(node)
                if tid:
                    active_tree_path.append(tid)
                    tree_nodes[tid]["status"] = "final"
            current_tree_id = active_tree_path[-1] if active_tree_path else current_tree_id
            status = "goal found"
        elif action == "fail":
            current_graph_path = []
            active_tree_path.clear()
            current_tree_id = None
            status = "no path"

        raw_steps.append({
            "event_type": action,
            "label": _dfs_label(action, node_id),
            "annotation": _dfs_annotation(action, node_id),
            "teaching_note": _dfs_teaching_note(action),
            "snapshot": snapshot(),
        })

    layout = _layout_tree([tree_nodes[t] for t in visible])
    initial_state = copy.deepcopy(build_blank_graph_dfs_bundle(graph_def).initial_state)
    initial_state["example_title"] = "Live Python graph"
    initial_state["example_subtitle"] = "Trace returned by your Python DFS solver."
    for node in initial_state["tree"]["nodes"]:
        if node["tree_id"] in layout:
            node["x"], node["y"] = layout[node["tree_id"]]

    steps: list[TraceStep] = []
    for index, entry in enumerate(raw_steps):
        snap = copy.deepcopy(entry["snapshot"])
        for node in snap["tree"]["nodes"]:
            if node["tree_id"] in layout:
                node["x"], node["y"] = layout[node["tree_id"]]
        steps.append(TraceStep(
            index=index, event_type=entry["event_type"] or "update", label=entry["label"],
            annotation=entry["annotation"], teaching_note=entry["teaching_note"], state_patch=snap,
        ))

    return TraceBundle(
        app_type="graph_dfs", trace_id="graph-dfs-live", is_complete=True,
        initial_state=initial_state,
        summary=TraceSummary(step_count=len(steps), result=result.get("status", "found")),
        steps=steps,
    )


def _dfs_label(action, node_id):
    return {"start": "Start DFS", "expand": f"Expand {node_id}",
            "backtrack": f"Backtrack from {node_id}", "found": "Goal found"}.get(action, "No path found")


def _dfs_annotation(action, node_id):
    return {
        "start": "The graph is ready. DFS starts at the start node.",
        "expand": f"DFS steps into {node_id} and keeps exploring.",
        "backtrack": f"DFS retreats from {node_id} after exhausting that branch.",
        "found": "DFS has reached the goal and the successful path is now highlighted.",
    }.get(action, "DFS has exhausted the reachable graph without finding the goal.")


def _dfs_teaching_note(action):
    if action == "found":
        return "Plain DFS stops as soon as it finds any goal path."
    return "The tree shows search history, while the graph view shows movement through the original problem."


def build_graph_dfs_trace(example: GraphDfsExample) -> TraceBundle:
    return build_graph_dfs_trace_from_definition(
        example.graph,
        title=example.title,
        subtitle=example.subtitle,
    )
