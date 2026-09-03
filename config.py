"""Typed application configuration."""

from __future__ import annotations

from dataclasses import dataclass

Cell = tuple[int, int]


@dataclass(frozen=True)
class Config:
    """Hold one completely parsed and validated configuration."""

    width: int
    height: int
    entry: Cell
    exit: Cell
    output_file: str
    perfect: bool
    seed: int | None = None

    def __post_init__(self) -> None:
        """Validate relationships that depend on several fields."""
        if self.width <= 0 or self.height <= 0:
            raise ValueError("WIDTH and HEIGHT must be positive")
        for name, (x, y) in (("ENTRY", self.entry), ("EXIT", self.exit)):
            if not 0 <= x < self.width or not 0 <= y < self.height:
                raise ValueError(f"{name} must be inside the maze")
        if self.entry == self.exit:
            raise ValueError("ENTRY and EXIT must be different")
        if not self.output_file:
            raise ValueError("OUTPUT_FILE must not be empty")

    @property
    def exit_(self) -> Cell:
        """Keep compatibility with the previous attribute name."""
        return self.exit
