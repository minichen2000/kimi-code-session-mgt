# Build & Development Guide

## Environment

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) for dependency management

## Setup

```bash
uv sync --group dev
```

## Run

```bash
python scripts/run.py
```

## Test

```bash
uv run pytest
```

## Lint & Format

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

To apply formatting:

```bash
uv run ruff format .
```

## Build Wheel

```bash
uv build
```

## Build Single-File Windows Executable

```bash
uv run python scripts/build_exe.py
```

The executable will be created at `dist/kimi-session-manager.exe`. It is a single-file, portable build that does not show a console window.

### Application Icon

The executable and the runtime window share the same icon: `assets/icon.ico` (committed to the repository). To regenerate it (requires the dev dependency Pillow):

```bash
uv run python scripts/generate_icon.py
```

Colors, corner radius, and text size are constants at the top of that script. The build embeds the icon via `--icon` (file icon) and `--add-data` (runtime window icon).

Pre-built executables are also available on the [GitHub Releases](https://github.com/minichen2000/kimi-code-session-mgt/releases) page.

