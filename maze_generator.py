#!/usr/bin/env python3
"""Reusable maze generation with deterministic randomness.

The public grid uses ``maze[y][x]``. Each integer stores four wall bits:
North=1, East=2, South=4 and West=8. A set bit means that the wall is
closed. Call :meth:`MazeGenerator.generate` before reading ``maze`` or
``solution``.
"""

from __future__ import annotations

import random
from collections import deque

Cell = tuple[int, int]
Direction = tuple[int, int, int, int]

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8
ALL_WALLS = NORTH | EAST | SOUTH | WEST

_DIRECTIONS: tuple[Direction, ...] = (
    (0, -1, NORTH, SOUTH),
    (1, 0, EAST, WEST),
    (0, 1, SOUTH, NORTH),
    (-1, 0, WEST, EAST),
)

_PATTERN_42 = (
    "1010111",
    "1010001",
    "1110111",
    "0010100",
    "0010111",
)


class MazeGenerator:
    """Generate perfect or braided mazes and their shortest path.

    Args:
        width: Number of columns.
        height: Number of rows.
        entry: Entrance as an ``(x, y)`` pair.
        exit: Exit as an ``(x, y)`` pair.
        perfect: If true, produce a connected maze without cycles. If false,
            produce a connected Pac-Man-like board with at least two cycles
            and at most two avoidable dead-ends.
        seed: Optional seed. Two new instances built with the same arguments
            and seed produce the same sequence of mazes.

    Attributes:
        maze: Wall grid indexed as ``maze[y][x]``.
        solution: Shortest path as a list of ``(x, y)`` coordinates.
        pattern_cells: Cells used to draw the closed ``42`` obstacle.
        warnings: Non-fatal messages, such as an omitted ``42`` pattern.
    """

    NORTH = NORTH
    EAST = EAST
    SOUTH = SOUTH
    WEST = WEST
    ALL_WALLS = ALL_WALLS

    def __init__(
        self,
        width: int,
        height: int,
        entry: Cell,
        exit: Cell,
        perfect: bool = False,
        seed: int | None = None,
    ) -> None:
        """Store generation parameters and initialize an empty result."""
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.perfect = perfect
        self.seed = seed
        self.maze: list[list[int]] = []
        self.solution: list[Cell] = []
        self.pattern_cells: set[Cell] = set()
        self.warnings: list[str] = []
        self._random = random.Random(seed)
        self._validate_parameters()

    def generate(self) -> list[list[int]]:
        """Generate a maze, validate it, and return the wall grid.

        Repeated calls generate a deterministic sequence when ``seed`` is
        provided. The returned grid is the public ``maze`` attribute.

        Returns:
            The newly generated wall grid.

        Raises:
            RuntimeError: If no valid non-perfect board can be generated.
        """
        attempts = 1 if self.perfect else 40
        last_error = "unknown generation error"
        for _ in range(attempts):
            self._reset()
            self._place_42_pattern()
            self._check_non_perfect_capacity()
            self._carve_spanning_tree()
            if not self.perfect:
                self._braid_dead_ends()
                self._add_extra_loops()
            self.solution = self._find_shortest_path()
            try:
                self._check_result()
                return self.maze
            except RuntimeError as error:
                last_error = str(error)
        raise RuntimeError(
            f"Could not generate a valid maze after {attempts} attempts: "
            f"{last_error}"
        )

    def _check_result(self) -> None:
        """Check the results that can still vary after generation.

        Raises:
            RuntimeError: If the current maze violates an invariant.
        """
        if not self.solution:
            raise RuntimeError("the exit is not reachable")
        if self._has_open_3_by_3():
            raise RuntimeError("the maze contains an open 3x3 area")
        loops = self._loop_count()
        if self.perfect and loops != 0:
            raise RuntimeError("a perfect maze contains a cycle")
        if not self.perfect:
            if loops < 2:
                raise RuntimeError(
                    "a non-perfect board has fewer than two loops"
                )
            if self._real_dead_end_count() > 2:
                raise RuntimeError(
                    "the board has more than two real dead-ends"
                )

    def _validate_parameters(self) -> None:
        """Check the constructor arguments."""
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")
        for name, cell in (("entry", self.entry), ("exit", self.exit)):
            if len(cell) != 2 or not self._inside(cell):
                raise ValueError(f"{name} must be inside the maze")
        if self.entry == self.exit:
            raise ValueError("entry and exit must be different")

    def _reset(self) -> None:
        """Close every wall and discard results from a previous run."""
        self.maze = [
            [ALL_WALLS for _ in range(self.width)]
            for _ in range(self.height)
        ]
        self.solution = []
        self.pattern_cells = set()
        self.warnings = []

    def _place_42_pattern(self) -> None:
        """Place a centred closed-cell ``42`` when dimensions permit."""
        pattern_width = len(_PATTERN_42[0])
        pattern_height = len(_PATTERN_42)
        if self.width < pattern_width + 2 \
                or self.height < pattern_height + 2:
            self.warnings.append(
                "maze too small for the 42 pattern; it was omitted"
            )
            return
        origins = self._pattern_origins(pattern_width, pattern_height)
        for origin_x, origin_y in origins:
            cells = self._pattern_at(origin_x, origin_y)
            if self.entry in cells or self.exit in cells:
                continue
            if not self._centre_remains_open(cells):
                continue
            if self._free_cells_are_connected(cells):
                self.pattern_cells = cells
                return
        self.warnings.append(
            "maze parameters leave no valid position for the 42 pattern; "
            "it was omitted"
        )

    def _pattern_origins(
        self,
        pattern_width: int,
        pattern_height: int,
    ) -> list[Cell]:
        """Return valid origins ordered from the centre outwards."""
        target_x = (self.width - pattern_width) / 2
        target_y = (self.height - pattern_height) / 2
        origins = [
            (x, y)
            for y in range(1, self.height - pattern_height)
            for x in range(1, self.width - pattern_width)
        ]
        return sorted(
            origins,
            key=lambda cell: (
                abs(cell[0] - target_x) + abs(cell[1] - target_y),
                cell[1],
                cell[0],
            ),
        )

    @staticmethod
    def _pattern_at(origin_x: int, origin_y: int) -> set[Cell]:
        """Translate the bitmap font to maze coordinates."""
        return {
            (origin_x + x, origin_y + y)
            for y, row in enumerate(_PATTERN_42)
            for x, value in enumerate(row)
            if value == "1"
        }

    def _centre_remains_open(self, blocked: set[Cell]) -> bool:
        """Keep at least one geometric centre cell available."""
        return any(cell not in blocked for cell in self._centre_cells())

    def _free_cells_are_connected(self, blocked: set[Cell]) -> bool:
        """Check geometric connectivity before carving passages."""
        if self.entry in blocked:
            return False
        seen = {self.entry}
        queue = deque([self.entry])
        while queue:
            cell = queue.popleft()
            for neighbour, _, _ in self._neighbours(cell):
                if neighbour not in blocked and neighbour not in seen:
                    seen.add(neighbour)
                    queue.append(neighbour)
        return len(seen) == self.width * self.height - len(blocked)

    def _check_non_perfect_capacity(self) -> None:
        """Check that the grid can contain at least two cycles."""
        if self.perfect:
            return
        cells = self._normal_cells()
        possible_edges = sum(
            1
            for cell in cells
            for neighbour, wall, _ in self._neighbours(cell)
            if wall in (EAST, SOUTH) and neighbour not in self.pattern_cells
        )
        maximum_loops = possible_edges - len(cells) + 1
        if maximum_loops < 2:
            raise ValueError(
                "PERFECT=False needs enough cells for at least two loops"
            )

    def _carve_spanning_tree(self) -> None:
        """Run an iterative randomized DFS (recursive backtracker)."""
        visited = {self.entry}
        stack = [self.entry]
        while stack:
            cell = stack[-1]
            choices = [
                item
                for item in self._neighbours(cell)
                if item[0] not in visited
                and item[0] not in self.pattern_cells
            ]
            if not choices:
                stack.pop()
                continue
            neighbour, wall, opposite = self._random.choice(choices)
            self._remove_wall(cell, neighbour, wall, opposite)
            visited.add(neighbour)
            stack.append(neighbour)
        expected = self.width * self.height - len(self.pattern_cells)
        if len(visited) != expected:
            raise RuntimeError("the navigable cell layout is disconnected")

    def _braid_dead_ends(self) -> None:
        """Open safe walls until no avoidable dead-end remains."""
        while True:
            dead_ends = [
                cell
                for cell in self._normal_cells()
                if self._open_degree(cell) == 1
                and self._closed_normal_neighbours(cell)
            ]
            if not dead_ends:
                return
            self._random.shuffle(dead_ends)
            progress = False
            for cell in dead_ends:
                if self._open_degree(cell) != 1:
                    continue
                choices = self._closed_normal_neighbours(cell)
                self._random.shuffle(choices)
                choices.sort(key=lambda item: self._open_degree(item[0]))
                for neighbour, wall, opposite in choices:
                    if self._would_create_open_3_by_3(cell, neighbour):
                        continue
                    self._remove_wall(cell, neighbour, wall, opposite)
                    progress = True
                    break
            if not progress:
                return

    def _add_extra_loops(self) -> None:
        """Add route choices without ever creating an open 3x3 area."""
        target = max(2, len(self._normal_cells()) // 12)
        if self._loop_count() >= target:
            return
        candidates = [
            (cell, neighbour, wall, opposite)
            for cell in self._normal_cells()
            for neighbour, wall, opposite in self._neighbours(cell)
            if wall in (EAST, SOUTH)
            and neighbour not in self.pattern_cells
            and self.maze[cell[1]][cell[0]] & wall
        ]
        self._random.shuffle(candidates)
        for cell, neighbour, wall, opposite in candidates:
            if self._loop_count() >= target:
                return
            if self._would_create_open_3_by_3(cell, neighbour):
                continue
            self._remove_wall(cell, neighbour, wall, opposite)

    def _remove_wall(
        self,
        cell: Cell,
        neighbour: Cell,
        wall: int,
        opposite: int,
    ) -> None:
        """Open one passage by clearing both cells' matching wall bits."""
        x, y = cell
        next_x, next_y = neighbour
        self.maze[y][x] &= ~wall
        self.maze[next_y][next_x] &= ~opposite

    def _find_shortest_path(self) -> list[Cell]:
        """Find the shortest entry-to-exit path with breadth-first search."""
        parents: dict[Cell, Cell | None] = {self.entry: None}
        queue = deque([self.entry])
        while queue:
            cell = queue.popleft()
            if cell == self.exit:
                break
            for neighbour, wall, _ in self._neighbours(cell):
                if neighbour in parents or neighbour in self.pattern_cells:
                    continue
                if not self.maze[cell[1]][cell[0]] & wall:
                    parents[neighbour] = cell
                    queue.append(neighbour)
        if self.exit not in parents:
            return []
        path: list[Cell] = []
        current: Cell | None = self.exit
        while current is not None:
            path.append(current)
            current = parents[current]
        path.reverse()
        return path

    def _neighbours(self, cell: Cell) -> list[tuple[Cell, int, int]]:
        """Return in-bounds neighbours with both wall bit values."""
        x, y = cell
        neighbours = []
        for delta_x, delta_y, wall, opposite in _DIRECTIONS:
            neighbour = (x + delta_x, y + delta_y)
            if self._inside(neighbour):
                neighbours.append((neighbour, wall, opposite))
        return neighbours

    def _closed_normal_neighbours(
        self,
        cell: Cell,
    ) -> list[tuple[Cell, int, int]]:
        """Return normal neighbours separated by a closed wall."""
        x, y = cell
        return [
            (neighbour, wall, opposite)
            for neighbour, wall, opposite in self._neighbours(cell)
            if neighbour not in self.pattern_cells
            and self.maze[y][x] & wall
        ]

    def _open_degree(self, cell: Cell) -> int:
        """Count open passages incident to one cell."""
        x, y = cell
        return sum(
            1
            for neighbour, wall, _ in self._neighbours(cell)
            if neighbour not in self.pattern_cells
            and not self.maze[y][x] & wall
        )

    def _would_create_open_3_by_3(
        self,
        first: Cell,
        second: Cell,
    ) -> bool:
        """Predict whether one candidate passage completes a 3x3 room."""
        extra_edge = frozenset((first, second))
        min_x, max_x = sorted((first[0], second[0]))
        min_y, max_y = sorted((first[1], second[1]))
        left_start = max(0, max_x - 2)
        left_stop = min(min_x, self.width - 3)
        top_start = max(0, max_y - 2)
        top_stop = min(min_y, self.height - 3)
        for top in range(top_start, top_stop + 1):
            for left in range(left_start, left_stop + 1):
                if self._open_3_by_3_at(left, top, extra_edge):
                    return True
        return False

    def _has_open_3_by_3(self) -> bool:
        """Return true if any 3x3 block has every internal wall open."""
        for top in range(self.height - 2):
            for left in range(self.width - 2):
                if self._open_3_by_3_at(left, top, frozenset()):
                    return True
        return False

    def _open_3_by_3_at(
        self,
        left: int,
        top: int,
        extra_edge: frozenset[Cell],
    ) -> bool:
        """Check all twelve internal passages of one 3x3 window."""
        cells = {
            (left + x, top + y)
            for y in range(3)
            for x in range(3)
        }
        if cells & self.pattern_cells:
            return False
        horizontal = (
            ((left + x, top + y), (left + x + 1, top + y))
            for y in range(3)
            for x in range(2)
        )
        vertical = (
            ((left + x, top + y), (left + x, top + y + 1))
            for y in range(2)
            for x in range(3)
        )
        return all(
            self._passage_is_open(first, second, extra_edge)
            for first, second in (*horizontal, *vertical)
        )

    def _passage_is_open(
        self,
        first: Cell,
        second: Cell,
        extra_edge: frozenset[Cell],
    ) -> bool:
        """Test an existing passage plus one hypothetical extra edge."""
        if frozenset((first, second)) == extra_edge:
            return True
        delta_x = second[0] - first[0]
        delta_y = second[1] - first[1]
        wall_by_step = {
            (0, -1): NORTH,
            (1, 0): EAST,
            (0, 1): SOUTH,
            (-1, 0): WEST,
        }
        wall = wall_by_step[(delta_x, delta_y)]
        return not self.maze[first[1]][first[0]] & wall

    def _real_dead_end_count(self) -> int:
        """Count dead-ends that could be opened toward a normal cell."""
        return sum(
            1
            for cell in self._normal_cells()
            if self._open_degree(cell) == 1
            and self._closed_normal_neighbours(cell)
        )

    def _loop_count(self) -> int:
        """Return the independent cycle count of the connected graph."""
        edges = sum(
            1
            for x, y in self._normal_cells()
            for wall in (EAST, SOUTH)
            if not self.maze[y][x] & wall
        )
        return edges - len(self._normal_cells()) + 1

    def _normal_cells(self) -> list[Cell]:
        """Return every non-pattern coordinate."""
        return [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in self.pattern_cells
        ]

    def _centre_cells(self) -> set[Cell]:
        """Return the one, two, or four cells around the geometric centre."""
        centre_x = {self.width // 2}
        centre_y = {self.height // 2}
        if self.width % 2 == 0:
            centre_x.add(self.width // 2 - 1)
        if self.height % 2 == 0:
            centre_y.add(self.height // 2 - 1)
        return {(x, y) for y in centre_y for x in centre_x}

    def _inside(self, cell: Cell) -> bool:
        """Return whether an ``(x, y)`` cell belongs to the grid."""
        x, y = cell
        return 0 <= x < self.width and 0 <= y < self.height
