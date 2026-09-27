# Kimi Code Session Manager

A cross-platform GUI tool for managing [Kimi Code](https://kimi-code.moonshot.cn/) sessions.

## Features

- Browse all Kimi Code sessions in a flat list.
- Sort sessions by title, updated time, wire size, or agent count.
- See session metadata: title, created time, updated time, and wire log size.
- Inspect every Agent's `wire.jsonl` log inside a session.
- Reveal session folders or individual `wire.jsonl` files in your file manager.
- Delete sessions safely with a confirmation dialog.
- Adjustable font size.
- Zero runtime third-party dependencies — uses Python's built-in `tkinter`.

## Quick Start

### From Source

```bash
python scripts/run.py
```

Or, after installing the package:

```bash
kimi-session-manager
```

### Windows Executable

A single-file executable is also available. See [BUILD.md](BUILD.md) for build instructions.


## Requirements

- Python 3.10+
- `tkinter` (usually bundled with Python)

## Development

See [BUILD.md](BUILD.md) for development and build instructions.

## License

MIT
