#!/usr/bin/env python3
"""Read and write the normalized hexadecimal maze output format."""

from __future__ import annotations

from errors import OutputFileError

Cell = tuple[int, int]

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8


class MazeOutput:
    """Serialize maze walls and the shortest path to the output file."""

    @staticmethod
    def write_output_file(
        maze: list[list[int]],
        output: str,
        entry: Cell,
        exit: Cell,
        solution: list[Cell],
    ) -> None:
        """Validate and write the complete subject-mandated file."""
        MazeOutput._validate_maze(maze)
        directions = MazeOutput.path_to_directions(
            maze,
            entry,
            exit,
            solution,
        )
        grid_lines = [
            "".join(format(value, "X") for value in row)
            for row in maze
        ]
        lines = grid_lines + [
            "",
            f"{entry[0]},{entry[1]}",
            f"{exit[0]},{exit[1]}",
            directions,
        ]
        try:
            with open(output, "w", encoding="utf-8") as stream:
                stream.write("\n".join(lines) + "\n")
        except OSError as error:
            raise OutputFileError(
                f"cannot write output file {output!r}: {error}"
            ) from error

    @staticmethod
    def read_output_file(
        output: str,
    ) -> tuple[list[list[int]], Cell, Cell, str]:
        """Read and validate a complete maze output file."""
        try:
            with open(output, "r", encoding="utf-8") as stream:
                lines = stream.read().splitlines()
        except OSError as error:
            raise OutputFileError(
                f"cannot read output file {output!r}: {error}"
            ) from error
        try:
            divider = lines.index("")
        except ValueError as error:
            message = "output file has no blank footer separator"
            raise OutputFileError(message) from error
        footer = lines[divider + 1:]
        if len(footer) != 3:
            raise OutputFileError("output footer must contain exactly 3 lines")
        maze = MazeOutput._parse_grid(lines[:divider])
        entry = MazeOutput._parse_coordinate(footer[0], "entry")
        exit_ = MazeOutput._parse_coordinate(footer[1], "exit")
        if any(letter not in "NESW" for letter in footer[2]):
            raise OutputFileError("path contains a letter outside N, E, S, W")
        MazeOutput._validate_encoded_path(maze, entry, exit_, footer[2])
        return maze, entry, exit_, footer[2]

    @staticmethod
    def generate_from_output_maze(output: str) -> list[list[int]]:
        """Return only the grid, preserving the mate's previous API."""
        maze, _, _, _ = MazeOutput.read_output_file(output)
        return maze

    @staticmethod
    def verify_output_file(output: str) -> bool:
        """Return true when *output* follows the complete expected format."""
        MazeOutput.read_output_file(output)
        return True

    @staticmethod
    def verif_ouput_file(output: str) -> bool:
        """Keep compatibility with the mate's previous misspelled method."""
        return MazeOutput.verify_output_file(output)

    @staticmethod
    def path_to_directions(
        maze: list[list[int]],
        entry: Cell,
        exit: Cell,
        solution: list[Cell],
    ) -> str:
        """Convert a coordinate path to the required N/E/S/W letters."""
        if not solution or solution[0] != entry or solution[-1] != exit:
            message = "solution must start at ENTRY and end at EXIT"
            raise OutputFileError(message)
        width = len(maze[0])
        height = len(maze)
        if any(
            not 0 <= x < width or not 0 <= y < height
            for x, y in solution
        ):
            raise OutputFileError("solution contains an out-of-bounds cell")
        moves = {
            (0, -1): ("N", NORTH),
            (1, 0): ("E", EAST),
            (0, 1): ("S", SOUTH),
            (-1, 0): ("W", WEST),
        }
        directions = []
        for first, second in zip(solution, solution[1:]):
            step = (second[0] - first[0], second[1] - first[1])
            if step not in moves:
                raise OutputFileError("solution contains non-adjacent cells")
            letter, wall = moves[step]
            if maze[first[1]][first[0]] & wall:
                raise OutputFileError("solution crosses a closed wall")
            directions.append(letter)
        return "".join(directions)

    @staticmethod
    def _parse_grid(lines: list[str]) -> list[list[int]]:
        """Parse rectangular rows containing one hexadecimal digit per cell."""
        if not lines or not lines[0]:
            raise OutputFileError("output grid is empty")
        width = len(lines[0])
        maze = []
        for number, line in enumerate(lines, start=1):
            if len(line) != width:
                raise OutputFileError(f"grid row {number} has a wrong width")
            try:
                maze.append([int(character, 16) for character in line])
            except ValueError as error:
                raise OutputFileError(
                    f"grid row {number} contains a non-hexadecimal cell"
                ) from error
        MazeOutput._validate_maze(maze)
        return maze

    @staticmethod
    def _parse_coordinate(value: str, name: str) -> Cell:
        """Parse one footer coordinate in x,y form."""
        parts = value.split(",")
        if len(parts) != 2:
            raise OutputFileError(f"{name} must use the x,y format")
        try:
            return int(parts[0]), int(parts[1])
        except ValueError as error:
            raise OutputFileError(f"{name} contains a non-integer") from error

    @staticmethod
    def _validate_maze(maze: list[list[int]]) -> None:
        """Reject empty, irregular, or out-of-range wall grids."""
        if not maze or not maze[0]:
            raise OutputFileError("maze must not be empty")
        width = len(maze[0])
        if any(len(row) != width for row in maze):
            raise OutputFileError("maze rows must all have the same width")
        if any(not 0 <= value <= 15 for row in maze for value in row):
            raise OutputFileError("maze cells must be integers from 0 to 15")
        MazeOutput._validate_walls(maze)

    @staticmethod
    def _validate_walls(maze: list[list[int]]) -> None:
        """Check closed borders and agreement between neighbouring cells."""
        height = len(maze)
        width = len(maze[0])
        if any(not maze[0][x] & NORTH for x in range(width)):
            raise OutputFileError("maze north border must stay closed")
        if any(not maze[height - 1][x] & SOUTH for x in range(width)):
            raise OutputFileError("maze south border must stay closed")
        if any(not row[0] & WEST for row in maze):
            raise OutputFileError("maze west border must stay closed")
        if any(not row[width - 1] & EAST for row in maze):
            raise OutputFileError("maze east border must stay closed")
        for y in range(height):
            for x in range(width):
                if x + 1 < width:
                    east = bool(maze[y][x] & EAST)
                    west = bool(maze[y][x + 1] & WEST)
                    if east != west:
                        raise OutputFileError("maze has incoherent walls")
                if y + 1 < height:
                    south = bool(maze[y][x] & SOUTH)
                    north = bool(maze[y + 1][x] & NORTH)
                    if south != north:
                        raise OutputFileError("maze has incoherent walls")

    @staticmethod
    def _validate_encoded_path(
        maze: list[list[int]],
        entry: Cell,
        exit: Cell,
        path: str,
    ) -> None:
        """Ensure the footer path stays in bounds and crosses open walls."""
        width = len(maze[0])
        height = len(maze)
        x, y = entry
        if not 0 <= x < width or not 0 <= y < height:
            raise OutputFileError("entry is outside the maze")
        moves = {
            "N": (0, -1, NORTH),
            "E": (1, 0, EAST),
            "S": (0, 1, SOUTH),
            "W": (-1, 0, WEST),
        }
        for letter in path:
            delta_x, delta_y, wall = moves[letter]
            if maze[y][x] & wall:
                raise OutputFileError("encoded path crosses a closed wall")
            x += delta_x
            y += delta_y
            if not 0 <= x < width or not 0 <= y < height:
                raise OutputFileError("encoded path leaves the maze")
        if (x, y) != exit:
            raise OutputFileError("encoded path does not finish at EXIT")
