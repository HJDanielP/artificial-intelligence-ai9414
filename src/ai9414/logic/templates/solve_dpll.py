"""Starter code for the propositional-logic DPLL exercise.

Implement ``solve_dpll(problem, options)``: run the DPLL procedure over the CNF
clauses and return the decision trace.

The problem dict includes "mode" ("sat" or "entailment"), "variables", and
"clauses" (each clause is a list of literal strings like "A" or "~B").

Return:
    {"algorithm": "dpll", "mode": problem["mode"], "status": ...,
     "trace": [ ... events ... ], "assignment": {"A": True, ...}}

Trace events carry a consecutive "step" (0, 1, 2, ...), "action", "node_id",
"parent_id", "variable", "value", "reason", "assignment". Actions: start,
choose_variable, assign, contradiction, backtrack, solution_found, finished.
"""

from __future__ import annotations

from typing import Any


def solve_dpll(problem: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    # TODO: implement DPLL (unit propagation, branching, backtracking) with a trace.
    return {
        "algorithm": "dpll",
        "mode": problem.get("mode", "sat"),
        "status": "error",
        "message": "Implement solve_dpll and record the decision trace.",
        "trace": [{"step": 0, "action": "start", "node_id": "t0", "parent_id": None, "variable": None, "value": None, "reason": None, "assignment": {}}],
        "assignment": {},
    }
