from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.kanban import KanbanCard, KanbanStatus


# ---- Schemas ----
class KanbanCreate(BaseModel):
    title: str
    description: str = ""
    status: KanbanStatus = KanbanStatus.todo
    position: int = 0


class KanbanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[KanbanStatus] = None
    position: Optional[int] = None


class KanbanResponse(BaseModel):
    id: int
    title: str
    description: str
    status: KanbanStatus
    position: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KanbanListResponse(BaseModel):
    items: List[KanbanResponse]
    total: int


# ---- Routes ----
router = APIRouter(prefix="/api/kanban", tags=["kanban"])


@router.get("", response_model=KanbanListResponse)
def list_kanban(db: Session = Depends(get_db)):
    items = db.query(KanbanCard).order_by(KanbanCard.position).all()
    return KanbanListResponse(
        items=[KanbanResponse.model_validate(k) for k in items],
        total=len(items),
    )


@router.get("/{card_id}", response_model=KanbanResponse)
def get_kanban_card(card_id: int, db: Session = Depends(get_db)):
    card = db.query(KanbanCard).filter(KanbanCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Kanban card not found")
    return KanbanResponse.model_validate(card)


@router.post("", response_model=KanbanResponse, status_code=201)
def create_kanban_card(data: KanbanCreate, db: Session = Depends(get_db)):
    card = KanbanCard(title=data.title, description=data.description, status=data.status, position=data.position)
    db.add(card)
    db.commit()
    db.refresh(card)
    return KanbanResponse.model_validate(card)


@router.put("/{card_id}", response_model=KanbanResponse)
def update_kanban_card(card_id: int, data: KanbanUpdate, db: Session = Depends(get_db)):
    card = db.query(KanbanCard).filter(KanbanCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Kanban card not found")
    if data.title is not None:
        card.title = data.title
    if data.description is not None:
        card.description = data.description
    if data.status is not None:
        card.status = data.status
    if data.position is not None:
        card.position = data.position
    db.commit()
    db.refresh(card)
    return KanbanResponse.model_validate(card)


@router.delete("/{card_id}", status_code=204)
def delete_kanban_card(card_id: int, db: Session = Depends(get_db)):
    card = db.query(KanbanCard).filter(KanbanCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Kanban card not found")
    db.delete(card)
    db.commit()