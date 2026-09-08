#!/usr/bin/env python3
"""Interactive ASCII renderer for a generated A-Maze-ing maze."""

from __future__ import annotations

import os

from config import Config
from maze_generator import MazeGenerator

NORTH = 0b0001
EAST = 0b0010
SOUTH = 0b0100
WEST = 0b1000

WALL_PALETTE = [
    "\033[34m\u2588\033[0m",
    "\033[32m\u2588\033[0m",
    "\033[33m\u2588\033[0m",
    "\033[31m\u2588\033[0m"
]
PATH_MARK = "\u25cf"


class AsciiRenderer:
    """Displays the maze in a terminal with interactive ASCII controls.

    Interactions (see subject, chapter 5):
        1: regenerate a new maze
        2: show/hide the solution path
        3: change the wall color
        4 / q: quit
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
            maze_generator: Generator used to create another maze.
        """
        self.grid = grid
        self.config = config
        self.path = path
        self.maze_generator = maze_generator

        self.show_path = False
        self.color_index = 0

    def run(self) -> None:
        """Draw the maze and process commands until the user quits."""
        try:
            while True:
                self.draw()
                key = self._read_key()
                if key in ("4", "q", "Q"):
                    break
                self.event_keyboard(key)
        except (EOFError, KeyboardInterrupt):
            pass
        self._close()

    @staticmethod
    def _read_key() -> str:
        """Read one command and normalize the AZERTY number row."""
        key = input().strip()[:1]
        return {
            "&": "1",
            "é": "2",
            '"': "3",
            "'": "4",
        }.get(key, key)

    def draw(self) -> None:
        """Redraw the whole maze as ASCII characters."""
        os.system("cls" if os.name == "nt" else "clear")
        height = len(self.grid)
        width = len(self.grid[0]) if height else 0
        wall = WALL_PALETTE[self.color_index]
        rendered = [
            [wall if row % 2 == 0 and column % 2 == 0 else " "
             for column in range(width * 2 + 1)]
            for row in range(height * 2 + 1)
        ]

        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell & NORTH:
                    rendered[2 * y][2 * x + 1] = wall
                if cell & SOUTH:
                    rendered[2 * y + 2][2 * x + 1] = wall
                if cell & WEST:
                    rendered[2 * y + 1][2 * x] = wall
                if cell & EAST:
                    rendered[2 * y + 1][2 * x + 2] = wall
                east_and_west = cell & WEST and cell & EAST
                if cell & NORTH and cell & SOUTH and east_and_west:
                    w42 = "\033[41m\u2588\033[0m"
                    for remplir_y in range(0, 2):
                        for remplir_x in range(0, 2):
                            rendered[
                                2 * y + remplir_y][
                                    2 * x + remplir_x] = w42

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
        if key == "1":
            self.regen_maze()
        elif key == "2":
            self._toggle_path()
        elif key == "3":
            self._next_color()

    def regen_maze(self) -> None:
        """Generate another maze and update its displayed path."""
        from maze_output import MazeOutput

        self.grid = self.maze_generator.generate()
        self.path = MazeOutput.path_to_directions(
            self.grid,
            self.config.entry,
            self.config.exit,
            self.maze_generator.solution
        )
        self.show_path = False

    def _toggle_path(self) -> None:
        """Toggle visibility of the solution path."""
        self.show_path = not self.show_path

    def _next_color(self) -> None:
        """Select the next wall color."""
        self.color_index = (self.color_index + 1) % len(WALL_PALETTE)

    def _close(self) -> None:
        """End the terminal renderer."""
        print("\nRenderer stopped.")
