#!/usr/bin/env python3

import sys
from parsing import ConfigParse
from maze_output import MazeOutput

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 config_parser.py <config.txt>")
        sys.exit(1)

    maze = [
        [15, 12, 5],
        [5, 1, 5],
        [10, 8, 9]
    ]

    MazeOutput.write_output_file(maze, "maze.txt")
    MazeOutput.generate_from_output_maze("maze.txt")
    print(ConfigParse.parse_config(sys.argv[1]))