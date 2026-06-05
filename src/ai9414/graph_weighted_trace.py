"""Shared result->TraceBundle converter for the weighted graph searches.

UCS, A*, and greedy best-first search share the same replay structure (a
route-keyed search tree, considered/relax/enqueue events, best/final paths).
This is a Python port of the former JS ``buildGraphUcs/AStar/GbfsTraceFromBackend``
functions, parameterised by algorithm.
"""

from __future__ import annotations

import copy
from typing import Any

from ai9414.core.models import TraceBundle, TraceStep, TraceSummary
from ai9414.search.models import WeightedGraph

# algorithm -> (app_type, module with build_blank_*_bundle + _layout_tree, label)
_ALGOS = {
    "ucs": ("graph_ucs", "ai9414.graph_ucs.trace", "build_blank_graph_ucs_bundle", "UCS"),
    "astar": ("graph_astar", "ai9414.graph_astar.trace", "build_blank_graph_astar_bundle", "A*"),
    "gbfs": ("graph_gbfs", "ai9414.graph_gbfs.trace", "build_blank_graph_gbfs_bundle", "greedy best-first"),
}


def _edge_id(u: str, v: str) -> str:
    return "--".join(sorted((u, v)))


def _route_key(route: list[str]) -> str:
    return "->".join(route)


def build_weighted_trace_from_result(
    graph: dict[str, Any],
    result: dict[str, Any],
    *,
    algorithm: str,
) -> TraceBundle:
    app_type, module_name, blank_fn_name, label = _ALGOS[algorithm]
    import importlib

    module = importlib.import_module(module_name)
    blank_bundle = getattr(module, blank_fn_name)
    layout_fn = getattr(module, "_layout_tree")

    graph_def = WeightedGraph.model_validate(graph)
    start = graph_def.start
    goal = graph_def.goal
    trace = result.get("trace", [])

    tree_nodes: dict[str, dict[str, Any]] = {}
    visible: list[str] = []
    tree_id_by_route: dict[str, str] = {}
    explored: list[str] = []
    visited_order: list[str] = [start]
    current_tree_id: str | None = "t0"
    current_path: list[str] = [start]
    active_tree_path: list[str] = ["t0"]
    best_path: list[str] = []
    final_path: list[str] = []
    best_tree_path: list[str] = []
    final_tree_path: list[str] = []
    current_cost = 0.0
    best_cost: float | None = None
    considered_edge: list[str] | None = None
    current_heuristic = 0.0
    current_priority = 0.0
    status = "searching"
    stats = {"expanded": 0, "relaxed": 0, "enqueued": 0}

    tree_nodes["t0"] = {
        "tree_id": "t0", "graph_node": start, "parent": None, "depth": 0, "path_cost": 0.0,
        "status": "active", "order": 0, "x": 0.5, "y": 0.12, "terminal": False,
    }
    visible.append("t0")
    tree_id_by_route[_route_key([start])] = "t0"

    def add_edge(a: str, b: str) -> None:
        eid = _edge_id(a, b)
        if eid not in explored:
            explored.append(eid)

    def ensure_tree_path(route: list[str], terminal: bool, path_cost: float | None) -> list[str]:
        ids: list[str] = []
        for index, node_id in enumerate(route):
            prefix = route[: index + 1]
            key = _route_key(prefix)
            tid = tree_id_by_route.get(key)
            if tid is None:
                parent_id = tree_id_by_route.get(_route_key(prefix[:-1]))
                parent_cost = float(tree_nodes[parent_id]["path_cost"]) if parent_id and parent_id in tree_nodes else 0.0
                is_last = index == len(route) - 1
                node_cost = path_cost if (is_last and path_cost is not None) else parent_cost
                tid = f"t{len(visible)}"
                tree_nodes[tid] = {
                    "tree_id": tid, "graph_node": node_id, "parent": parent_id, "depth": index,
                    "path_cost": node_cost, "status": "expanded", "order": len(visible),
                    "terminal": bool(terminal and is_last), "x": 0.0, "y": 0.0,
                }
                visible.append(tid)
                tree_id_by_route[key] = tid
            elif index == len(route) - 1 and path_cost is not None and tid in tree_nodes:
                tree_nodes[tid]["path_cost"] = path_cost
                tree_nodes[tid]["terminal"] = terminal
            ids.append(tid)
        return ids

    def snapshot() -> dict[str, Any]:
        return {
            "tree": {"nodes": [copy.deepcopy(tree_nodes[t]) for t in visible]},
            "search": {
                "active_tree_node": current_tree_id,
                "active_tree_path": list(active_tree_path),
                "best_tree_path": list(best_tree_path),
                "final_tree_path": list(final_tree_path),
                "current_graph_path": list(current_path),
                "best_graph_path": list(best_path),
                "final_graph_path": list(final_path),
                "visited_order": list(visited_order),
                "explored_graph_edges": [e.split("--") for e in explored],
                "considered_edge": list(considered_edge) if considered_edge else None,
                "current_cost": current_cost,
                "best_cost": best_cost,
                "current_heuristic": current_heuristic,
                "current_priority": current_priority,
                "explored_count": len(visited_order),
                "current_depth": max(len(current_path) - 1, 0),
                "status": status,
                "found": bool(final_path),
            },
            "stats": dict(stats),
        }

    raw_steps: list[dict[str, Any]] = []
    for step in trace:
        action = step.get("action")
        node_id = step.get("node") if isinstance(step.get("node"), str) else None
        parent = step.get("parent") if isinstance(step.get("parent"), str) else None
        cp = step.get("current_path")
        current_path = list(cp) if isinstance(cp, list) and cp else []
        current_cost = float(step.get("current_cost") or 0)
        best_path = list(step.get("best_path") or [])
        bc = step.get("best_cost")
        best_cost = None if bc is None else float(bc)
        ce = step.get("considered_edge")
        considered_edge = list(ce) if isinstance(ce, list) else None
        current_heuristic = float(step.get("heuristic") or 0)
        current_priority = float(step.get("priority") or 0)
        path_cost = float(step.get("path_cost") or current_cost)

        if action == "start":
            current_path = current_path or [start]
            active_tree_path = ensure_tree_path(current_path, False, 0.0)
            current_tree_id = active_tree_path[-1] if active_tree_path else "t0"
            status = "searching"
        elif action == "expand":
            stats["expanded"] += 1
            active_tree_path = ensure_tree_path(current_path, node_id == goal, path_cost)
            current_tree_id = active_tree_path[-1] if active_tree_path else current_tree_id
            if current_tree_id in tree_nodes:
                tree_nodes[current_tree_id]["status"] = "active"
            status = "searching"
        elif action == "consider_edge":
            active_tree_path = ensure_tree_path(current_path, False, path_cost)
            current_tree_id = active_tree_path[-1] if active_tree_path else current_tree_id
            if considered_edge:
                add_edge(considered_edge[0], considered_edge[1])
            status = "considering"
        elif action in ("relax", "enqueue"):
            stats["relaxed" if action == "relax" else "enqueued"] += 1
            active_tree_path = ensure_tree_path(current_path, node_id == goal, path_cost)
            current_tree_id = active_tree_path[-1] if active_tree_path else current_tree_id
            if parent and node_id:
                add_edge(parent, node_id)
            if node_id and node_id not in visited_order:
                visited_order.append(node_id)
            if current_tree_id in tree_nodes:
                tree_nodes[current_tree_id]["status"] = "active"
            status = "searching"
        elif action == "found":
            final_path = list(result.get("path") or best_path or current_path)
            best_path = list(final_path)
            rbc = result.get("best_cost")
            if rbc is not None:
                best_cost = float(rbc)
            active_tree_path = ensure_tree_path(final_path, True, best_cost if best_cost is not None else current_cost)
            current_tree_id = active_tree_path[-1] if active_tree_path else current_tree_id
            best_tree_path = list(active_tree_path)
            final_tree_path = list(active_tree_path)
            for tid in final_tree_path:
                if tid in tree_nodes:
                    tree_nodes[tid]["status"] = "final"
            status = "goal found"
        elif action == "fail":
            current_path = []
            active_tree_path = []
            current_tree_id = None
            considered_edge = None
            status = "no path"

        raw_steps.append({
            "event_type": action,
            "label": _label(algorithm, label, action, node_id, considered_edge),
            "annotation": _annotation(algorithm, action, node_id),
            "teaching_note": _note(algorithm, action),
            "snapshot": snapshot(),
        })

    layout = layout_fn([tree_nodes[t] for t in visible])
    initial_state = copy.deepcopy(blank_bundle(graph_def).initial_state)
    initial_state["example_title"] = "Live Python weighted graph"
    initial_state["example_subtitle"] = f"Trace returned by your Python {label} solver."
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
        app_type=app_type, trace_id=f"{app_type.replace('_', '-')}-live", is_complete=True,
        initial_state=initial_state,
        summary=TraceSummary(step_count=len(steps), result=result.get("status", "found")),
        steps=steps,
    )


def _label(algorithm, label, action, node_id, considered_edge):
    if action == "start":
        return f"Start {label}"
    if action == "expand":
        return f"Expand {node_id}"
    if action == "consider_edge":
        edge = f"{considered_edge[0]} -> {considered_edge[1]}" if considered_edge else "edge"
        return f"Consider {edge}"
    if action == "relax":
        return f"Relax {node_id}"
    if action == "enqueue":
        return f"Enqueue {node_id}"
    if action == "found":
        return "Goal found"
    return "No path found"


def _annotation(algorithm, action, node_id):
    if action == "start":
        return "The weighted graph is ready. Search starts at the start node."
    if action == "expand":
        return f"Expand {node_id} from the frontier."
    if action == "consider_edge":
        return "Check whether this edge improves the route to its neighbour."
    if action == "relax":
        return f"The route to {node_id} improves, so the frontier is updated with the new cost."
    if action == "enqueue":
        return f"{node_id} is added to the frontier."
    if action == "found":
        return "The goal has been removed from the frontier; the highlighted path is the result."
    return "The frontier was exhausted without reaching the goal."


def _note(algorithm, action):
    if action == "found":
        if algorithm == "gbfs":
            return "Greedy best-first follows the heuristic and is not guaranteed optimal."
        return "With positive edge costs, the first goal removed from the frontier is optimal."
    return "The tree may repeat graph nodes when a cheaper route to the same state is found later."
