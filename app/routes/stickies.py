from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.stickies import StickyNote


# ── Schemas ────────────────────────────────────────────────────────

class StickyCreate(BaseModel):
    title: str = ""
    content: str = ""
    color: str = "#fef08a"
    pos_x: int = 0
    pos_y: int = 0
    width: int = 220
    height: int = 200


class StickyUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    color: Optional[str] = None
    pos_x: Optional[int] = None
    pos_y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    z_index: Optional[int] = None


class StickyResponse(BaseModel):
    id: int
    title: str
    content: str
    color: str
    pos_x: int
    pos_y: int
    width: int
    height: int
    z_index: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StickyListResponse(BaseModel):
    items: List[StickyResponse]
    total: int


class BulkDeleteRequest(BaseModel):
    ids: List[int]


# ── Router ─────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/stickies", tags=["stickies"])


@router.get("", response_model=StickyListResponse)
def list_stickies(db: Session = Depends(get_db)):
    items = db.query(StickyNote).order_by(StickyNote.z_index).all()
    return StickyListResponse(
        items=[StickyResponse.model_validate(s) for s in items],
        total=len(items),
    )


@router.get("/{sticky_id}", response_model=StickyResponse)
def get_sticky(sticky_id: int, db: Session = Depends(get_db)):
    s = db.query(StickyNote).filter(StickyNote.id == sticky_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Sticky note not found")
    return StickyResponse.model_validate(s)


@router.post("", response_model=StickyResponse, status_code=201)
def create_sticky(data: StickyCreate, db: Session = Depends(get_db)):
    # Auto-position: place at a slight offset so new notes don't stack
    count = db.query(StickyNote).count()
    offset = (count % 10) * 30
    sticky = StickyNote(
        title=data.title, content=data.content, color=data.color,
        pos_x=data.pos_x + offset, pos_y=data.pos_y + offset,
        width=data.width, height=data.height,
        z_index=count,
    )
    db.add(sticky)
    db.commit()
    db.refresh(sticky)
    return StickyResponse.model_validate(sticky)


@router.put("/{sticky_id}", response_model=StickyResponse)
def update_sticky(sticky_id: int, data: StickyUpdate, db: Session = Depends(get_db)):
    s = db.query(StickyNote).filter(StickyNote.id == sticky_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Sticky note not found")
    if data.title is not None:
        s.title = data.title
    if data.content is not None:
        s.content = data.content
    if data.color is not None:
        s.color = data.color
    if data.pos_x is not None:
        s.pos_x = data.pos_x
    if data.pos_y is not None:
        s.pos_y = data.pos_y
    if data.width is not None:
        s.width = data.width
    if data.height is not None:
        s.height = data.height
    if data.z_index is not None:
        s.z_index = data.z_index
    db.commit()
    db.refresh(s)
    return StickyResponse.model_validate(s)


@router.delete("/{sticky_id}", status_code=204)
def delete_sticky(sticky_id: int, db: Session = Depends(get_db)):
    s = db.query(StickyNote).filter(StickyNote.id == sticky_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Sticky note not found")
    db.delete(s)
    db.commit()


@router.post("/bulk-delete", status_code=204)
def bulk_delete_stickies(data: BulkDeleteRequest, db: Session = Depends(get_db)):
    """Delete multiple sticky notes at once."""
    if not data.ids:
        raise HTTPException(status_code=400, detail="No IDs provided")
    db.query(StickyNote).filter(StickyNote.id.in_(data.ids)).delete(synchronize_session=False)
    db.commit()