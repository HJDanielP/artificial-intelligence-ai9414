"""Central demo registry shared by the CLI and the unified server.

This module owns the catalogue of installed demos (`demo_specs`), the lazy
per-type instance cache used by the unified ``ai9414 serve`` application
(`get_demo`), and the sidebar metadata (`list_demos`).

Historically the catalogue lived in ``ai9414.cli``; it was moved here so the
server can build a multi-demo application without importing the CLI. ``cli``
re-imports the public names, so existing references keep working.
"""

from __future__ import annotations

import difflib
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from ai9414.core.app import BaseEducationalApp
from ai9414.core.errors import AI9414Error


@dataclass(frozen=True)
class DemoSpec:
    """Describe one installed demo entry."""

    name: str
    title: str
    description: str
    default_example: str
    factory: Callable[[], BaseEducationalApp]
    group: str = "General"
    aliases: tuple[str, ...] = ()
    example_names: Callable[[], Sequence[str]] | None = None
    live_factory: Callable[[], Any] | None = None
    """Lazily build the demo's LiveSpec for the in-browser solver, if supported."""


def _create_labyrinth_demo() -> BaseEducationalApp:
    from ai9414.labyrinth import LabyrinthDemo

    return LabyrinthDemo()


def _create_delivery_demo() -> BaseEducationalApp:
    from ai9414.delivery import DeliveryDemo

    return DeliveryDemo()


def _create_graph_dfs_demo() -> BaseEducationalApp:
    from ai9414.graph_dfs import GraphDfsDemo

    return GraphDfsDemo()


def _create_graph_bfs_demo() -> BaseEducationalApp:
    from ai9414.graph_bfs import GraphBfsDemo

    return GraphBfsDemo()


def _create_graph_gbfs_demo() -> BaseEducationalApp:
    from ai9414.graph_gbfs import GraphGbfsDemo

    return GraphGbfsDemo()


def _create_graph_astar_demo() -> BaseEducationalApp:
    from ai9414.graph_astar import GraphAStarDemo

    return GraphAStarDemo()


def _create_graph_ucs_demo() -> BaseEducationalApp:
    from ai9414.graph_ucs import GraphUcsDemo

    return GraphUcsDemo()


def _create_graph_bnb_demo() -> BaseEducationalApp:
    from ai9414.search import SearchDemo

    return SearchDemo()


def _create_logic_demo() -> BaseEducationalApp:
    from ai9414.logic import DpllDemo

    return DpllDemo()


def _create_uncertainty_demo() -> BaseEducationalApp:
    from ai9414.uncertainty import BeliefStateExplorer

    return BeliefStateExplorer()


def _create_foundation_models_demo() -> BaseEducationalApp:
    from ai9414.foundation_models import TokenisationExplorer

    return TokenisationExplorer()


def _create_csp_demo() -> BaseEducationalApp:
    from ai9414.csp import CSPDemo

    return CSPDemo()


def _create_delivery_csp_demo() -> BaseEducationalApp:
    from ai9414.delivery_csp import DeliveryCSPDemo

    return DeliveryCSPDemo()


def _create_strips_demo() -> BaseEducationalApp:
    from ai9414.strips import StripsDemo

    return StripsDemo()


def _list_logic_examples() -> Sequence[str]:
    from ai9414.logic.examples import build_examples

    return list(build_examples())


def _live_graph_bfs() -> Any:
    from ai9414.graph_bfs.live import build_live_spec

    return build_live_spec()


def _live_factory(module: str) -> Callable[[], Any]:
    def factory() -> Any:
        import importlib

        return importlib.import_module(module).build_live_spec()

    return factory


def demo_specs() -> tuple[DemoSpec, ...]:
    """Return the installed demo catalogue."""

    return (
        DemoSpec(
            name="labyrinth",
            title="Labyrinth DFS",
            description="Labyrinth depth-first search",
            default_example="small",
            factory=_create_labyrinth_demo,
            group="Search",
            live_factory=_live_factory("ai9414.labyrinth.live"),
        ),
        DemoSpec(
            name="delivery",
            title="Delivery DFS",
            description="Office delivery depth-first search",
            default_example="four_rooms",
            factory=_create_delivery_demo,
            group="Search",
            live_factory=_live_factory("ai9414.delivery.live"),
        ),
        DemoSpec(
            name="graph-dfs",
            title="Graph DFS",
            description="Spatial graph depth-first search",
            default_example="small",
            factory=_create_graph_dfs_demo,
            group="Search",
            aliases=("graph_dfs",),
            live_factory=_live_factory("ai9414.graph_dfs.live"),
        ),
        DemoSpec(
            name="graph-bfs",
            title="Graph BFS",
            description="Spatial graph breadth-first search",
            default_example="small",
            factory=_create_graph_bfs_demo,
            group="Search",
            aliases=("graph_bfs",),
            live_factory=_live_graph_bfs,
        ),
        DemoSpec(
            name="graph-gbfs",
            title="Graph Greedy Best-First Search",
            description="Spatial graph greedy best-first search",
            default_example="small",
            factory=_create_graph_gbfs_demo,
            group="Search",
            aliases=("graph_gbfs",),
            live_factory=_live_factory("ai9414.graph_gbfs.live"),
        ),
        DemoSpec(
            name="graph-astar",
            title="Graph A* Search",
            description="Spatial graph A* search",
            default_example="small",
            factory=_create_graph_astar_demo,
            group="Search",
            aliases=("graph_astar",),
            live_factory=_live_factory("ai9414.graph_astar.live"),
        ),
        DemoSpec(
            name="graph-ucs",
            title="Graph Uniform-Cost Search",
            description="Spatial graph uniform-cost search",
            default_example="small",
            factory=_create_graph_ucs_demo,
            group="Search",
            aliases=("graph_ucs",),
            live_factory=_live_factory("ai9414.graph_ucs.live"),
        ),
        DemoSpec(
            name="graph-bnb",
            title="Graph Branch-and-Bound Search",
            description="Spatial graph branch-and-bound search",
            default_example="small",
            factory=_create_graph_bnb_demo,
            group="Search",
            aliases=("graph_branch_and_bound", "graph-branch-and-bound"),
        ),
        DemoSpec(
            name="logic-dpll",
            title="Visual DPLL",
            description="Propositional logic DPLL",
            default_example="simple_sat",
            factory=_create_logic_demo,
            group="Logic",
            aliases=("logic_dpll",),
            example_names=_list_logic_examples,
            live_factory=_live_factory("ai9414.logic.live"),
        ),
        DemoSpec(
            name="uncertainty",
            title="Belief-State Explorer",
            description="Reasoning with uncertainty belief-state explorer",
            default_example="office_localisation_basic",
            factory=_create_uncertainty_demo,
            group="Uncertainty",
            live_factory=_live_factory("ai9414.uncertainty.live"),
        ),
        DemoSpec(
            name="foundation-models",
            title="Tokenisation Explorer",
            description="Foundation models tokenisation explorer",
            default_example="simple_sentence",
            factory=_create_foundation_models_demo,
            group="Foundation Models",
            aliases=("foundation_models",),
        ),
        DemoSpec(
            name="csp-map",
            title="CSP Map Colouring",
            description="CSP map colouring",
            default_example="australia",
            factory=_create_csp_demo,
            group="CSP",
            aliases=("csp", "csp_map"),
            live_factory=_live_factory("ai9414.csp.live"),
        ),
        DemoSpec(
            name="csp-delivery",
            title="CSP Delivery Scheduling",
            description="CSP delivery time-slot assignment",
            default_example="weekday_schedule",
            factory=_create_delivery_csp_demo,
            group="CSP",
            aliases=("delivery_csp", "csp_delivery"),
            live_factory=_live_factory("ai9414.delivery_csp.live"),
        ),
        DemoSpec(
            name="strips",
            title="STRIPS Planning",
            description="STRIPS planning",
            default_example="canonical_delivery",
            factory=_create_strips_demo,
            group="Planning",
            live_factory=_live_factory("ai9414.strips.live"),
        ),
    )


def _normalise_demo_name(name: str) -> str:
    return str(name).strip().lower().replace("_", "-")


def _known_demo_names() -> list[str]:
    names: list[str] = []
    for spec in demo_specs():
        names.append(spec.name)
        names.extend(spec.aliases)
    return names


def resolve_demo_spec(name: str) -> DemoSpec:
    """Resolve a canonical or alias demo name to its :class:`DemoSpec`."""

    normalised = _normalise_demo_name(name)
    for spec in demo_specs():
        if normalised == spec.name or normalised in spec.aliases:
            return spec

    suggestions = difflib.get_close_matches(normalised, _known_demo_names(), n=3)
    hint = f" Did you mean: {', '.join(suggestions)}?" if suggestions else ""
    raise AI9414Error(
        code="demo_not_found",
        message=f"Unknown demo '{name}'. Run 'ai9414 list' to see the available demos.{hint}",
    )


def demo_example_names(spec: DemoSpec) -> list[str]:
    """Return curated example names for a demo without launching it twice."""

    if spec.example_names is not None:
        return list(spec.example_names())
    return list(spec.factory().list_examples())


# --- Lazy per-type instance cache (used by the unified server) ---------------

_INSTANCES: dict[str, BaseEducationalApp] = {}


def get_demo(name: str) -> BaseEducationalApp:
    """Return a shared, lazily-created instance for a demo name (or alias).

    The unified ``ai9414 serve`` app keeps one instance per demo type so that
    per-session playback state (current step, loaded example, generated graph)
    survives across requests, matching the single-demo behaviour.
    """

    spec = resolve_demo_spec(name)
    instance = _INSTANCES.get(spec.name)
    if instance is None:
        instance = spec.factory()
        _INSTANCES[spec.name] = instance
    return instance


def list_demos() -> list[dict[str, str]]:
    """Return sidebar metadata for every demo, in catalogue order."""

    return [
        {
            "name": spec.name,
            "title": spec.title,
            "description": spec.description,
            "group": spec.group,
        }
        for spec in demo_specs()
    ]


def reset_instances() -> None:
    """Drop all cached demo instances (test helper)."""

    _INSTANCES.clear()
