"""Tests for the session scanner."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from kimi_code_session_manager.scanner import scan_all_sessions, scan_session
from kimi_code_session_manager.utils import get_directory_size


def _make_state_json(
    session_dir: Path,
    *,
    session_id: str | None = None,
    title: str = "Test Session",
    cwd: str = "C:/data/test",
    created_at: int = 1000,
    updated_at: int = 2000,
) -> None:
    session_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "id": session_id or session_dir.name,
        "title": title,
        "cwd": cwd,
        "createdAt": created_at,
        "updatedAt": updated_at,
    }
    (session_dir / "state.json").write_text(json.dumps(data), encoding="utf-8")


def _make_wire_jsonl(agent_dir: Path, lines: list[str]) -> None:
    agent_dir.mkdir(parents=True, exist_ok=True)
    content = "\n".join(lines) + "\n"
    (agent_dir / "wire.jsonl").write_text(content, encoding="utf-8")


@pytest.fixture
def fake_sessions(tmp_path: Path) -> Path:
    """Create a fake Kimi Code sessions root."""
    root = tmp_path / "sessions"
    workspace = root / "wd_test_12345678"

    session_a = workspace / "session_a1111111-1111-1111-1111-111111111111"
    _make_state_json(
        session_a,
        session_id="session_a",
        title="Alpha",
        cwd="C:/data/alpha",
        created_at=1000,
        updated_at=3000,
    )
    _make_wire_jsonl(session_a / "agents" / "main", ["line1", "line2", "line3"])

    session_b = workspace / "session_b2222222-2222-2222-2222-222222222222"
    _make_state_json(
        session_b,
        session_id="session_b",
        title="Beta",
        cwd="C:/data/alpha",  # same cwd as Alpha to test grouping
        created_at=2000,
        updated_at=4000,
    )
    _make_wire_jsonl(session_b / "agents" / "main", ["a", "b"])
    _make_wire_jsonl(session_b / "agents" / "agent-0", ["x"])

    session_c = workspace / "session_c3333333-3333-3333-3333-333333333333"
    _make_state_json(
        session_c,
        session_id="session_c",
        title="Gamma",
        cwd="C:/data/gamma",
        created_at=500,
        updated_at=500,
    )
    # No agents directory.

    return root


def test_scan_session_reads_metadata_and_wire_logs(fake_sessions: Path) -> None:
    session_dir = (
        fake_sessions / "wd_test_12345678" / "session_a1111111-1111-1111-1111-111111111111"
    )
    session = scan_session(session_dir)

    assert session is not None
    assert session.session_id == "session_a"
    assert session.title == "Alpha"
    assert session.cwd == "C:/data/alpha"
    assert session.created_at == 1000
    assert session.updated_at == 3000
    assert session.total_size == get_directory_size(session_dir)
    assert len(session.agents) == 1
    assert session.agents[0].agent_name == "main"
    assert session.agents[0].line_count == 3


def test_scan_session_without_state_json_is_tolerant(fake_sessions: Path) -> None:
    session_dir = (
        fake_sessions / "wd_test_12345678" / "session_d4444444-4444-4444-4444-444444444444"
    )
    session_dir.mkdir(parents=True)
    (session_dir / "agents" / "main").mkdir(parents=True)
    (session_dir / "agents" / "main" / "wire.jsonl").write_text("{}\n", encoding="utf-8")

    session = scan_session(session_dir)

    assert session is not None
    assert session.session_id == session_dir.name
    assert session.title == session_dir.name
    assert session.cwd == str(session_dir.parent)
    assert len(session.agents) == 1


def test_scan_all_sessions_groups_by_cwd(fake_sessions: Path) -> None:
    groups = scan_all_sessions(fake_sessions)

    assert len(groups) == 2
    cwds = [group.cwd for group in groups]
    assert cwds == ["C:/data/alpha", "C:/data/gamma"]

    alpha_group = next(group for group in groups if group.cwd == "C:/data/alpha")
    assert len(alpha_group.sessions) == 2
    assert alpha_group.sessions[0].title == "Beta"  # updated_at descending
    assert alpha_group.sessions[1].title == "Alpha"

    gamma_group = next(group for group in groups if group.cwd == "C:/data/gamma")
    assert len(gamma_group.sessions) == 1
    assert gamma_group.sessions[0].title == "Gamma"


def test_scan_all_sessions_ignores_non_session_directories(fake_sessions: Path) -> None:
    (fake_sessions / "wd_test_12345678" / "not_a_session").mkdir()
    (fake_sessions / "not_a_workspace").mkdir()

    groups = scan_all_sessions(fake_sessions)
    assert len(groups) == 2
