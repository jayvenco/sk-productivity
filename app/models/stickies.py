from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base


class StickyNote(Base):
    """Floating sticky note on the grid."""
    __tablename__ = "stickies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, default="")
    content = Column(Text, nullable=False, default="")
    color = Column(String(7), nullable=False, default="#fef08a")  # hex color
    pos_x = Column(Integer, default=0, nullable=False)
    pos_y = Column(Integer, default=0, nullable=False)
    width = Column(Integer, default=220, nullable=False)
    height = Column(Integer, default=200, nullable=False)
    z_index = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))