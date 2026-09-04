#!/usr/bin/env python3
"""Write the normalized hexadecimal maze output format."""

from __future__ import annotations

from errors import AMazeIngError
from maze_generator import EAST, NORTH, SOUTH, WEST

Cell = tuple[int, int]


class MazeOutput:
    """Write the generated maze to its output file."""

    @staticmethod
    def write_output_file(
        maze: list[list[int]],
        output_file: str,
        entry: Cell,
        exit: Cell,
        solution: list[Cell],
    ) -> None:
        """Write the maze and its shortest path to a file."""
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
            with open(output_file, "w", encoding="utf-8") as stream:
                stream.write("\n".join(lines) + "\n")
        except OSError as error:
            raise AMazeIngError(
                f"cannot write output file {output_file!r}: {error}"
            ) from error

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
            raise AMazeIngError(message)
        width = len(maze[0])
        height = len(maze)
        if any(
            not 0 <= x < width or not 0 <= y < height
            for x, y in solution
        ):
            raise AMazeIngError("solution contains an out-of-bounds cell")
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
                raise AMazeIngError("solution contains non-adjacent cells")
            letter, wall = moves[step]
            if maze[first[1]][first[0]] & wall:
                raise AMazeIngError("solution crosses a closed wall")
            directions.append(letter)
        return "".join(directions)
