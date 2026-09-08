#!/usr/bin/env python3
"""ASCII renderer for the A-Maze-ing maze, read from maze.txt."""

from __future__ import annotations

import os
from config import Config

NORTH = 0b0001
EAST = 0b0010
SOUTH = 0b0100
WEST = 0b1000

WALL_PALETTE = ["-", "=", "~", "*", "%"]
PATH_MARK = "\u25cf"


class AsciiRenderer:
    from maze_generator import MazeGenerator
    """Displays the maze in a terminal with interactive ASCII controls.

    Interactions (see subject, chapter 5):
        1: regenerate a new maze
        2: show/hide the solution path
        3: change the horizontal wall character
        4 / q / ESC: quit
    """

    def __init__(
        self,
        grid: list[list[int]],
        config: Config,
        path: str,
        maze_generator: MazeGenerator,
    ) -> None:
        """Set up the terminal renderer for a maze.

        Args:
            grid: Maze cells (wall bitmask per cell).
            config: Maze configuration (entry/exit).
            path: Solution path as N/E/S/W letters.
            regenerate: Optional callback returning a new
                (grid, config, path) triple, called on the
                "regenerate" key. Defaults to redrawing the same
                maze (until MazeGenerator is wired in).
        """
        self.grid = grid
        self.config = config
        self.path = path
        self.maze_generator = maze_generator

        self.show_path = False
        self.color_index = 0

    def run(self) -> None:
        """Draw the maze and process one console key at a time."""
        while True:
            self.draw()
            key = self._read_key()
            if key in ("4", "q", "Q", "\x1b"):
                self._close()
                return
            self.event_keyboard(key)

    @staticmethod
    def _read_key() -> str:
        """Read one key."""
        return input().strip()[:1]

    def draw(self) -> None:
        """Redraw the whole maze as ASCII characters."""
        os.system("cls" if os.name == "nt" else "clear")
        height = len(self.grid)
        width = len(self.grid[0]) if height else 0
        rendered = [
            ["+" if row % 2 == 0 and column % 2 == 0 else " "
             for column in range(width * 2 + 1)]
            for row in range(height * 2 + 1)
        ]
        horizontal_wall = WALL_PALETTE[self.color_index]

        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell & NORTH:
                    rendered[2 * y][2 * x + 1] = horizontal_wall
                if cell & SOUTH:
                    rendered[2 * y + 2][2 * x + 1] = horizontal_wall
                if cell & WEST:
                    rendered[2 * y + 1][2 * x] = "|"
                if cell & EAST:
                    rendered[2 * y + 1][2 * x + 2] = "|"

        if self.show_path:
            for x, y in self._path_cells()[1:-1]:
                rendered[2 * y + 1][2 * x + 1] = PATH_MARK
        ex, ey = self.config.entry
        xx, xy = self.config.exit
        rendered[2 * ey + 1][2 * ex + 1] = "S"
        rendered[2 * xy + 1][2 * xx + 1] = "E"
        print("\n".join("".join(row) for row in rendered))
        print("\n[1] regenerate  [2] path  [3] wall  [4/q] quit")

    def _path_cells(self) -> list[tuple[int, int]]:
        """Compute the (x, y) cells visited by the solution path.

        Returns:
            The list of cells from entry to exit, inclusive.
        """
        x, y = self.config.entry
        cells = [(x, y)]
        deltas = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
        for step in self.path:
            dx, dy = deltas[step]
            x, y = x + dx, y + dy
            cells.append((x, y))
        return cells

    def event_keyboard(self, key: str) -> None:
        """Handle one terminal key (see class docstring for bindings)."""
        key = {
            "&": "1",
            "é": "2",
            '"': "3",
            "'": "4",
        }.get(key, key)
        if key == "1":
            self.regen_maze()
        elif key == "2":
            self._toggle_path()
        elif key == "3":
            self._next_color()
        elif key in ("4", "q", "Q", "\x1b"):
            self._close()

    def regen_maze(self) -> None:
        """Load a new maze from the configured regeneration callback."""
        from maze_output import MazeOutput

        self.grid = self.maze_generator.generate()
        self.path = MazeOutput.path_to_directions(
            self.grid,
            self.config.entry,
            self.config.exit,
            self.maze_generator.solution
        )
        self.show_path = False
        self.draw()

    def _toggle_path(self) -> None:
        """Toggle visibility of the solution path."""
        self.show_path = not self.show_path
        self.draw()

    def _next_color(self) -> None:
        """Select the next horizontal wall character and redraw."""
        self.color_index = (self.color_index + 1) % len(WALL_PALETTE)
        self.draw()

    def _close(self) -> None:
        """End the terminal renderer."""
        print("\nRenderer stopped.")
