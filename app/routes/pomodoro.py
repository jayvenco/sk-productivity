from datetime import datetime, timezone, timedelta
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.pomodoro import PomodoroSession


# ---- Schemas ----
class PomodoroStart(BaseModel):
    session_type: str = "focus"
    duration_minutes: int = 25
    item_type: Optional[str] = None  # 'task', 'note', 'kanban', 'wiki', 'snippet'
    item_id: Optional[int] = None


class PomodoroResponse(BaseModel):
    id: int
    session_type: str
    duration_minutes: int
    item_type: Optional[str] = None
    item_id: Optional[int] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    completed: bool

    model_config = {"from_attributes": True}


class PomodoroStatusResponse(BaseModel):
    active: bool
    session: Optional[PomodoroResponse] = None


class PomodoroReportItem(BaseModel):
    item_type: str
    item_id: int
    total_sessions: int
    total_minutes: int
    last_session: Optional[datetime] = None


class PomodoroReportResponse(BaseModel):
    items: List[PomodoroReportItem]
    total: int


# ---- Routes ----
router = APIRouter(prefix="/api/pomodoro", tags=["pomodoro"])


@router.get("/status", response_model=PomodoroStatusResponse)
def get_pomodoro_status(db: Session = Depends(get_db)):
    active = (
        db.query(PomodoroSession)
        .filter(PomodoroSession.completed == False)
        .order_by(PomodoroSession.started_at.desc())
        .first()
    )
    if active:
        return PomodoroStatusResponse(
            active=True,
            session=PomodoroResponse.model_validate(active),
        )
    return PomodoroStatusResponse(active=False, session=None)


@router.post("/start", response_model=PomodoroResponse, status_code=201)
def start_pomodoro(data: PomodoroStart, db: Session = Depends(get_db)):
    active = (
        db.query(PomodoroSession)
        .filter(PomodoroSession.completed == False)
        .first()
    )
    if active:
        raise HTTPException(status_code=400, detail="An active pomodoro session is already running. Stop it first.")
    session = PomodoroSession(
        session_type=data.session_type,
        duration_minutes=data.duration_minutes,
        item_type=data.item_type,
        item_id=data.item_id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return PomodoroResponse.model_validate(session)


@router.post("/stop", response_model=PomodoroResponse)
def stop_pomodoro(db: Session = Depends(get_db)):
    active = (
        db.query(PomodoroSession)
        .filter(PomodoroSession.completed == False)
        .order_by(PomodoroSession.started_at.desc())
        .first()
    )
    if not active:
        raise HTTPException(status_code=404, detail="No active pomodoro session")
    active.ended_at = datetime.now(timezone.utc)
    active.completed = True
    db.commit()
    db.refresh(active)
    return PomodoroResponse.model_validate(active)


@router.get("", response_model=List[PomodoroResponse])
def list_pomodoro_sessions(db: Session = Depends(get_db)):
    sessions = db.query(PomodoroSession).order_by(PomodoroSession.started_at.desc()).limit(50).all()
    return [PomodoroResponse.model_validate(s) for s in sessions]


@router.get("/report", response_model=PomodoroReportResponse)
def pomodoro_report(
    item_type: Optional[str] = Query(None),
    item_id: Optional[int] = Query(None),
    days: int = Query(30, description="Days to look back"),
    db: Session = Depends(get_db),
):
    """Get pomodoro time report. Optionally filter by item_type + item_id."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

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

    items = [
        PomodoroReportItem(
            item_type=r.item_type,
            item_id=r.item_id,
            total_sessions=r.total_sessions,
            total_minutes=r.total_minutes or 0,
            last_session=r.last_session,
        )
        for r in rows
    ]

    return PomodoroReportResponse(items=items, total=len(items))