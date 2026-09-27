"""Build a single-file Windows executable using PyInstaller."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    entry = Path(__file__).resolve().parent / "entry.py"
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
            str(entry),
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
