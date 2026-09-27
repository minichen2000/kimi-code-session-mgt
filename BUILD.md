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
