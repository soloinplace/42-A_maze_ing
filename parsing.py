#!/usr/bin/env python3
"""Parsing and checking of the A-Maze-ing config.txt file."""

from __future__ import annotations
import traceback


class ConfigParse:
    """Parses and checks the A-Maze-ing config.txt file."""

    @staticmethod
    def parse_config(path: str) -> dict[str, object] | None:
        """We read the config file and see if all the keys are respected."""
        configs_file: dict[str, str] = {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    key, _, value = line.partition("=")
                    configs_file[key.strip().upper()] = value.strip()

            width = ConfigParse.check_width(configs_file["WIDTH"])
            height = ConfigParse.check_height(configs_file["HEIGHT"])
            entry = ConfigParse.check_entry(configs_file["ENTRY"])
            exit_ = ConfigParse.check_exit(configs_file["EXIT"])
            output_file = ConfigParse.check_output_file(configs_file["OUTPUT_FILE"])
            perfect = ConfigParse.check_perfect(configs_file["PERFECT"])

            return {
                "width": width,
                "height": height,
                "entry": entry,
                "exit": exit_,
                "output_file": output_file,
                "perfect": perfect,
            }

        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            print(f"Function: {tb[-1].name}()")
            print(f"Error: {type(e).__name__}: {e}")
            return None

    @staticmethod
    def check_width(width: str) -> int:
        """
        Checking if the width is an int and positive

        Return the number width (int)
        """
        w = int(width)
        if w > 0:
            return w
        raise ValueError("La width doit être positive")

    @staticmethod
    def check_height(height: str) -> int:
        """
        Checking if the height is an int and positive

        Return the number height (int)
        """
        h = int(height)
        if h > 0:
            return h
        raise ValueError("La height doit être positive")

    @staticmethod
    def check_entry(entry: str) -> tuple[int, int]:
        """
        Checking if entry is a valid "x,y" coordinate pair

        Return the (x, y) tuple
        """
        x_str, _, y_str = entry.partition(",")
        x, y = int(x_str), int(y_str)
        if x < 0 or y < 0:
            raise ValueError("ENTRY doit être composé de coordonnées >= 0")
        return x, y

    @staticmethod
    def check_exit(exit: str) -> tuple[int, int]:
        """
        Checking if exit is a valid "x,y" coordinate pair

        Return the (x, y) tuple
        """
        x_str, _, y_str = exit.partition(",")
        x, y = int(x_str), int(y_str)
        if x < 0 or y < 0:
            raise ValueError("EXIT doit être composé de coordonnées >= 0")
        return x, y

    @staticmethod
    def check_output_file(output_file: str) -> str:
        """
        Checking that output_file is a non-empty filename

        Return the output_file (str)
        """
        if not output_file:
            raise ValueError("OUTPUT_FILE ne doit pas être vide")
        return output_file

    @staticmethod
    def check_perfect(perfect: str) -> bool:
        """
        Checking if perfect is a valid boolean flag (True/False)

        Return the perfect flag (bool)
        """
        normalized = perfect.strip().lower()
        if normalized in ("true", "1", "yes"):
            return True
        if normalized in ("false", "0", "no"):
            return False
        raise ValueError("PERFECT doit être True ou False")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 config_parser.py <config.txt>")
        sys.exit(1)

    print(ConfigParse.parse_config(sys.argv[1]))