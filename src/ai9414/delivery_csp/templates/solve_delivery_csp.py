"""Starter code for the delivery time-slot CSP exercise.

Implement ``solve_delivery_csp(problem, options)``: assign each delivery to a
time-slot/room value with backtracking + forward checking, honouring the
precedence/exclusion constraints, and return an event trace.

Return shape:
    {
        "algorithm": "backtracking_forward_checking",
        "status": "found" | "not_found",
        "events": [ {"action": ..., ...}, ... ],
        "assignment": {"meds": "slot_2_clinic", ...},
        "stats": {"assignments": 0, "backtracks": 0, "prunes": 0},
    }

Event actions: start, select_variable, try_value, assign, prune,
domain_wipeout, backtrack, unassign, solution_found, failure.
"""

from __future__ import annotations

from typing import Any


def solve_delivery_csp(problem: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    # TODO: implement backtracking + forward checking and record an event trace.
    return {
        "algorithm": "backtracking_forward_checking",
        "status": "error",
        "message": "Implement solve_delivery_csp: schedule the deliveries and return an event trace.",
        "events": [],
        "assignment": {},
        "stats": {},
    }
