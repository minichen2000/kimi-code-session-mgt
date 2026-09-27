# Kimi Code Session Manager

A cross-platform GUI tool for managing [Kimi Code](https://kimi-code.moonshot.cn/) sessions.

## Features

- Browse all Kimi Code sessions grouped by workspace directory.
- See session metadata: title, created time, updated time, and total size.
- Inspect every Agent's `wire.jsonl` log inside a session.
- Reveal session folders or individual `wire.jsonl` files in your file manager.
- Delete sessions safely with a confirmation dialog.
- Zero runtime third-party dependencies — uses Python's built-in `tkinter`.

## Quick Start

```bash
# Run from source
python scripts/run.py
```

Or, after installing the package:

```bash
kimi-session-manager
```

## Requirements

- Python 3.10+
- `tkinter` (usually bundled with Python)

## Development

See [BUILD.md](BUILD.md) for development and build instructions.

## License

MIT
