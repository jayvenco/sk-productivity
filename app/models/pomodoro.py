from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Boolean, DateTime, String, Enum as SAEnum
import enum
from app.database import Base


class PomoStatus(str, enum.Enum):
    running = "running"
    paused = "paused"
    completed = "completed"


class PomodoroSession(Base):
    __tablename__ = "pomodoro"

    id = Column(Integer, primary_key=True, index=True)
    session_type = Column(String(10), nullable=False, default="focus")
    duration_minutes = Column(Integer, nullable=False, default=25)
    status = Column(SAEnum(PomoStatus), default=PomoStatus.running, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)  # legacy, kept for DB compat
    item_type = Column(String(20), nullable=True)
    item_id = Column(Integer, nullable=True)
    elapsed_seconds = Column(Integer, default=0, nullable=False)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime, nullable=True)