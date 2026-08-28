"""
Calendar endpoint — returns all items with deadlines grouped by date.
"""
from datetime import datetime, timezone, date
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.routes.auth import require_auth
from app.models.tasks import Task, TaskStatus
from app.models.kanban import KanbanCard, KanbanStatus

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


class DeadlineItem(BaseModel):
    id: int
    title: str
    item_type: str  # "task" or "kanban"
    due_date: str
    status: str


class CalendarResponse(BaseModel):
    deadlines: List[DeadlineItem]


@router.get("/deadlines", response_model=CalendarResponse)
def get_deadlines(days: int = 60, auth: str = Depends(require_auth), db: Session = Depends(get_db)):
    """Get all items with deadlines within the next N days."""
    now = datetime.now(timezone.utc)
    end = now.replace(hour=23, minute=59, second=59)
    future = date.fromtimestamp(end.timestamp() + days * 86400)

    deadlines = []

    # Tasks with due_date
    tasks = db.query(Task).filter(
        Task.due_date.isnot(None),
        func.date(Task.due_date) <= future,
    ).all()
    for t in tasks:
        deadlines.append(DeadlineItem(
            id=t.id, title=t.title,
            item_type="task", due_date=t.due_date.strftime("%Y-%m-%d"),
            status=t.status.value,
        ))

    # Kanban cards with due_date
    cards = db.query(KanbanCard).filter(
        KanbanCard.due_date.isnot(None),
        func.date(KanbanCard.due_date) <= future,
    ).all()
    for c in cards:
        deadlines.append(DeadlineItem(
            id=c.id, title=c.title,
            item_type="kanban", due_date=c.due_date.strftime("%Y-%m-%d"),
            status=c.status.value if c.status else "todo",
        ))

    return CalendarResponse(deadlines=deadlines)