"""
MCP tools for the Pomodoro module.
"""
import json
from datetime import datetime, timezone
from app.database import SessionLocal
from app.mcp_tools._shared import _format_item, _format_list, _format_error, _format_deleted
from app.models.pomodoro import PomodoroSession


def _session_to_json(s):
    return _format_item({
        "id": s.id, "session_type": s.session_type, "duration_minutes": s.duration_minutes,
        "started_at": s.started_at, "ended_at": s.ended_at, "completed": s.completed,
    })


def register_pomodoro_tools(mcp, mcp_prefix="swissknife"):
    @mcp.tool(name=f"{mcp_prefix}_pomodoro_status")
    def pomodoro_status() -> str:
        """Check if there is an active (running) pomodoro session."""
        db = SessionLocal()
        try:
            active = db.query(PomodoroSession).filter(PomodoroSession.completed == False)\
                .order_by(PomodoroSession.started_at.desc()).first()
            if active:
                s = json.loads(_session_to_json(active))
                return json.dumps({"active": True, "session": s})
            return json.dumps({"active": False, "session": None})
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_pomodoro_start")
    def pomodoro_start(session_type: str = "focus", duration_minutes: int = 25) -> str:
        """Start a new pomodoro session. Type: focus or break. Duration in minutes (default 25)."""
        db = SessionLocal()
        try:
            active = db.query(PomodoroSession).filter(PomodoroSession.completed == False).first()
            if active:
                return _format_error("An active pomodoro session is already running. Stop it first.")
            session = PomodoroSession(session_type=session_type, duration_minutes=duration_minutes)
            db.add(session)
            db.commit()
            db.refresh(session)
            return _session_to_json(session)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_pomodoro_stop")
    def pomodoro_stop() -> str:
        """Stop the currently running pomodoro session."""
        db = SessionLocal()
        try:
            active = db.query(PomodoroSession).filter(PomodoroSession.completed == False)\
                .order_by(PomodoroSession.started_at.desc()).first()
            if not active:
                return _format_error("No active pomodoro session")
            active.ended_at = datetime.now(timezone.utc)
            active.completed = True
            db.commit()
            db.refresh(active)
            return _session_to_json(active)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_pomodoro_list")
    def pomodoro_list() -> str:
        """List recent pomodoro sessions (last 50)."""
        db = SessionLocal()
        try:
            sessions = db.query(PomodoroSession).order_by(PomodoroSession.started_at.desc()).limit(50).all()
            return _format_list([json.loads(_session_to_json(s)) for s in sessions])
        finally:
            db.close()