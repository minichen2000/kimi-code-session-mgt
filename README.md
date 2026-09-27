# Kimi Code Session Manager

A cross-platform GUI tool for managing [Kimi Code](https://kimi-code.moonshot.cn/) sessions.

## Features

- Browse all Kimi Code sessions in a flat list.
- Sort sessions by title, updated time, wire size, or agent count (click column headers).
- See session metadata: title, created time, updated time, and wire log size.
- Inspect every Agent's `wire.jsonl` log inside a session.
- Reveal session folders or individual `wire.jsonl` files in your file manager.
- Delete sessions safely with a confirmation dialog.
- Adjustable font size.
- Alternating row colors and column dividers for better readability.
- Window is centered on screen at startup.
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

Download `kimi-session-manager.exe` from the [GitHub Releases](https://github.com/minichen2000/kimi-code-session-mgt/releases) page. It is a single-file, portable build that does not show a console window.

To build it yourself, see [BUILD.md](BUILD.md).


## Requirements

- Python 3.10+
- `tkinter` (usually bundled with Python)

## Development

See [BUILD.md](BUILD.md) for development and build instructions.

## License

MIT
