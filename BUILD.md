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

