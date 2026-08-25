from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Boolean, DateTime, String
from app.database import Base


class PomodoroSession(Base):
    __tablename__ = "pomodoro"

    id = Column(Integer, primary_key=True, index=True)
    session_type = Column(String(10), nullable=False, default="focus")  # focus / break
    duration_minutes = Column(Integer, nullable=False, default=25)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)