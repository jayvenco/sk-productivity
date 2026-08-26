from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    color = Column(String(7), nullable=False, default="#4f8cff")  # hex kleur


class Tagging(Base):
    __tablename__ = "taggings"

    id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    tagable_type = Column(String(20), nullable=False)  # 'note', 'task', 'kanban', 'wiki', 'snippet'
    tagable_id = Column(Integer, nullable=False)

    tag = relationship("Tag")

    __table_args__ = (
        UniqueConstraint("tag_id", "tagable_type", "tagable_id", name="uq_tagging"),
    )