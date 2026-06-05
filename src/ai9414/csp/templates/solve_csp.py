"""Starter code for the CSP map-colouring exercise.

Implement ``solve_csp(problem, options)``. It receives the CSP problem and the
UI options, runs backtracking search with forward checking, and returns an
event trace the app replays.

Return shape:
    {
        "algorithm": "backtracking_forward_checking",
        "status": "found" | "not_found",
        "events": [ {"action": ..., ...}, ... ],
        "assignment": {"wa": "red", ...},
        "stats": {"assignments": 0, "backtracks": 0, "prunes": 0},
    }

Event actions: start, select_variable, try_value, assign, prune,
domain_wipeout, backtrack, unassign, solution_found, failure.
"""

from __future__ import annotations

from typing import Any


def solve_csp(problem: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    # TODO: implement backtracking + forward checking and record an event trace.
    return {
        "algorithm": "backtracking_forward_checking",
        "status": "error",
        "message": "Implement solve_csp: run backtracking search and return an event trace.",
        "events": [],
        "assignment": {},
        "stats": {},
    }
