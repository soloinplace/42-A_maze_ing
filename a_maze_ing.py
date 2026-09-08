#!/usr/bin/env python3
"""Command-line entry point for A-Maze-ing."""

from __future__ import annotations

import sys

from errors import AMazeIngError
from maze_generator import MazeGenerator
from maze_output import MazeOutput
from parsing import ConfigParse
from rendering import AsciiRenderer


def main(argv: list[str]) -> int:
    """Generate the configured maze and write its normalized output."""
    if len(argv) != 1:
        print("Usage: python3 a_maze_ing.py <config.txt>", file=sys.stderr)
        return 2
    try:
        config = ConfigParse.parse_config(argv[0])
        generator = MazeGenerator(
            width=config.width,
            height=config.height,
            entry=config.entry,
            exit=config.exit,
            perfect=config.perfect,
            seed=config.seed,
        )
        generator.generate()
        MazeOutput.write_output_file(
            generator.maze,
            config.output_file,
            config.entry,
            config.exit,
            generator.solution,
        )
        # rendering: render_maze(generator.maze)
        rendering = AsciiRenderer(grid, config, path)
        rendering.run()
    except (AMazeIngError, RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    for warning in generator.warnings:
        print(f"Warning: {warning}", file=sys.stderr)
    print(f"Maze written to {config.output_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
