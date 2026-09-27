# Agent Notes

## Project Overview

A cross-platform GUI tool for managing Kimi Code sessions. Built with Python 3 and Tkinter so it has zero runtime third-party dependencies.

## Architecture Decisions

- **GUI**: `tkinter` from the Python standard library. No PyQt, no Electron, no web stack — keeps the tool lightweight and easy to run anywhere Python is installed.
- **Session discovery**: Scan the filesystem under the Kimi Code sessions root (`~/.kimi-code/sessions` or `%USERPROFILE%/.kimi-code/sessions`). Parse each `session_<uuid>/state.json` for metadata and scan `agents/<agent_name>/wire.jsonl` for logs.
- **Grouping**: Sessions are grouped by their `cwd` (working directory) from `state.json`. If `cwd` is missing, the parent workspace directory name (`wd_<name>_<hash>`) is used as a fallback.
- **Size calculation**: Total size includes the entire `session_<uuid>` directory (logs, media, file-history, agent data, etc.), not just `wire.jsonl`.
- **Reveal in file manager**: Platform-specific commands:
  - Windows: `explorer /select,"<path>"`
  - macOS: `open -R "<path>"`
  - Linux: `xdg-open "<dir>"`

## Coding Conventions

- Follow PEP 8 via `ruff`.
- Type hints are required for public functions and classes (`mypy --strict`).
- Keep GUI code separate from scanner/model logic.
- All user-facing strings in the GUI are in Chinese because the primary users speak Chinese.

## Known Pitfalls

- `state.json` may be missing or malformed if a session was interrupted. The scanner must tolerate this and continue.
- `wire.jsonl` can be very large; the GUI should not load the entire file into memory automatically. Show a preview of the first/last N lines and offer to open it externally.
- Deleting a session is irreversible. Always show a confirmation dialog and delete only the `session_<uuid>` directory, never the parent `wd_*` workspace directory.

## External Dependencies

- None at runtime.
- Dev dependencies: `pytest`, `ruff`, `mypy`.

## Agent Handoff Checklist

1. Read `AGENTS.md` (this file).
2. Read `PROGRESS.md` for current status and TODOs.
3. Read `README.md` / `BUILD.md` for usage and build instructions.
