"""Trace construction for the spatial graph BFS demo."""

from __future__ import annotations

import copy
from typing import Any

from ai9414.core.models import TraceBundle, TraceStep, TraceSummary
from ai9414.graph_bfs.models import GraphBfsExample
from ai9414.graph_bfs.solver import ALGORITHM_LABEL, ALGORITHM_NOTE, _edge_id, solve_graph_bfs
from ai9414.graph_dfs.models import SpatialGraphDefinition


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


def build_blank_graph_bfs_bundle(graph: SpatialGraphDefinition) -> TraceBundle:
    initial_state = {
        "example_title": "Generated graph",
        "example_subtitle": "Generate a graph, then use Solve with Python to run BFS on the same graph.",
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
        app_type="graph_bfs",
        trace_id="graph-bfs-empty",
        is_complete=True,
        initial_state=initial_state,
        summary=TraceSummary(step_count=0, result="ready"),
        steps=[],
    )


def build_graph_bfs_trace_from_definition(
    graph: SpatialGraphDefinition,
    *,
    title: str,
    subtitle: str,
) -> TraceBundle:
    result = solve_graph_bfs(graph)
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
        app_type="graph_bfs",
        trace_id=result.trace_id,
        is_complete=True,
        initial_state=initial_state,
        summary=TraceSummary(step_count=len(steps), result=result.status),
        steps=steps,
    )


def build_graph_bfs_trace(example: GraphBfsExample) -> TraceBundle:
    return build_graph_bfs_trace_from_definition(
        example.graph,
        title=example.title,
        subtitle=example.subtitle,
    )


def build_graph_bfs_trace_from_result(
    graph: dict[str, Any],
    result: dict[str, Any],
) -> TraceBundle:
    """Convert a student BFS result dict into a replayable TraceBundle.

    Ported from the former JS ``buildGraphBfsTraceFromBackend``. The student
    returns a compact trace (``start``/``expand``/``found``/``fail`` events with
    ``node``/``parent``/``depth``/``route``); this rebuilds the rich per-step
    snapshots (search-tree nodes, active path, explored edges) the frontend
    replays, identical in shape to the reference example trace.
    """

    graph_def = SpatialGraphDefinition.model_validate(graph)
    start = graph_def.start
    trace = result.get("trace", [])

    tree_nodes: dict[str, dict[str, Any]] = {}
    visible_tree_ids: list[str] = []
    tree_id_by_node: dict[str, str] = {}
    visited_order: list[str] = [start]
    active_tree_path: list[str] = ["t0"]
    explored_edge_ids: list[str] = []
    current_graph_path: list[str] = [start]
    current_tree_id: str | None = "t0"
    final_graph_path: list[str] = []
    search_status = "searching"
    counter = 1

    tree_nodes["t0"] = {
        "tree_id": "t0",
        "graph_node": start,
        "parent": None,
        "depth": 0,
        "path_cost": 0,
        "status": "active",
        "order": 0,
        "x": 0.5,
        "y": 0.12,
    }
    visible_tree_ids.append("t0")
    tree_id_by_node[start] = "t0"

    def _add_explored(left: str, right: str) -> None:
        edge_id = _edge_id(left, right)
        if edge_id not in explored_edge_ids:
            explored_edge_ids.append(edge_id)

    def snapshot() -> dict[str, Any]:
        return {
            "tree": {
                "nodes": [copy.deepcopy(tree_nodes[tree_id]) for tree_id in visible_tree_ids]
            },
            "search": {
                "active_tree_node": current_tree_id,
                "active_tree_path": list(active_tree_path),
                "current_graph_path": list(current_graph_path),
                "visited_order": list(visited_order),
                "dead_end_nodes": [],
                "final_graph_path": list(final_graph_path),
                "explored_graph_edges": [edge_id.split("--") for edge_id in explored_edge_ids],
                "explored_count": len(visited_order),
                "current_depth": max(len(current_graph_path) - 1, 0),
                "status": search_status,
                "found": bool(final_graph_path),
            },
        }

    raw_steps: list[dict[str, Any]] = []
    for step in trace:
        action = step.get("action")
        node_raw = step.get("node")
        node_id = node_raw if isinstance(node_raw, str) else None
        parent_raw = step.get("parent")
        parent = parent_raw if isinstance(parent_raw, str) else None
        route = list(step.get("route") or [])
        depth = int(step.get("depth") or 0)

        if action == "start":
            current_graph_path = route if route else [start]
            search_status = "searching"
        elif action == "expand":
            parent_id = tree_id_by_node.get(parent)
            tree_id = f"t{counter}"
            counter += 1
            tree_nodes[tree_id] = {
                "tree_id": tree_id,
                "graph_node": node_id,
                "parent": parent_id,
                "depth": depth,
                "path_cost": depth,
                "status": "active",
                "order": len(visible_tree_ids),
                "x": 0.0,
                "y": 0.0,
            }
            visible_tree_ids.append(tree_id)
            if node_id is not None:
                tree_id_by_node[node_id] = tree_id
            if parent and node_id:
                _add_explored(parent, node_id)
            current_graph_path = route
            if node_id is not None and node_id not in visited_order:
                visited_order.append(node_id)
            active_tree_path = [
                tree_id_by_node[route_node]
                for route_node in current_graph_path
                if route_node in tree_id_by_node
            ]
            current_tree_id = tree_id
            if parent_id and parent_id in tree_nodes:
                tree_nodes[parent_id]["status"] = "expanded"
            search_status = "searching"
        elif action == "found":
            if node_id is not None and node_id not in tree_id_by_node:
                parent_id = tree_id_by_node.get(parent)
                tree_id = f"t{counter}"
                counter += 1
                tree_nodes[tree_id] = {
                    "tree_id": tree_id,
                    "graph_node": node_id,
                    "parent": parent_id,
                    "depth": depth,
                    "path_cost": depth,
                    "status": "final",
                    "order": len(visible_tree_ids),
                    "x": 0.0,
                    "y": 0.0,
                }
                visible_tree_ids.append(tree_id)
                tree_id_by_node[node_id] = tree_id
            result_path = list(result.get("path") or [])
            current_graph_path = route if route else result_path
            final_graph_path = result_path if result_path else list(current_graph_path)
            active_tree_path = []
            for route_node in current_graph_path:
                route_tree_id = tree_id_by_node.get(route_node)
                if route_tree_id:
                    active_tree_path.append(route_tree_id)
                    tree_nodes[route_tree_id]["status"] = "final"
            current_tree_id = active_tree_path[-1] if active_tree_path else current_tree_id
            search_status = "goal found"
        elif action == "fail":
            current_graph_path = []
            active_tree_path = []
            current_tree_id = None
            search_status = "no path"

        raw_steps.append(
            {
                "event_type": action,
                "label": _bfs_label(action, node_id),
                "annotation": _bfs_annotation(action, node_id),
                "teaching_note": _bfs_teaching_note(action),
                "snapshot": snapshot(),
            }
        )

    layout = _layout_tree([tree_nodes[tree_id] for tree_id in visible_tree_ids])

    blank = build_blank_graph_bfs_bundle(graph_def)
    initial_state = copy.deepcopy(blank.initial_state)
    initial_state["example_title"] = "Live Python graph"
    initial_state["example_subtitle"] = "Trace returned by your Python BFS solver."
    for node in initial_state["tree"]["nodes"]:
        if node["tree_id"] in layout:
            node["x"], node["y"] = layout[node["tree_id"]]

    steps: list[TraceStep] = []
    for index, entry in enumerate(raw_steps):
        snap = copy.deepcopy(entry["snapshot"])
        for node in snap["tree"]["nodes"]:
            if node["tree_id"] in layout:
                node["x"], node["y"] = layout[node["tree_id"]]
        steps.append(
            TraceStep(
                index=index,
                event_type=entry["event_type"] or "update",
                label=entry["label"],
                annotation=entry["annotation"],
                teaching_note=entry["teaching_note"],
                state_patch=snap,
            )
        )

    return TraceBundle(
        app_type="graph_bfs",
        trace_id="graph-bfs-live",
        is_complete=True,
        initial_state=initial_state,
        summary=TraceSummary(step_count=len(steps), result=result.get("status", "found")),
        steps=steps,
    )


def _bfs_label(action: str | None, node_id: str | None) -> str:
    if action == "start":
        return "Start BFS"
    if action == "expand":
        return f"Expand {node_id}"
    if action == "found":
        return "Goal found"
    return "No path found"


def _bfs_annotation(action: str | None, node_id: str | None) -> str:
    if action == "start":
        return "The graph is ready. BFS starts at the start node."
    if action == "expand":
        return f"BFS discovers {node_id} and adds it to the next frontier layer."
    if action == "found":
        return "BFS has reached the goal and the successful path is now highlighted."
    return "BFS has exhausted the reachable graph without finding the goal."


def _bfs_teaching_note(action: str | None) -> str:
    if action == "found":
        return "In an unweighted graph, BFS reaches the goal on a shallowest path."
    return "The tree shows discovery order, while the graph view shows the route to the highlighted node."
