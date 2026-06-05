"""Trace construction for the labyrinth demo."""

from __future__ import annotations

import copy
from typing import Any

from ai9414.core.models import TraceBundle, TraceStep, TraceSummary
from ai9414.labyrinth.models import LabyrinthDefinition, LabyrinthExample
from ai9414.labyrinth.solver import ALGORITHM_LABEL, ALGORITHM_NOTE, solve_labyrinth


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


def build_empty_labyrinth_bundle(labyrinth: LabyrinthDefinition) -> TraceBundle:
    initial_state = {
        "example_title": "Generated labyrinth",
        "example_subtitle": "Generate a maze, then use Solve with Python to run DFS on the same maze.",
        "algorithm_label": ALGORITHM_LABEL,
        "algorithm_note": ALGORITHM_NOTE,
        "goal_label": "Find any path from start to exit",
        "labyrinth": labyrinth.model_dump(),
        "tree": {
            "nodes": [
                {
                    "tree_id": "t0",
                    "graph_node": f"({labyrinth.start[0]}, {labyrinth.start[1]})",
                    "cell": list(labyrinth.start),
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
            "current_route": [list(labyrinth.start)],
            "visited_order": [list(labyrinth.start)],
            "dead_end_cells": [],
            "final_path": [],
            "explored_count": 1,
            "current_depth": 0,
            "status": "searching",
            "found": False,
        },
    }
    return TraceBundle(
        app_type="labyrinth",
        trace_id="labyrinth-empty",
        is_complete=True,
        initial_state=initial_state,
        summary=TraceSummary(step_count=0, result="ready"),
        steps=[],
    )


def build_labyrinth_trace_from_definition(
    labyrinth: LabyrinthDefinition,
    *,
    title: str,
    subtitle: str,
) -> TraceBundle:
    result = solve_labyrinth(labyrinth)
    all_tree_nodes = result.raw_steps[-1].snapshot["tree"]["nodes"] if result.raw_steps else result.initial_state["tree"]["nodes"]
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
        app_type="labyrinth",
        trace_id=result.trace_id,
        is_complete=True,
        initial_state=initial_state,
        summary=TraceSummary(step_count=len(steps), result=result.status),
        steps=steps,
    )


def build_labyrinth_trace_from_result(
    labyrinth: dict[str, Any],
    result: dict[str, Any],
    *,
    app_type: str = "labyrinth",
) -> TraceBundle:
    """Convert a student grid-DFS result (cells + stack) into a TraceBundle.

    Shared by the labyrinth and delivery demos. Ported from the former JS
    ``buildLabyrinthTraceFromBackend``.
    """

    lab = LabyrinthDefinition.model_validate(labyrinth)
    delivery = app_type == "delivery"
    start = list(lab.start)
    key = lambda c: f"{c[0]},{c[1]}"

    tree_nodes: dict[str, dict[str, Any]] = {}
    visible: list[str] = []
    tree_id_by_cell: dict[str, str] = {}
    dead_ends: list[list[int]] = []
    dead_end_set: set[str] = set()
    visited_order: list[list[int]] = [list(start)]
    active_tree_path: list[str] = ["t0"]
    current_route: list[list[int]] = [list(start)]
    current_tree_id: str | None = "t0"
    final_path: list[list[int]] = []
    status = "searching"
    counter = 1

    tree_nodes["t0"] = {
        "tree_id": "t0", "graph_node": f"({start[0]},{start[1]})", "cell": list(start),
        "parent": None, "depth": 0, "path_cost": 0, "status": "active", "order": 0, "x": 0.5, "y": 0.12,
    }
    visible.append("t0")
    tree_id_by_cell[key(start)] = "t0"

    def set_active(route: list[list[int]]) -> None:
        active_tree_path.clear()
        for cell in route:
            tid = tree_id_by_cell.get(key(cell))
            if tid:
                active_tree_path.append(tid)

    def snapshot() -> dict[str, Any]:
        return {
            "tree": {"nodes": [copy.deepcopy(tree_nodes[t]) for t in visible]},
            "search": {
                "active_tree_node": current_tree_id,
                "active_tree_path": list(active_tree_path),
                "current_route": [list(c) for c in current_route],
                "visited_order": [list(c) for c in visited_order],
                "dead_end_cells": [list(c) for c in dead_ends],
                "final_path": [list(c) for c in final_path],
                "explored_count": len(visited_order),
                "current_depth": max(len(current_route) - 1, 0),
                "status": status,
                "found": bool(final_path),
            },
        }

    raw_steps: list[dict[str, Any]] = []
    for step in result.get("trace", []):
        action = step.get("action")
        cell = list(step.get("cell")) if isinstance(step.get("cell"), list) else None
        parent = list(step.get("parent")) if isinstance(step.get("parent"), list) else None
        stack = [list(c) for c in (step.get("stack") or [])]
        depth = int(step.get("depth") or 0)

        if action == "start":
            current_route = stack or [list(start)]
            status = "searching"
        elif action == "expand":
            parent_id = tree_id_by_cell.get(key(parent)) if parent else None
            tid = f"t{counter}"; counter += 1
            tree_nodes[tid] = {
                "tree_id": tid, "graph_node": f"({cell[0]},{cell[1]})", "cell": cell,
                "parent": parent_id, "depth": depth, "path_cost": depth,
                "status": "active", "order": len(visible), "x": 0.0, "y": 0.0,
            }
            visible.append(tid)
            tree_id_by_cell[key(cell)] = tid
            current_route = stack
            if not any(key(c) == key(cell) for c in visited_order):
                visited_order.append(cell)
            set_active(current_route)
            current_tree_id = tid
            if parent_id and parent_id in tree_nodes:
                tree_nodes[parent_id]["status"] = "expanded"
            status = "searching"
        elif action == "backtrack":
            current_route = stack
            set_active(current_route)
            bt = tree_id_by_cell.get(key(cell)) if cell else None
            if bt and bt in tree_nodes:
                tree_nodes[bt]["status"] = "backtracked"
            if cell and key(cell) not in dead_end_set:
                dead_end_set.add(key(cell)); dead_ends.append(cell)
            current_tree_id = active_tree_path[-1] if active_tree_path else "t0"
            if current_tree_id in tree_nodes:
                tree_nodes[current_tree_id]["status"] = "active"
            status = "backtracking"
        elif action == "found":
            if cell and key(cell) not in tree_id_by_cell:
                parent_id = tree_id_by_cell.get(key(parent)) if parent else None
                tid = f"t{counter}"; counter += 1
                tree_nodes[tid] = {
                    "tree_id": tid, "graph_node": f"({cell[0]},{cell[1]})", "cell": cell,
                    "parent": parent_id, "depth": depth, "path_cost": depth,
                    "status": "final", "order": len(visible), "x": 0.0, "y": 0.0,
                }
                visible.append(tid)
                tree_id_by_cell[key(cell)] = tid
            current_route = stack
            final_path = [list(c) for c in stack]
            active_tree_path.clear()
            for c in current_route:
                tid = tree_id_by_cell.get(key(c))
                if tid:
                    active_tree_path.append(tid)
                    tree_nodes[tid]["status"] = "final"
            current_tree_id = active_tree_path[-1] if active_tree_path else current_tree_id
            status = "delivery found" if delivery else "exit found"
        elif action == "fail":
            current_route = []
            active_tree_path.clear()
            current_tree_id = None
            status = "no route" if delivery else "no path"

        label = _lab_label(action, cell, delivery)
        raw_steps.append({
            "event_type": action, "label": label,
            "annotation": _lab_annotation(action, cell, delivery),
            "teaching_note": _lab_note(action, delivery),
            "snapshot": snapshot(),
        })

    base = solve_labyrinth(lab)
    layout = _layout_tree([tree_nodes[t] for t in visible])
    initial_state = copy.deepcopy(base.initial_state)
    initial_state["example_title"] = "Live Python delivery" if delivery else "Live Python labyrinth"
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
        app_type=app_type, trace_id=f"{app_type}-live", is_complete=True,
        initial_state=initial_state,
        summary=TraceSummary(step_count=len(steps), result=result.get("status", "found")),
        steps=steps,
    )


def _lab_label(action, cell, delivery):
    if action == "start":
        return "Start DFS"
    if action == "expand":
        return f"{'Move to' if delivery else 'Expand'} ({cell[0]},{cell[1]})"
    if action == "backtrack":
        return f"Backtrack from ({cell[0]},{cell[1]})"
    if action == "found":
        return "Delivery location found" if delivery else "Exit found"
    return "No delivery route found" if delivery else "No path found"


def _lab_annotation(action, cell, delivery):
    if action == "start":
        return "The office is ready. DFS starts at the robot." if delivery else "The maze is ready. DFS starts at the entrance."
    if action == "expand":
        return f"DFS steps into ({cell[0]},{cell[1]}) and keeps exploring."
    if action == "backtrack":
        return f"DFS retreats from ({cell[0]},{cell[1]}) after exhausting that branch."
    if action == "found":
        return "DFS reached the goal; the successful route is highlighted."
    return "DFS exhausted the reachable grid without reaching the goal."


def _lab_note(action, delivery):
    if action == "found":
        return "Plain DFS stops as soon as it finds any route."
    return "The tree shows search history; the grid shows spatial movement."


def build_labyrinth_trace(example: LabyrinthExample) -> TraceBundle:
    return build_labyrinth_trace_from_definition(
        example.labyrinth,
        title=example.title,
        subtitle=example.subtitle,
    )
