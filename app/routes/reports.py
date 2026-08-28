"""
Reports endpoint — aggregated stats, charts, and tables.
"""
from datetime import datetime, timezone, timedelta, date
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.routes.auth import require_auth
from app.models.notes import Note
from app.models.tasks import Task, TaskStatus
from app.models.kanban import KanbanCard, KanbanColumn, KanbanStatus
from app.models.wiki import WikiPage
from app.models.snippets import Snippet
from app.models.tags import Tag, Tagging

router = APIRouter(prefix="/api/reports", tags=["reports"])


# ── Schemas ─────────────────────────────────────────────────────────

class ModuleCount(BaseModel):
    module: str
    total: int
    completed: int
    completion_rate: float


class TagCount(BaseModel):
    tag_id: int
    tag_name: str
    tag_color: str
    total: int
    completed: int


class DailyCount(BaseModel):
    date: str
    created: int
    completed: int


class DashboardResponse(BaseModel):
    totals: List[ModuleCount]
    by_tag: List[TagCount]
    by_day: List[DailyCount]
    total_items: int
    total_completed: int
    avg_completion_rate: float


# ── Helpers ─────────────────────────────────────────────────────────

def _is_completed(module: str, item) -> bool:
    if module == "task":
        return item.status == TaskStatus.completed
    if module == "kanban":
        return item.status == KanbanStatus.done
    return False


def _completion_status(module: str) -> list:
    """Return the status values that mean 'completed' for a module."""
    if module == "task":
        return [TaskStatus.completed]
    if module == "kanban":
        return [KanbanStatus.done]
    return []


# ── Endpoints ───────────────────────────────────────────────────────

@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    days: int = Query(90, description="Lookback period in days"),
    auth: str = Depends(require_auth),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=days)

    totals = []
    total_items = 0
    total_completed = 0

    # ── Notes ──
    notes_all = db.query(Note).count()
    total_items += notes_all
    totals.append(ModuleCount(
        module="notes", total=notes_all, completed=0, completion_rate=0.0,
    ))

    # ── Tasks ──
    tasks_all = db.query(Task).count()
    tasks_done = db.query(Task).filter(Task.status == TaskStatus.completed).count()
    total_items += tasks_all
    total_completed += tasks_done
    totals.append(ModuleCount(
        module="tasks", total=tasks_all, completed=tasks_done,
        completion_rate=round(tasks_done / tasks_all * 100, 1) if tasks_all else 0,
    ))

    # ── Kanban ──
    kanban_all = db.query(KanbanCard).count()
    kanban_done = db.query(KanbanCard).filter(KanbanCard.status == KanbanStatus.done).count()
    total_items += kanban_all
    total_completed += kanban_done
    totals.append(ModuleCount(
        module="kanban", total=kanban_all, completed=kanban_done,
        completion_rate=round(kanban_done / kanban_all * 100, 1) if kanban_all else 0,
    ))

    # ── Wiki ──
    wiki_all = db.query(WikiPage).count()
    total_items += wiki_all
    totals.append(ModuleCount(
        module="wiki", total=wiki_all, completed=0, completion_rate=0.0,
    ))

    # ── Snippets ──
    snippets_all = db.query(Snippet).count()
    total_items += snippets_all
    totals.append(ModuleCount(
        module="snippets", total=snippets_all, completed=0, completion_rate=0.0,
    ))

    avg_rate = round(total_completed / total_items * 100, 1) if total_items else 0

    # ── Per Tag ──
    tags = db.query(Tag).all()
    by_tag = []
    for tag in tags:
        tag_tot = 0
        tag_done = 0
        taggings = db.query(Tagging).filter(Tagging.tag_id == tag.id).all()
        for tg in taggings:
            tag_tot += 1
            if tg.tagable_type == "task":
                item = db.query(Task).filter(Task.id == tg.tagable_id).first()
                if item and item.status == TaskStatus.completed:
                    tag_done += 1
            elif tg.tagable_type == "kanban":
                item = db.query(KanbanCard).filter(KanbanCard.id == tg.tagable_id).first()
                if item and item.status == KanbanStatus.done:
                    tag_done += 1
        if tag_tot > 0:
            by_tag.append(TagCount(
                tag_id=tag.id, tag_name=tag.name, tag_color=tag.color,
                total=tag_tot, completed=tag_done,
            ))

    # ── Daily activity (last N days) ──
    by_day = []
    for i in range(days - 1, -1, -1):
        d = (now - timedelta(days=i)).date()
        d_start = datetime.combine(d, datetime.min.time(), tzinfo=timezone.utc)
        d_end = datetime.combine(d, datetime.max.time(), tzinfo=timezone.utc)

        created = 0
        completed = 0

        created += db.query(Note).filter(Note.created_at.between(d_start, d_end)).count()
        created += db.query(Task).filter(Task.created_at.between(d_start, d_end)).count()
        created += db.query(KanbanCard).filter(KanbanCard.created_at.between(d_start, d_end)).count()
        created += db.query(WikiPage).filter(WikiPage.created_at.between(d_start, d_end)).count()
        created += db.query(Snippet).filter(Snippet.created_at.between(d_start, d_end)).count()

        completed += db.query(Task).filter(
            Task.status == TaskStatus.completed,
            Task.updated_at.between(d_start, d_end),
        ).count()
        completed += db.query(KanbanCard).filter(
            KanbanCard.status == KanbanStatus.done,
            KanbanCard.updated_at.between(d_start, d_end),
        ).count()

        if created > 0 or completed > 0:
            by_day.append(DailyCount(
                date=d.strftime("%Y-%m-%d"), created=created, completed=completed,
            ))

    return DashboardResponse(
        totals=totals, by_tag=by_tag, by_day=by_day,
        total_items=total_items, total_completed=total_completed,
        avg_completion_rate=avg_rate,
    )