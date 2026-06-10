"""Installed command-line interface for ai9414 demos."""

from __future__ import annotations

import argparse
import socket
import sys
from collections.abc import Sequence
from typing import TextIO

from ai9414.core import AI9414Error, AppLauncher
from ai9414.core.registry import (
    DemoSpec,
    demo_example_names,
    demo_specs,
    resolve_demo_spec,
)

__all__ = ["DemoSpec", "demo_specs", "resolve_demo_spec", "build_parser", "main"]


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level parser for the installed CLI."""

    parser = argparse.ArgumentParser(
        prog="ai9414",
        description="Launch ai9414 teaching demos from an installed package.",
    )
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser(
        "list",
        help="List available demos or curated examples.",
    )
    list_parser.add_argument(
        "--examples",
        metavar="DEMO",
        help="Show the curated example names for one demo.",
    )

    serve_parser = subparsers.add_parser(
        "serve",
        help="Launch all demos together in one local browser app.",
    )
    serve_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface to bind the local server to.",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        help="Port for the local server. Defaults to 9414 (or a free port).",
    )
    serve_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Start the server without opening a browser window automatically.",
    )
    serve_parser.add_argument(
        "--solver",
        metavar="PATH",
        help="Preload a student solver .py file for the live 'Solve' workflow.",
    )
    serve_parser.add_argument(
        "--workspace",
        metavar="DIR",
        help="Directory for saved solver drafts (default ./ai9414-solutions).",
    )

    demo_parser = subparsers.add_parser(
        "demo",
        help="Launch one demo in a local browser session.",
    )
    demo_parser.add_argument(
        "name",
        help="Demo name. Run 'ai9414 list' to see the available options.",
    )
    source_group = demo_parser.add_mutually_exclusive_group()
    source_group.add_argument(
        "--example",
        help="Curated example name to load before launching the demo.",
    )
    source_group.add_argument(
        "--config",
        help="Path to a JSON configuration file to load before launching the demo.",
    )
    demo_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface to bind the local demo server to.",
    )
    demo_parser.add_argument(
        "--port",
        type=int,
        help="Port for the local demo server. If omitted, a free port is chosen automatically.",
    )
    demo_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Start the local server without opening a browser window automatically.",
    )
    demo_parser.add_argument(
        "--solver",
        metavar="PATH",
        help="Preload a student solver .py file for the live 'Solve' workflow.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the installed ai9414 CLI."""

    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        if args.command is None:
            _print_overview(parser)
            return 0
        if args.command == "list":
            return _run_list_command(args)
        if args.command == "serve":
            return _run_serve_command(args)
        if args.command == "demo":
            return _run_demo_command(args)
    except AI9414Error as exc:
        print(f"Error: {exc.message}", file=sys.stderr)
        return 1

    parser.print_help()
    return 1


def _run_list_command(args: argparse.Namespace) -> int:
    if args.examples:
        spec = resolve_demo_spec(args.examples)
        print(f"{spec.name} examples:")
        for example_name in demo_example_names(spec):
            print(f"- {example_name}")
        return 0

    print("Available demos:")
    for spec in demo_specs():
        alias_text = ""
        if spec.aliases:
            alias_text = f" | aliases: {', '.join(spec.aliases)}"
        print(
            f"- {spec.name}: {spec.description} "
            f"(default example: {spec.default_example}{alias_text})"
        )
    print()
    print("Start everything with: ai9414 serve")
    print("Start one demo with: ai9414 demo <name>")
    print("Show example names with: ai9414 list --examples <name>")
    return 0


def _run_serve_command(args: argparse.Namespace) -> int:
    from ai9414.core import solve as solve_module
    from ai9414.core import workspace as workspace_module
    from ai9414.core.server import create_app

    if getattr(args, "solver", None):
        solve_module.set_preloaded_solver(args.solver)
    if getattr(args, "workspace", None):
        workspace_module.set_workspace_dir(args.workspace)

    port = args.port if args.port is not None else _preferred_serve_port(args.host)
    launcher = AppLauncher(
        None,
        host=args.host,
        port=port,
        open_browser=not args.no_browser,
        fastapi_app=create_app(),
    )
    launcher.start()
    return 0


def _run_demo_command(args: argparse.Namespace) -> int:
    spec = resolve_demo_spec(args.name)
    app = spec.factory()

    if args.config:
        app.load_config(args.config)
    elif args.example:
        app.load_example(args.example)

    if getattr(args, "solver", None):
        from ai9414.core import solve as solve_module

        solve_module.set_preloaded_solver(args.solver)

    launcher = AppLauncher(
        app,
        host=args.host,
        port=args.port,
        open_browser=not args.no_browser,
    )
    launcher.start()
    return 0


def _preferred_serve_port(host: str, preferred: int = 9414) -> int:
    """Use the conventional 9414 port if free, otherwise pick a free one."""

    from ai9414.core.server import find_free_port

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, preferred))
            return preferred
        except OSError:
            return find_free_port(host)


def _print_overview(parser: argparse.ArgumentParser, *, file: TextIO | None = None) -> None:
    output = file or sys.stdout
    parser.print_help(file=output)
    print(file=output)
    print("Examples:", file=output)
    print("  ai9414 serve", file=output)
    print("  ai9414 list", file=output)
    print("  ai9414 demo graph-bnb", file=output)
    print("  python -m ai9414 demo graph-dfs", file=output)
