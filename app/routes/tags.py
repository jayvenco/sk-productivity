from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.tags import Tag, Tagging


# ---- Schemas ----
class TagCreate(BaseModel):
    name: str
    color: str = "#4f8cff"


class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class TagResponse(BaseModel):
    id: int
    name: str
    color: str

    model_config = {"from_attributes": True}


class TagListResponse(BaseModel):
    items: List[TagResponse]
    total: int


# ---- Routes ----
router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=TagListResponse)
def list_tags(db: Session = Depends(get_db)):
    items = db.query(Tag).order_by(Tag.name).all()
    return TagListResponse(
        items=[TagResponse.model_validate(t) for t in items],
        total=len(items),
    )


@router.post("", response_model=TagResponse, status_code=201)
def create_tag(data: TagCreate, db: Session = Depends(get_db)):
    existing = db.query(Tag).filter(Tag.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already exists")
    tag = Tag(name=data.name, color=data.color)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return TagResponse.model_validate(tag)


@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(tag_id: int, data: TagUpdate, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if data.name is not None:
        tag.name = data.name
    if data.color is not None:
        tag.color = data.color
    db.commit()
    db.refresh(tag)
    return TagResponse.model_validate(tag)


@router.delete("/{tag_id}", status_code=204)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.commit()


# ---- Tagging endpoints (attach/detach tags to items) ----

@router.get("/attached", response_model=List[TagResponse])
def get_tags_for_item(item_type: str, item_id: int, db: Session = Depends(get_db)):
    """Get all tags attached to an item."""
    taggings = db.query(Tagging).filter(
        Tagging.tagable_type == item_type,
        Tagging.tagable_id == item_id,
    ).all()
    tag_ids = [t.tag_id for t in taggings]
    tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all() if tag_ids else []
    return [TagResponse.model_validate(t) for t in tags]


@router.post("/attach", status_code=201)
def attach_tag(tag_id: int, item_type: str, item_id: int, db: Session = Depends(get_db)):
    """Attach a tag to an item."""
    existing = db.query(Tagging).filter(
        Tagging.tag_id == tag_id,
        Tagging.tagable_type == item_type,
        Tagging.tagable_id == item_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already attached")
    tagging = Tagging(tag_id=tag_id, tagable_type=item_type, tagable_id=item_id)
    db.add(tagging)
    db.commit()
    return {"attached": True, "tag_id": tag_id}


@router.delete("/detach", status_code=204)
def detach_tag(tag_id: int, item_type: str, item_id: int, db: Session = Depends(get_db)):
    """Detach a tag from an item."""
    tagging = db.query(Tagging).filter(
        Tagging.tag_id == tag_id,
        Tagging.tagable_type == item_type,
        Tagging.tagable_id == item_id,
    ).first()
    if not tagging:
        raise HTTPException(status_code=404, detail="Tag not attached")
    db.delete(tagging)
    db.commit()