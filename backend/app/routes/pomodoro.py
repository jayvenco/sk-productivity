from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.pomodoro import PomodoroSession


# ---- Schemas ----
class PomodoroStart(BaseModel):
    session_type: str = "focus"
    duration_minutes: int = 25


class PomodoroResponse(BaseModel):
    id: int
    session_type: str
    duration_minutes: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    completed: bool

    model_config = {"from_attributes": True}


class PomodoroStatusResponse(BaseModel):
    active: bool
    session: Optional[PomodoroResponse] = None


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
    session = PomodoroSession(session_type=data.session_type, duration_minutes=data.duration_minutes)
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