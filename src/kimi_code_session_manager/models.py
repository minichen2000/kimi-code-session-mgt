"""Data models for Kimi Code session management."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AgentWireLog:
    """Represents a single Agent's wire.jsonl log file."""

    agent_name: str
    path: Path
    size: int
    line_count: int


@dataclass
class Session:
    """Represents a Kimi Code session."""

    session_id: str
    title: str
    cwd: str
    session_dir: Path
    created_at: int
    updated_at: int
    total_size: int
    agents: list[AgentWireLog] = field(default_factory=list)

    @property
    def workspace_name(self) -> str:
        """Return the parent workspace directory name."""
        return self.session_dir.parent.name


@dataclass
class WorkspaceGroup:
    """Groups sessions that belong to the same working directory."""

    cwd: str
    sessions: list[Session] = field(default_factory=list)

    @property
    def total_size(self) -> int:
        return sum(session.total_size for session in self.sessions)
