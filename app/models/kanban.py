from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class KanbanStatus(str, enum.Enum):
    todo = "todo"
    doing = "doing"
    done = "done"


class KanbanColumn(Base):
    """A user-configurable column/step in the kanban board."""
    __tablename__ = "kanban_columns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    position = Column(Integer, default=0, nullable=False)
    color = Column(String(7), nullable=False, default="#666666")  # hex color
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    cards = relationship("KanbanCard", back_populates="column", cascade="all, delete-orphan")


class KanbanCard(Base):
    __tablename__ = "kanban"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False, default="")
    status = Column(SAEnum(KanbanStatus), default=KanbanStatus.todo, nullable=True)
    position = Column(Integer, default=0, nullable=False)
    column_id = Column(Integer, ForeignKey("kanban_columns.id"), nullable=True, index=True)
    swimlane_id = Column(Integer, ForeignKey("kanban_swimlanes.id"), nullable=True, index=True)
    project_id = Column(Integer, nullable=True, index=True)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    column = relationship("KanbanColumn", back_populates="cards")
    swimlane = relationship("KanbanSwimlane", back_populates="cards")


class KanbanSwimlane(Base):
    """A horizontal swimlane/row in the kanban board."""
    __tablename__ = "kanban_swimlanes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    position = Column(Integer, default=0, nullable=False)
    color = Column(String(7), nullable=False, default="#444466")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    cards = relationship("KanbanCard", back_populates="swimlane", cascade="all, delete-orphan")