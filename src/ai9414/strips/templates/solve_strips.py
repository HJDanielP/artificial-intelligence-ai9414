"""Starter code for the STRIPS planning exercise.

Implement ``solve_strips(problem)``: a small forward breadth-first planner that
finds a sequence of grounded actions reaching the goal from the initial state.

Required return shape:
    {
        "algorithm": "strips_bfs",
        "status": "found" | "not_found",
        "plan": [
            "move(robot, corridor, office_a)",
            "pickup_keycard(robot, keycard, office_a)",
        ],
        "stats": {
            "expanded_states": 0,
            "generated_states": 1,
            "frontier_peak": 1,
        },
    }

Each plan entry is an action signature string. The app validates the plan
against the operators and replays the resulting world states.
"""

from __future__ import annotations

from typing import Any

from ai9414.strips import (
    apply_action_signature,
    get_applicable_actions,
    get_initial_facts,
)


def canonical_state_id(facts: list[tuple[str, ...]]) -> tuple[tuple[str, ...], ...]:
    """Turn a fact list into a hashable canonical state identifier."""
    return tuple(sorted(tuple(fact) for fact in facts))


def goal_satisfied(facts: list[tuple[str, ...]], goal: list[list[str]]) -> bool:
    """Return True when every goal fact already appears in the current state."""
    state = {tuple(fact) for fact in facts}
    return all(tuple(goal_fact) in state for goal_fact in goal)


def solve_strips(problem: dict[str, Any]) -> dict[str, Any]:
    """Implement a small forward STRIPS planner here."""
    start_facts = get_initial_facts(problem)

    # TODO:
    # 1. Create a BFS frontier of (facts, plan) pairs.
    # 2. Keep a visited set using canonical_state_id(...).
    # 3. Repeatedly pop the next state.
    # 4. Test goal_satisfied(...).
    # 5. Generate actions with get_applicable_actions(...).
    # 6. Apply actions with apply_action_signature(...).
    # 7. Return the first valid plan found.
    #
    # The helper call below is deliberately unused. It lets you inspect the
    # starting state while you are implementing the planner.
    _ = start_facts

    stats = {
        "expanded_states": 0,
        "generated_states": 1,
        "frontier_peak": 1,
    }

    return {
        "algorithm": "strips_bfs",
        "status": "error",
        "message": "TODO: implement forward STRIPS BFS planning.",
        "plan": [],
        "stats": stats,
    }
