"""
MCP tools for the Pomodoro module.
"""
from datetime import datetime, timezone
from app.database import SessionLocal
from app.models.pomodoro import PomodoroSession


def _session_to_json(s):
    ended = f'"{s.ended_at.isoformat()}"' if s.ended_at else "null"
    return (
        f'{{"id":{s.id},"session_type":"{s.session_type}","duration_minutes":{s.duration_minutes},'
        f'"started_at":"{s.started_at.isoformat()}","ended_at":{ended},"completed":{str(s.completed).lower()}}}'
    )


def register_pomodoro_tools(mcp, mcp_prefix="swissknife"):
    @mcp.tool(name=f"{mcp_prefix}_pomodoro_status")
    def pomodoro_status() -> str:
        """Check if there is an active (running) pomodoro session."""
        db = SessionLocal()
        try:
            active = db.query(PomodoroSession).filter(PomodoroSession.completed == False)\
                .order_by(PomodoroSession.started_at.desc()).first()
            if active:
                return f'{{"active":true,"session":{_session_to_json(active)}}}'
            return '{"active":false,"session":null}'
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_pomodoro_start")
    def pomodoro_start(session_type: str = "focus", duration_minutes: int = 25) -> str:
        """Start a new pomodoro session. Type: focus or break. Duration in minutes (default 25)."""
        db = SessionLocal()
        try:
            active = db.query(PomodoroSession).filter(PomodoroSession.completed == False).first()
            if active:
                return '{"error": "An active pomodoro session is already running. Stop it first."}'
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
                return '{"error": "No active pomodoro session"}'
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
            items = ",".join(_session_to_json(s) for s in sessions)
            return f'{{"items":[{items}],"total":{len(sessions)}}}'
        finally:
            db.close()