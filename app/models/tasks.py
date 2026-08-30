from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SAEnum
import enum
from app.database import Base


class TaskStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False, default="")
    status = Column(SAEnum(TaskStatus), default=TaskStatus.pending, nullable=False)
    color = Column(String(7), nullable=False, default="#262a36")
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))