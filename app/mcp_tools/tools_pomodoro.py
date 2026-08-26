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
        "item_type": s.item_type, "item_id": s.item_id,
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
    def pomodoro_start(session_type: str = "focus", duration_minutes: int = 25,
                        item_type: str = None, item_id: int = None) -> str:
        """Start a new pomodoro session. Type: focus or break. Duration in minutes (default 25).
        Optionally link to an item: item_type='task'/'note'/'kanban', item_id=<id>."""
        db = SessionLocal()
        try:
            active = db.query(PomodoroSession).filter(PomodoroSession.completed == False).first()
            if active:
                return _format_error("An active pomodoro session is already running. Stop it first.")
            session = PomodoroSession(
                session_type=session_type, duration_minutes=duration_minutes,
                item_type=item_type, item_id=item_id,
            )
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

    @mcp.tool(name=f"{mcp_prefix}_pomodoro_report")
    def pomodoro_report(days: int = 30, item_type: str = None, item_id: int = None) -> str:
        """Get pomodoro time report. Filter by item_type ('task'/'note'/'kanban') and item_id optional.
        Returns total sessions and minutes per item."""
        from sqlalchemy import func
        db = SessionLocal()
        try:
            since = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            from datetime import timedelta
            since -= timedelta(days=days)

            query = db.query(
                PomodoroSession.item_type,
                PomodoroSession.item_id,
                func.count(PomodoroSession.id).label("total_sessions"),
                func.sum(PomodoroSession.duration_minutes).label("total_minutes"),
                func.max(PomodoroSession.ended_at).label("last_session"),
            ).filter(
                PomodoroSession.completed == True,
                PomodoroSession.ended_at >= since,
                PomodoroSession.item_type.isnot(None),
                PomodoroSession.item_id.isnot(None),
            )

            if item_type:
                query = query.filter(PomodoroSession.item_type == item_type)
            if item_id is not None:
                query = query.filter(PomodoroSession.item_id == item_id)

            rows = query.group_by(PomodoroSession.item_type, PomodoroSession.item_id).all()

            items = []
            for r in rows:
                items.append({
                    "item_type": r.item_type,
                    "item_id": r.item_id,
                    "total_sessions": r.total_sessions,
                    "total_minutes": r.total_minutes or 0,
                    "last_session": r.last_session.isoformat() if r.last_session else None,
                })

            return json.dumps({"items": items, "total": len(items)})
        finally:
            db.close()