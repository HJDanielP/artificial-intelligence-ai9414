"""Trace construction helpers for the DPLL demo."""

from __future__ import annotations

import copy
from dataclasses import asdict
from typing import Any

from ai9414.core.models import TraceBundle, TraceStep, TraceSummary
from ai9414.logic.models import LogicExample, LogicProblem
from ai9414.logic.solver import evaluate_formula, solve_dpll


def build_logic_trace(
    example: LogicExample,
    *,
    unit_propagation: bool = True,
    pure_literals: bool = False,
    variable_order: str = "alphabetical",
) -> TraceBundle:
    return build_logic_trace_from_problem(
        example.problem,
        title=example.title,
        subtitle=example.subtitle,
        unit_propagation=unit_propagation,
        pure_literals=pure_literals,
        variable_order=variable_order,
    )


def build_logic_trace_from_result(problem: dict[str, Any], result: dict[str, Any]) -> TraceBundle:
    """Convert a student DPLL result into a TraceBundle (port of the former JS
    ``buildLogicTraceFromBackend``), reusing ``evaluate_formula`` for clause state."""

    model = LogicProblem.model_validate(problem)
    clauses = [list(c) for c in model.clauses]
    mode = result.get("mode") or model.mode
    final_result = result.get("status")

    tree_nodes: dict[str, dict[str, Any]] = {}
    tree_ids: list[str] = []
    path_by_id: dict[str, list[str]] = {"t0": ["t0"]}
    active_tree_node = "t0"
    active_tree_path = ["t0"]
    final_tree_path: list[str] = []
    assignment_items: list[dict[str, Any]] = []
    status = "ready"
    stats = {"decisions": 0, "forced_assignments": 0, "contradictions": 0, "backtracks": 0}

    tree_nodes["t0"] = {
        "tree_id": "t0", "graph_node": "start", "assignment_text": "No assignments",
        "parent": None, "depth": 0, "path_cost": 0, "status": "active", "order": 0,
        "x": 0.5, "y": 0.12, "terminal": False, "reason": "start",
    }
    tree_ids.append("t0")

    def clause_view(assignment: dict[str, bool]) -> list[dict[str, Any]]:
        return [asdict(c) for c in evaluate_formula(clauses, assignment)]

    def sync_items(assignment: dict[str, bool], tree_path: list[str]) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for tid in tree_path[1:]:
            node = tree_nodes.get(tid)
            if not node or "=" not in node["graph_node"]:
                continue
            variable, raw = (part.strip() for part in node["graph_node"].split("="))
            items.append({
                "variable": variable, "value": raw == "T", "reason": node.get("reason"),
                "clause_index": node.get("clause_index"), "text": f"{variable} = {raw}",
            })
        return items

    def snapshot(assignment: dict[str, bool]) -> dict[str, Any]:
        return {
            "tree": {"nodes": [copy.deepcopy(tree_nodes[t]) for t in tree_ids]},
            "search": {
                "active_tree_node": active_tree_node,
                "active_tree_path": list(active_tree_path),
                "best_tree_path": [],
                "final_tree_path": list(final_tree_path),
                "finished": status in {"finished", "satisfiable", "unsatisfiable", "entailed", "not entailed"},
                "status": status,
                "result": final_result,
            },
            "logic": {
                "mode": mode,
                "variables": list(model.variables or []),
                "clauses": clause_view(assignment),
                "assignment": list(assignment_items),
                "kb_formulas": list(model.kb_formulas or []),
                "query": model.query,
                "entailment_target": model.entailment_target,
                "original_input": list(model.original_input or []),
            },
            "stats": dict(stats),
        }

    raw_steps: list[dict[str, Any]] = []
    for step in result.get("trace", []):
        action = step.get("action")
        node_id = step.get("node_id")
        parent_id = step.get("parent_id")
        variable = step.get("variable")
        reason = step.get("reason")
        value = step.get("value")
        assignment = dict(step.get("assignment") or {})

        if action == "start":
            active_tree_node = "t0"
            active_tree_path = ["t0"]
            tree_nodes["t0"]["status"] = "active"
            status = "searching"
        elif action == "choose_variable":
            active_tree_node = node_id or active_tree_node
            active_tree_path = path_by_id.get(active_tree_node, active_tree_path)
            status = "branching"
        elif action == "assign":
            value_text = "T" if value else "F"
            tree_nodes[node_id] = {
                "tree_id": node_id, "graph_node": f"{variable} = {value_text}",
                "assignment_text": ", ".join(f"{n} = {'T' if v else 'F'}" for n, v in assignment.items()),
                "parent": parent_id, "depth": len(assignment), "path_cost": 0,
                "status": "active" if reason == "decision" else "forced",
                "order": len(tree_ids), "x": 0.5, "y": 0.12, "terminal": False,
                "reason": reason or "decision", "clause_index": step.get("clause_index"),
            }
            tree_ids.append(node_id)
            path_by_id[node_id] = path_by_id.get(parent_id, ["t0"]) + [node_id]
            active_tree_node = node_id
            active_tree_path = path_by_id[node_id]
            if reason == "decision":
                stats["decisions"] += 1
                if parent_id in tree_nodes:
                    tree_nodes[parent_id]["status"] = "branched"
                status = "branching"
            else:
                stats["forced_assignments"] += 1
                status = "propagating"
        elif action == "contradiction":
            if node_id in tree_nodes:
                tree_nodes[node_id]["status"] = "contradiction"
                active_tree_node = node_id
                active_tree_path = path_by_id.get(node_id, active_tree_path)
            stats["contradictions"] += 1
            status = "contradiction"
        elif action == "backtrack":
            if node_id:
                active_tree_node = node_id
                active_tree_path = path_by_id.get(node_id, ["t0"])
            if active_tree_node in tree_nodes:
                tree_nodes[active_tree_node]["status"] = "active"
            stats["backtracks"] += 1
            status = "backtracking"
        elif action == "solution_found":
            if node_id in tree_nodes:
                tree_nodes[node_id]["status"] = "solution"
                active_tree_node = node_id
                active_tree_path = path_by_id.get(node_id, active_tree_path)
            final_tree_path = list(active_tree_path)
            status = "satisfiable" if mode == "sat" else "not entailed"
        elif action == "finished":
            if final_result in {"satisfiable", "not_entailed"}:
                final_tree_path = list(active_tree_path)
            status = {
                "not_entailed": "not entailed", "unsatisfiable": "unsatisfiable",
                "entailed": "entailed",
            }.get(final_result, final_result or "finished")

        assignment_items = sync_items(assignment, active_tree_path)
        raw_steps.append({
            "event_type": action,
            "label": _dpll_label(action, variable, value, reason),
            "annotation": _dpll_annotation(action, variable, value, reason, final_result),
            "teaching_note": _dpll_note(action),
            "snapshot": snapshot(assignment),
        })

    base = solve_dpll(model)
    layout = _layout_tree([tree_nodes[t] for t in tree_ids])
    initial_state = copy.deepcopy(base.initial_data)
    initial_state["example_title"] = "Live Python DPLL"
    initial_state["example_subtitle"] = "Trace returned by your Python DPLL solver."
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
        app_type="logic", trace_id="logic-live", is_complete=True,
        initial_state=initial_state,
        summary=TraceSummary(step_count=len(steps), result=final_result or "finished"),
        steps=steps,
    )


def _dpll_label(action, variable, value, reason):
    if action == "start":
        return "Start DPLL"
    if action == "choose_variable":
        return f"Choose {variable}"
    if action == "assign":
        verb = "Assign" if reason == "decision" else "Force"
        return f"{verb} {variable} = {'T' if value else 'F'}"
    return {"contradiction": "Contradiction", "backtrack": "Backtrack",
            "solution_found": "Solution found"}.get(action, "Finished")


def _dpll_annotation(action, variable, value, reason, final_result):
    if action == "assign":
        if reason == "decision":
            return f"Choose {variable} = {'true' if value else 'false'} as the next branch."
        if reason == "unit":
            return f"A unit clause forces {variable} = {'true' if value else 'false'}."
        return f"A pure literal lets DPLL set {variable} = {'true' if value else 'false'}."
    return {
        "start": "The clause list is ready for a DPLL replay.",
        "choose_variable": f"No forced move remains, so DPLL branches on {variable}.",
        "contradiction": "One clause is now false, so the current branch fails.",
        "backtrack": "DPLL returns to the previous decision point and tries another branch.",
        "solution_found": "All clauses are satisfied under the current assignment.",
    }.get(action, "The search has finished.")


def _dpll_note(action):
    if action == "backtrack":
        return "A failed branch does not end the search until every alternative has also failed."
    return "The tree shows partial assignments; the clauses show why each step happened."


def build_logic_trace_from_problem(
    problem: LogicProblem,
    *,
    title: str | None = None,
    subtitle: str | None = None,
    unit_propagation: bool = True,
    pure_literals: bool = False,
    variable_order: str = "alphabetical",
) -> TraceBundle:
    result = solve_dpll(
        problem,
        unit_propagation=unit_propagation,
        pure_literals=pure_literals,
        variable_order=variable_order,
    )

    all_tree_nodes = result.initial_data["tree"]["nodes"]
    for raw_step in result.raw_steps:
        all_tree_nodes = raw_step.snapshot["tree"]["nodes"]
    layout = _layout_tree(all_tree_nodes)

    initial_state = copy.deepcopy(result.initial_data)
    if title is not None:
        initial_state["example_title"] = title
    if subtitle is not None:
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
        app_type="logic",
        trace_id=result.trace_id,
        is_complete=True,
        initial_state=initial_state,
        summary=TraceSummary(step_count=len(steps), result=result.status),
        steps=steps,
    )


def _layout_tree(nodes: list[dict[str, Any]]) -> dict[str, tuple[float, float]]:
    children: dict[str | None, list[str]] = {}
    depth_map: dict[str, int] = {}
    for node in nodes:
        children.setdefault(node["parent"], []).append(node["tree_id"])
        depth_map[node["tree_id"]] = int(node["depth"])

    order_map = {node["tree_id"]: node["order"] for node in nodes}
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
