from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Project(Base):
    """A project/group for organizing tasks, notes, and other items."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(7), nullable=False, default="#E44332")
    position = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))