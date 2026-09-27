"""Filesystem scanner for Kimi Code sessions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from kimi_code_session_manager.models import AgentWireLog, Session, WorkspaceGroup
from kimi_code_session_manager.utils import count_lines, get_directory_size, get_sessions_root


def _parse_state_json(state_path: Path) -> dict[str, Any]:
    """Parse a state.json file, returning an empty dict on failure."""
    try:
        with state_path.open("r", encoding="utf-8") as f:
            return json.load(f)  # type: ignore[no-any-return]
    except (json.JSONDecodeError, OSError):
        return {}


def _scan_agents(session_dir: Path) -> list[AgentWireLog]:
    """Find all Agent wire.jsonl logs inside a session directory."""
    agents_dir = session_dir / "agents"
    logs: list[AgentWireLog] = []
    if not agents_dir.is_dir():
        return logs

    for agent_dir in sorted(agents_dir.iterdir()):
        if not agent_dir.is_dir():
            continue
        wire_path = agent_dir / "wire.jsonl"
        if wire_path.is_file():
            size = wire_path.stat().st_size
            logs.append(
                AgentWireLog(
                    agent_name=agent_dir.name,
                    path=wire_path,
                    size=size,
                    line_count=count_lines(wire_path),
                )
            )
    return logs


def scan_session(session_dir: Path) -> Session | None:
    """Scan a single session directory and return its model."""
    if not session_dir.is_dir():
        return None

    state_path = session_dir / "state.json"
    state = _parse_state_json(state_path)

    session_id = state.get("id") or session_dir.name
    title = state.get("title") or session_id
    cwd = state.get("cwd") or str(session_dir.parent)
    created_at = state.get("createdAt", 0)
    updated_at = state.get("updatedAt", created_at)

    agents = _scan_agents(session_dir)
    total_size = get_directory_size(session_dir)

    return Session(
        session_id=session_id,
        title=title,
        cwd=cwd,
        session_dir=session_dir,
        created_at=created_at,
        updated_at=updated_at,
        total_size=total_size,
        agents=agents,
    )


def scan_all_sessions(sessions_root: Path | None = None) -> list[WorkspaceGroup]:
    """Scan the entire Kimi Code sessions root and group sessions by cwd."""
    if sessions_root is None:
        sessions_root = get_sessions_root()

    groups: dict[str, WorkspaceGroup] = {}

    if not sessions_root.is_dir():
        return []

    for workspace_dir in sorted(sessions_root.iterdir()):
        if not workspace_dir.is_dir() or not workspace_dir.name.startswith("wd_"):
            continue

        for session_dir in sorted(workspace_dir.iterdir()):
            if not session_dir.is_dir() or not session_dir.name.startswith("session_"):
                continue

            session = scan_session(session_dir)
            if session is None:
                continue

            cwd = session.cwd
            if cwd not in groups:
                groups[cwd] = WorkspaceGroup(cwd=cwd)
            groups[cwd].sessions.append(session)

    # Sort groups by cwd and sessions within each group by updated time descending.
    for group in groups.values():
        group.sessions.sort(key=lambda s: s.updated_at, reverse=True)

    return sorted(groups.values(), key=lambda g: g.cwd)
