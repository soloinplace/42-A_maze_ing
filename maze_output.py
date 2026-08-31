#!/usr/bin/env python3
"""
    Open the output file and write the maze in hexadecimal.
    Take the output file and make it becomes a maze
"""

from __future__ import annotations
from errors import OutputFileError


def convert_number_base(n: int | str, base: int) -> int | str:
    base_16 = "0123456789ABCDEF"
    if isinstance(n, int):
        if n < 0 or n >= base:
            msg = f"entre 0 - {base - 1} inclus : valeur actuelle = {n}"
            raise ValueError(f"La valeur d'une case doit être comprise {msg}")
        return base_16[n]
    if isinstance(n, str):
        return base_16.index(n.upper())


class MazeOutput:
    """
        Manage the creation / edition of the Output file
        Retrieve the informations to make this a usable maze
    """
    @staticmethod
    def write_output_file(maze: list[list[int]], output: str) -> None:
        try:
            #TODO: Vérifier le maze
            maze_hexa: list[list[str]] = []
            for row in range(0, len(maze)):
                maze_hexa.append([])
                for column in range(0, len(maze[row])):
                    maze_hexa[row].append(
                        convert_number_base(maze[row][column], 16)
                    )
            with open(output, "w", encoding="UTF-8") as f:
                for row in range(0, len(maze_hexa)):
                    f.write("".join(maze_hexa[row]))
                    if (row != len(maze_hexa) - 1):
                        f.write("\n")
            MazeOutput.verif_ouput_file(output)
        except Exception as e:
            print(f"{type(e).__name__}: {e}")


    @staticmethod
    def generate_output_maze(output: str) -> list[list[int]]:
        try:
            MazeOutput.verif_ouput_file(output)
            maze: list[list[int]] = []
            with open(output, "r", encoding="UTF-8") as f:
                content = f.read()
                lines: list[str] = content.split("\n")
                for line in range(0, len(lines)):
                    maze.append([])
                    for character in lines[line]:
                        maze[line].append(
                            convert_number_base(character, 10)
                        )
        except Exception as e:
            print(f"{type(e).__name__}: {e}")
        #TODO: Vérifier le maze
        return maze


    @staticmethod
    def verif_ouput_file(output: str) -> bool:
        import sys

        try:
            with open(output, "r", encoding="UTF-8") as f:
                content = f.read()
                lines: list[str] = content.split("\n")
                for line in range(0, len(lines)):
                    for character in lines[line]:
                        if character not in "0123456789ABCDEF":
                            msg = f"The output file as an error line {line}"
                            raise OutputFileError(f"{msg}: charactère -> {character}")
        except Exception as e:
            print(f"{type(e).__name__}: {e}")
            sys.exit(0)


if __name__ == "__main__":
    maze = [
        [15, 12, 5],
        [5, 1, 5],
        [10, 8, 9]
    ]

    #MazeOutput.write_output_file(maze, "maze.txt")
    MazeOutput.generate_output_maze("maze.txt")
