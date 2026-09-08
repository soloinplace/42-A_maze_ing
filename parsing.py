#!/usr/bin/env python3
"""Parsing and checking of the A-Maze-ing configuration file."""

from __future__ import annotations

from config import Config
from errors import AMazeIngError


class ConfigParse:
    """Parse and validate the A-Maze-ing configuration file."""

    @staticmethod
    def parse_config(path: str) -> Config:
        """Read *path* and return a fully validated configuration.

        Raises:
            AMazeIngError: If the file or one of its values is invalid.
        """
        try:
            values = ConfigParse._read_values(path)
            missing = ConfigParse._missing_keys(values)
            if missing:
                names = ", ".join(sorted(missing))
                raise ValueError(f"missing mandatory key(s): {names}")
            return Config(
                width=int(values["WIDTH"]),
                height=int(values["HEIGHT"]),
                entry=ConfigParse._parse_coordinate(
                    values["ENTRY"], "ENTRY"
                ),
                exit=ConfigParse._parse_coordinate(values["EXIT"], "EXIT"),
                output_file=values["OUTPUT_FILE"],
                perfect=ConfigParse._parse_bool(values["PERFECT"]),
                seed=(
                    int(values["SEED"])
                    if "SEED" in values
                    else None
                ),
            )
        except OSError as error:
            raise AMazeIngError(
                f"cannot read configuration file {path!r}: {error}"
            ) from error
        except ValueError as error:
            raise AMazeIngError(f"invalid configuration: {error}") \
                from error

    @staticmethod
    def _read_values(path: str) -> dict[str, str]:
        """Read key-value pairs and reject malformed or duplicate lines."""
        values: dict[str, str] = {}
        with open(path, "r", encoding="utf-8") as stream:
            for number, raw_line in enumerate(stream, start=1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ValueError(f"line {number}: expected KEY=VALUE")
                key, value = (part.strip() for part in line.split("=", 1))
                key = key.upper()
                if not key or not value:
                    raise ValueError(f"line {number}: empty key or value")
                if key in values:
                    raise ValueError(f"line {number}: duplicate key {key}")
                values[key] = value
        return values

    @staticmethod
    def _missing_keys(values: dict[str, str]) -> set[str]:
        """Return mandatory keys absent from the parsed mapping."""
        mandatory = {
            "WIDTH",
            "HEIGHT",
            "ENTRY",
            "EXIT",
            "OUTPUT_FILE",
            "PERFECT",
        }
        return mandatory - values.keys()

    @staticmethod
    def _parse_coordinate(value: str, name: str) -> tuple[int, int]:
        """Parse exactly two integers separated by a comma."""
        parts = value.split(",")
        if len(parts) != 2:
            raise ValueError(f"{name} must use the x,y format")
        x, y = parts
        return int(x.strip()), int(y.strip())

    @staticmethod
    def _parse_bool(value: str) -> bool:
        """Parse the True or False value used by PERFECT."""
        normalized = value.lower()
        if normalized == "true":
            return True
        if normalized == "false":
            return False
        raise ValueError("PERFECT must be True or False")
