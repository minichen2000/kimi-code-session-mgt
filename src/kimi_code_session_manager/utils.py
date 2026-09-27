"""Utility functions for formatting and platform integration."""

from __future__ import annotations

import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def format_size(size: int) -> str:
    """Format a byte size as human-readable string."""
    if size < 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    for unit in units:
        if value < 1024:
            return (
                f"{value:.1f} {unit}"
                if value != int(value) or unit == "B"
                else f"{int(value)} {unit}"
            )
        value /= 1024
    return f"{value:.1f} PB"


def format_timestamp_ms(timestamp_ms: int) -> str:
    """Format a millisecond timestamp as a local datetime string."""
    try:
        dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
        return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")
    except (OSError, ValueError, OverflowError):
        return "未知"


def get_sessions_root() -> Path:
    """Return the Kimi Code sessions root directory."""
    env_root = os.environ.get("KIMI_SESSIONS_ROOT")
    if env_root:
        return Path(env_root).expanduser()

    home = Path.home()
    return home / ".kimi-code" / "sessions"


def reveal_in_file_manager(path: Path) -> None:
    """Open the file manager at the given path and select it if possible."""
    system = platform.system()
    absolute = str(path.resolve())

    if system == "Windows":
        # explorer /select expects Windows-style backslash paths.
        win_path = absolute.replace("/", "\\")
        subprocess.run(["explorer", f"/select,{win_path}"], check=False)
    elif system == "Darwin":
        subprocess.run(["open", "-R", absolute], check=False)
    else:
        # Linux and other Unix-like systems: open the parent directory.
        target = absolute if path.is_dir() else str(path.parent)
        subprocess.run(["xdg-open", target], check=False)


def get_directory_size(path: Path) -> int:
    """Calculate total byte size of a directory recursively."""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=False):
                total += get_directory_size(Path(entry.path))
            else:
                total += entry.stat(follow_symlinks=False).st_size
    except OSError:
        pass
    return total


def count_lines(path: Path) -> int:
    """Count lines in a text file efficiently."""
    count = 0
    try:
        with path.open("rb") as f:
            for _ in f:
                count += 1
    except OSError:
        pass
    return count
