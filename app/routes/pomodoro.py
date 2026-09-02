"""
Pomodoro API — multi-session support.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.pomodoro import PomodoroSession, PomoStatus

router = APIRouter(prefix="/api/pomodoro", tags=["pomodoro"])


# ---- Schemas ----
class PomodoroStart(BaseModel):
    session_type: str = "focus"
    duration_minutes: int = 25
    item_type: Optional[str] = None
    item_id: Optional[int] = None


class PomodoroResponse(BaseModel):
    id: int
    session_type: str
    duration_minutes: int
    status: PomoStatus
    elapsed_seconds: int = 0
    item_type: Optional[str] = None
    item_id: Optional[int] = None
    started_at: datetime
    ended_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PomoStatusResponse(BaseModel):
    sessions: List[PomodoroResponse]
    total: int


class PomoReportItem(BaseModel):
    item_type: str
    item_id: int
    total_sessions: int
    total_minutes: int
    last_session: Optional[datetime] = None


class PomoReportResponse(BaseModel):
    items: List[PomoReportItem]
    total: int


# ---- Routes ----
router = APIRouter(prefix="/api/pomodoro", tags=["pomodoro"])


@router.get("/status", response_model=PomoStatusResponse)
def get_pomo_status(db: Session = Depends(get_db)):
    """Get all active (running or paused) sessions."""
    sessions = (
        db.query(PomodoroSession)
        .filter(PomodoroSession.status.in_([PomoStatus.running, PomoStatus.paused]))
        .order_by(PomodoroSession.started_at.desc())
        .all()
    )
    return PomoStatusResponse(
        sessions=[PomodoroResponse.model_validate(s) for s in sessions],
        total=len(sessions),
    )


@router.get("/history", response_model=PomoStatusResponse)
def get_pomo_history(limit: int = 50, db: Session = Depends(get_db)):
    """Get recent completed sessions."""
    sessions = (
        db.query(PomodoroSession)
        .filter(PomodoroSession.status == PomoStatus.completed)
        .order_by(PomodoroSession.started_at.desc())
        .limit(limit)
        .all()
    )
    return PomoStatusResponse(
        sessions=[PomodoroResponse.model_validate(s) for s in sessions],
        total=len(sessions),
    )


@router.post("/start", response_model=PomodoroResponse, status_code=201)
def start_pomodoro(data: PomodoroStart, db: Session = Depends(get_db)):
    """Start a new pomodoro session. Multiple sessions can run simultaneously."""
    session = PomodoroSession(
        session_type=data.session_type,
        duration_minutes=data.duration_minutes,
        status=PomoStatus.running,
        item_type=data.item_type,
        item_id=data.item_id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return PomodoroResponse.model_validate(session)


@router.post("/pause/{session_id}", response_model=PomodoroResponse)
def pause_pomodoro(session_id: int, elapsed: int = Query(0), db: Session = Depends(get_db)):
    """Pause a running session."""
    session = db.query(PomodoroSession).filter(PomodoroSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != PomoStatus.running:
        raise HTTPException(status_code=400, detail="Session is not running")
    session.status = PomoStatus.paused
    session.elapsed_seconds = elapsed if elapsed > 0 else int((datetime.now(timezone.utc) - session.started_at).total_seconds())
    db.commit()
    db.refresh(session)
    return PomodoroResponse.model_validate(session)


@router.post("/resume/{session_id}", response_model=PomodoroResponse)
def resume_pomodoro(session_id: int, db: Session = Depends(get_db)):
    """Resume a paused session."""
    session = db.query(PomodoroSession).filter(PomodoroSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != PomoStatus.paused:
        raise HTTPException(status_code=400, detail="Session is not paused")
    # Reset started_at so the timer calculation works from resume time
    session.status = PomoStatus.running
    # Adjust started_at to account for elapsed time
    session.started_at = datetime.now(timezone.utc) - timedelta(seconds=session.elapsed_seconds)
    db.commit()
    db.refresh(session)
    return PomodoroResponse.model_validate(session)


@router.post("/stop/{session_id}", response_model=PomodoroResponse)
def stop_pomodoro(session_id: int, elapsed: int = Query(0), db: Session = Depends(get_db)):
    """Stop a session (mark as completed)."""
    session = db.query(PomodoroSession).filter(PomodoroSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status == PomoStatus.completed:
        raise HTTPException(status_code=400, detail="Session already completed")
    session.status = PomoStatus.completed
    session.ended_at = datetime.now(timezone.utc)
    session.elapsed_seconds = elapsed if elapsed > 0 else int((session.ended_at - session.started_at).total_seconds())
    db.commit()
    db.refresh(session)
    return PomodoroResponse.model_validate(session)


@router.delete("/{session_id}", status_code=204)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    """Delete a session."""
    session = db.query(PomodoroSession).filter(PomodoroSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()


@router.get("/report", response_model=PomoReportResponse)
def pomodoro_report(
    item_type: Optional[str] = Query(None),
    item_id: Optional[int] = Query(None),
    days: int = Query(30, description="Days to look back"),
    db: Session = Depends(get_db),
):
    """Get pomodoro time report."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    query = db.query(
        PomodoroSession.item_type,
        PomodoroSession.item_id,
        func.count(PomodoroSession.id).label("total_sessions"),
        func.sum(PomodoroSession.duration_minutes).label("total_minutes"),
        func.max(PomodoroSession.ended_at).label("last_session"),
    ).filter(
        PomodoroSession.status == PomoStatus.completed,
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
        PomoReportItem(
            item_type=r.item_type,
            item_id=r.item_id,
            total_sessions=r.total_sessions,
            total_minutes=r.total_minutes or 0,
            last_session=r.last_session,
        )
        for r in rows
    ]

    return PomoReportResponse(items=items, total=len(items))