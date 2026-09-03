#!/usr/bin/env python3
"""Parsing and checking of the A-Maze-ing configuration file."""

from __future__ import annotations

from config import Config
from errors import ConfigurationError


class ConfigParse:
    """Parse and validate the A-Maze-ing configuration file."""

    @staticmethod
    def parse_config(path: str) -> Config:
        """Read *path* and return a fully validated configuration.

        Raises:
            ConfigurationError: If the file or one of its values is invalid.
        """
        try:
            values = ConfigParse._read_values(path)
            missing = ConfigParse._missing_keys(values)
            if missing:
                names = ", ".join(sorted(missing))
                raise ValueError(f"missing mandatory key(s): {names}")
            return Config(
                width=ConfigParse.check_width(values["WIDTH"]),
                height=ConfigParse.check_height(values["HEIGHT"]),
                entry=ConfigParse.check_entry(values["ENTRY"]),
                exit=ConfigParse.check_exit(values["EXIT"]),
                output_file=ConfigParse.check_output_file(
                    values["OUTPUT_FILE"]
                ),
                perfect=ConfigParse.check_perfect(values["PERFECT"]),
                seed=ConfigParse.check_seed(values.get("SEED")),
            )
        except OSError as error:
            raise ConfigurationError(
                f"cannot read configuration file {path!r}: {error}"
            ) from error
        except (KeyError, TypeError, ValueError) as error:
            raise ConfigurationError(f"invalid configuration: {error}") \
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
    def check_width(width: str) -> int:
        """Return a strictly positive maze width."""
        value = int(width)
        if value > 0:
            return value
        raise ValueError("WIDTH must be positive")

    @staticmethod
    def check_height(height: str) -> int:
        """Return a strictly positive maze height."""
        value = int(height)
        if value > 0:
            return value
        raise ValueError("HEIGHT must be positive")

    @staticmethod
    def check_entry(entry: str) -> tuple[int, int]:
        """Return ENTRY parsed as a non-negative ``(x, y)`` pair."""
        return ConfigParse._check_coordinate(entry, "ENTRY")

    @staticmethod
    def check_exit(exit: str) -> tuple[int, int]:
        """Return EXIT parsed as a non-negative ``(x, y)`` pair."""
        return ConfigParse._check_coordinate(exit, "EXIT")

    @staticmethod
    def _check_coordinate(value: str, name: str) -> tuple[int, int]:
        """Parse exactly two non-negative integers separated by a comma."""
        parts = value.split(",")
        if len(parts) != 2:
            raise ValueError(f"{name} must use the x,y format")
        x, y = (int(part.strip()) for part in parts)
        if x < 0 or y < 0:
            raise ValueError(f"{name} coordinates must be non-negative")
        return x, y

    @staticmethod
    def check_output_file(output_file: str) -> str:
        """Return a non-empty output filename."""
        if not output_file:
            raise ValueError("OUTPUT_FILE must not be empty")
        return output_file

    @staticmethod
    def check_perfect(perfect: str) -> bool:
        """Parse a textual boolean flag."""
        normalized = perfect.strip().lower()
        if normalized in ("true", "1", "yes"):
            return True
        if normalized in ("false", "0", "no"):
            return False
        raise ValueError("PERFECT must be True or False")

    @staticmethod
    def check_seed(seed: str | None) -> int | None:
        """Parse the optional deterministic random seed."""
        return None if seed is None else int(seed)
