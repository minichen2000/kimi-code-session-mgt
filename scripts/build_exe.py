"""Build a single-file Windows executable using PyInstaller."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run(*args: str) -> None:
    subprocess.run([sys.executable, "-m", *args], check=True)


def main() -> None:
    # Ensure code quality before building the executable.
    _run("ruff", "check", ".")
    _run("mypy", "src")
    _run("pytest")

    root = Path(__file__).resolve().parent.parent
    entry = root / "scripts" / "entry.py"
    icon = root / "assets" / "icon.ico"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--onefile",
            "--noconsole",
            "--clean",
            "--name",
            "kimi-session-manager",
            "--icon",
            str(icon),
            "--add-data",
            f"{icon};assets",
            str(entry),
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
