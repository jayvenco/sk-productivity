from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base


class Snippet(Base):
    __tablename__ = "snippets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    language = Column(String(50), nullable=False, default="text")
    code = Column(Text, nullable=False, default="")
    project_id = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))