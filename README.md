*This activity has been created as part of the 42 curriculum by csodini, lmauriti.*

# A-Maze-ing

## Description

A-Maze-ing generates a deterministic maze from a configuration file. It
supports a perfect mode (one connected spanning tree) and a braided,
Pac-Man-like mode (several routes and very few dead-ends). Every wall is
stored as a four-bit mask and the output includes the shortest path.

## Instructions

Use Python 3.10 or later:

```console
make install
make run
make lint
make package
```

The application command is:

```console
python3 a_maze_ing.py config.txt
```

## Configuration

The file contains one `KEY=VALUE` pair per line. Empty lines and lines that
start with `#` are ignored.

```text
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=False
SEED=42
```

The first six keys are mandatory. `SEED` is optional and makes generation
reproducible.

## Generation algorithm

`MazeGenerator` starts with every wall closed and treats the cells of the
visible `42` as obstacles. A randomized depth-first search then links every
normal cell exactly once to create a spanning tree. This directly guarantees
connectivity without cycles in perfect mode.

In non-perfect mode, the generator opens additional safe walls. It first
removes avoidable dead-ends, then adds independent cycles. A candidate wall
is never removed if that removal would complete a fully open 3x3 area. A BFS
computes the shortest path in both modes.

This approach was chosen because each main requirement follows from a small,
explainable invariant rather than from a large special-case algorithm.

## Reusable module

The standalone `maze_generator.py` module contains the reusable logic and has
no dependency on parsing, output, or display code.

```python
from maze_generator import MazeGenerator

generator = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit=(19, 14),
    perfect=True,
    seed=42,
)
maze = generator.generate()
solution = generator.get_solution()
```

The grid is `list[list[int]]` and is indexed as `maze[y][x]`. The path is a
`list[tuple[int, int]]` containing `(x, y)` coordinates.

## Team and project management

- Paradise / soloinplace: maze generation, graph invariants, shortest path,
  and reusable packaging.
- Lockelfe / Loic: configuration parsing, output serialization, and display.
- The team integrated through the typed `Config`, `maze`, and `solution`
  interfaces. Planning evolved from separate components to early integration
  after the parser and first output implementation were shared.
- Static checks, the provided `maze_analyzer.py`, and generated edge cases are
  used to catch integration errors.
- The clear division of responsibilities worked well. Earlier agreement on
  the exact output and exception contracts would have reduced rework during
  integration.

## Resources

- Python documentation: `random`, `collections.deque`, and packaging guides.
- Maze algorithms: randomized depth-first search / recursive backtracker.
- Graph concepts: spanning trees, independent cycles, and BFS.
- The subject-provided `maze_analyzer.py` validates wall coherence and graph
  properties.
- AI was used to clarify the subject, review integration code, propose tests,
  and explain algorithms. Every generated change was reviewed and tested by
  the team, which remains responsible for the submitted code.
