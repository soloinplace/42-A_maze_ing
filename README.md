*This activity has been created as part of the 42 curriculum by csodini, lmauriti.*

# A-Maze-ing

## Description

A-Maze-ing is a Python maze generator driven by a configuration file.

The program generates a random maze with optional deterministic
reproducibility through a seed, writes it using the hexadecimal wall format
required by the subject, computes a shortest path from the entry to the exit,
and provides a visual representation of the result.

Two generation modes are supported:

- `PERFECT=True` generates a perfect maze: all navigable cells are connected
  without cycles.
- `PERFECT=False` starts from the same connected structure and opens
  additional passages to create a more open, Pac-Man-like maze with several
  possible routes and few avoidable dead-ends.

Maze walls are represented with four-bit masks:

- North: `1`
- East: `2`
- South: `4`
- West: `8`

A set bit means that the corresponding wall is closed.

When possible, the maze also contains the required visible `42` pattern made
of fully closed cells.

## Instructions

Python 3.10 or later is required.

The main application is executed with:

```console
python3 a_maze_ing.py config.txt
```

The Makefile provides the following commands:

```console
make install
make run
make debug
make clean
make lint
make lint-strict
make package
```

`make run` uses `config.txt` by default. Another configuration file can be
used with:

```console
make run CONFIG=other_config.txt
```

`make lint` runs the required `flake8` and `mypy` checks.
`make lint-strict` additionally runs `mypy --strict`.

`make package` builds the reusable maze generator package as standard Python
distribution files at the repository root.

### Visual controls

The terminal renderer accepts the following commands:

- `1`: generate and display another maze;
- `2`: show or hide the shortest path;
- `3`: change the wall color;
- `4` or `q`: quit.

Press Enter after each command. On an AZERTY keyboard, `&`, `é`, `"`, and `'`
are also accepted for `1`, `2`, `3`, and `4`.

## Configuration

The configuration file contains one `KEY=VALUE` pair per line.

Empty lines and lines beginning with `#` are ignored.

Example:

```text
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=False
SEED=42
```

The mandatory keys are:

| Key | Description |
| --- | --- |
| `WIDTH` | Maze width in cells |
| `HEIGHT` | Maze height in cells |
| `ENTRY` | Entry coordinates as `x,y` |
| `EXIT` | Exit coordinates as `x,y` |
| `OUTPUT_FILE` | File in which the encoded maze is written |
| `PERFECT` | `True` for a perfect maze, `False` for a non-perfect maze |

`SEED` is optional. When provided, it is parsed as an integer and makes the
random generation reproducible.

The parser rejects malformed lines, duplicate keys, missing mandatory keys,
invalid values, invalid coordinates, and impossible configuration values.

## Maze generation algorithm

### Wall representation

Each maze cell is stored as an integer from `0` to `15`.

The four least significant bits describe its walls:

```text
North = 1
East  = 2
South = 4
West  = 8
```

For example, a cell containing `3` has its North and East walls closed.

The public grid is indexed as:

```python
maze[y][x]
```

### 42 pattern

The generator first closes every wall and searches for a valid position for
the `42` bitmap.

Pattern cells are kept fully closed and excluded from the navigable graph.
The placement algorithm prefers positions near the geometric centre while
avoiding the entry and exit and preserving connectivity of the remaining
cells.

If the maze is too small for the pattern, generation continues without it
and a warning is reported.

### Perfect maze

The navigable cells are considered as vertices of a graph, with possible
passages between adjacent cells.

A randomized iterative depth-first search, equivalent to the recursive
backtracker algorithm, starts from the entry.

When DFS reaches an unvisited neighbouring cell, the wall between the two
cells is removed and the neighbour is marked as visited.

This produces a spanning tree of the navigable cells:

- every navigable cell is connected;
- there are no cycles;
- therefore there is exactly one path between any two navigable cells.

This directly provides the required perfect-maze property.

### Non-perfect maze

Non-perfect generation begins with the same spanning tree.

The generator then braids the maze by opening additional safe walls:

1. avoidable dead-ends are progressively opened;
2. additional passages are added to introduce independent cycles;
3. a wall is never removed when doing so would create a fully open `3x3`
   area.

The resulting graph remains connected while providing several possible
routes. The generated result is checked to contain at least two independent
cycles and no more than two avoidable dead-ends.

### Shortest path

After generation, a breadth-first search (BFS) starts from the entry.

Because every maze passage has the same cost, BFS guarantees that the first
path found to the exit is a shortest path.

Parent links recorded during the search are then followed backwards from the
exit to reconstruct the path.

### Why DFS and BFS?

Randomized DFS was chosen because a depth-first spanning tree naturally
produces a perfect maze while remaining simple to reason about, reproduce
with a seed, and validate.

The non-perfect mode can then reuse the same valid connected structure and
only add passages where needed instead of relying on a completely separate
generation algorithm.

BFS was chosen for pathfinding because it directly guarantees a shortest path
in an unweighted maze graph.

## Output format

The output grid contains one hexadecimal digit per cell and one maze row per
line.

After the grid, an empty line separates a three-line footer containing:

1. the entry coordinates;
2. the exit coordinates;
3. the shortest path encoded with `N`, `E`, `S`, and `W`.

Example structure:

```text
<hexadecimal maze row>
<hexadecimal maze row>
...

0,0
19,14
EESSWN...
```

The output layer assumes that the maze comes from `MazeGenerator`. Before
writing the file, it checks that the solution:

- starts at the configured entry and finishes at the exit;
- stays inside the maze;
- moves only between adjacent cells;
- never crosses a closed wall.

Wall coherence and the other maze properties are guaranteed by the generation
algorithm and checked during development with the provided `maze_analyzer.py`.

## Reusable module

Maze generation is isolated in the standalone `maze_generator.py` module.

It has no dependency on the configuration parser, output serializer, or
display code and can therefore be reused independently in another Python
project.

The generator can be instantiated directly:

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
solution = generator.solution
```

The main parameters are:

- `width`: number of columns;
- `height`: number of rows;
- `entry`: entry as an `(x, y)` tuple;
- `exit`: exit as an `(x, y)` tuple;
- `perfect`: selects perfect or non-perfect generation;
- `seed`: optional deterministic random seed.

After `generate()`, the public attributes are:

- `generator.maze`: the `list[list[int]]` grid, indexed with `maze[y][x]`;
- `generator.solution`: the shortest path as `list[tuple[int, int]]`;
- `generator.pattern_cells`: the cells used for the `42` pattern;
- `generator.warnings`: any non-fatal generation messages.

In a fresh virtual environment, install the standard build frontend and build
the reusable distribution with:

```console
python3 -m pip install build
make package
```

The project uses the standard Python build system with `setuptools` and
produces the `mazegen` package in `.whl` and `.tar.gz` formats.

## Team and project management

### Roles

- **Côme Sodini / csodini**
  - maze generation;
  - graph representation and invariants;
  - perfect and non-perfect generation algorithms;
  - shortest-path computation.

- **Loïc Mauritius / lmauriti**
  - configuration parsing;
  - output serialization and validation;
  - visual representation and display integration.

### Planning and evolution

The initial plan was to divide the project into mostly independent
components so both team members could work in parallel.

The generator, parser, output, and display layers were therefore developed
separately around a small set of shared interfaces.

Integration was moved earlier once the first parser and output components
were available. The main interfaces used between components became:

- the typed `Config` object;
- the `maze[y][x]` wall grid;
- the `solution` list of `(x, y)` coordinates.

This made it possible to integrate and test components without tightly
coupling their internal implementations.

### What worked well

The clear division of responsibilities made parallel development effective.

Keeping maze generation independent from parsing, serialization, and display
also made the generator easier to reason about, test, and package for reuse.

Typed interfaces helped detect integration mistakes early.

### What could be improved

The exact contracts between components, especially output formatting and
application-specific error handling, could have been defined earlier.

Doing so would have reduced some integration work and made the boundaries
between parser, generator, and output layers clearer from the beginning.

### Tools

The project uses:

- Git for version control and collaboration;
- a Makefile for installation, execution, debugging, cleaning, linting, and
  packaging;
- `flake8` for Python style and static checks;
- `mypy` for static type checking;
- Python's built-in `pdb` debugger;
- the subject-provided `maze_analyzer.py` to check wall coherence and maze
  graph properties;
- Python's standard packaging tools with `setuptools`.

## Resources

The main references used during the project were:

- the official Python documentation;
- Python `random` documentation for deterministic pseudo-random generation;
- Python `collections.deque` documentation for DFS/BFS data structures;
- Python packaging documentation for `pyproject.toml`, `setuptools`, wheels,
  and source distributions;
- documentation and explanations of randomized depth-first search /
  recursive backtracking;
- graph theory resources covering spanning trees, connectivity, cycles, and
  breadth-first search;
- the A-Maze-ing subject and its provided `maze_analyzer.py`.

### Use of AI

AI was used as a learning, exploration, and review tool during the project.

It was mainly used to:

- explore and clarify new algorithmic concepts, especially graph
  representation, randomized DFS, spanning trees, cycles, and BFS;
- understand and review the bitmask representation used for maze walls;
- explore Python concepts that were new or unfamiliar during development;
- reason about error handling, exception propagation, and the architecture of
  application-specific errors;
- review the boundaries and interfaces between parsing, generation, output,
  and display components;
- clarify Python packaging and build concepts;
- suggest edge cases and help review implementation choices.

AI-generated suggestions were reviewed and questioned before being retained.
The final code was checked with the project's static-analysis tools and the
provided maze analyzer, and retained code was required to be understood and
explainable by the team.
