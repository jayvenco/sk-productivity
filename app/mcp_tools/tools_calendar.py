"""
MCP tools for the Calendar module.
"""
import json
from datetime import datetime, timezone, date
from app.database import SessionLocal
from app.mcp_tools._shared import _format_list
from app.models.tasks import Task
from app.models.kanban import KanbanCard
from app.models.notes import Note
from sqlalchemy import func


def register_calendar_tools(mcp, mcp_prefix="swissknife"):
    @mcp.tool(name=f"{mcp_prefix}_calendar_deadlines")
    def calendar_deadlines(days: int = 60) -> str:
        """Get all items with deadlines within the next N days.
        Returns tasks, kanban cards, and notes with due dates."""
        db = SessionLocal()
        try:
            now = datetime.now(timezone.utc)
            end = now.replace(hour=23, minute=59, second=59)
            future = date.fromtimestamp(end.timestamp() + days * 86400)
            deadlines = []

            tasks = db.query(Task).filter(
                Task.due_date.isnot(None),
                func.date(Task.due_date) <= future,
            ).all()
            for t in tasks:
                deadlines.append({"id": t.id, "title": t.title, "item_type": "task",
                                  "due_date": t.due_date.strftime("%Y-%m-%d"), "status": t.status.value})

            cards = db.query(KanbanCard).filter(
                KanbanCard.due_date.isnot(None),
                func.date(KanbanCard.due_date) <= future,
            ).all()
            for c in cards:
                deadlines.append({"id": c.id, "title": c.title, "item_type": "kanban",
                                  "due_date": c.due_date.strftime("%Y-%m-%d"), "status": c.status.value if c.status else "todo"})

            notes = db.query(Note).filter(
                Note.due_date.isnot(None),
                func.date(Note.due_date) <= future,
            ).all()
            for n in notes:
                deadlines.append({"id": n.id, "title": n.title, "item_type": "note",
                                  "due_date": n.due_date.strftime("%Y-%m-%d"), "status": ""})

            return json.dumps({"deadlines": deadlines})
        finally:
            db.close()