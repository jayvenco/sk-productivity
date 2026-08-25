from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SAEnum
import enum
from app.database import Base


class KanbanStatus(str, enum.Enum):
    todo = "todo"
    doing = "doing"
    done = "done"


class KanbanCard(Base):
    __tablename__ = "kanban"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False, default="")
    status = Column(SAEnum(KanbanStatus), default=KanbanStatus.todo, nullable=False)
    position = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))