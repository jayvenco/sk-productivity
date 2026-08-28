from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.kanban import KanbanCard, KanbanColumn, KanbanSwimlane, KanbanStatus


# ── Column Schemas ───────────────────────────────────────────────────

class KanbanColumnCreate(BaseModel):
    name: str
    position: int = 0
    color: str = "#6b7280"


class KanbanColumnUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[int] = None
    color: Optional[str] = None


class KanbanColumnResponse(BaseModel):
    id: int
    name: str
    position: int
    color: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Card Schemas ────────────────────────────────────────────────────

class KanbanCreate(BaseModel):
    title: str
    description: str = ""
    column_id: Optional[int] = None
    swimlane_id: Optional[int] = None
    position: int = 0
    due_date: Optional[datetime] = None


class KanbanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    column_id: Optional[int] = None
    swimlane_id: Optional[int] = None
    position: Optional[int] = None
    due_date: Optional[datetime] = None


class KanbanResponse(BaseModel):
    id: int
    title: str
    description: str
    column_id: Optional[int] = None
    swimlane_id: Optional[int] = None
    position: int
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KanbanListResponse(BaseModel):
    items: List[KanbanResponse]
    total: int


# ── Router ──────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/kanban", tags=["kanban"])


# ── Column Endpoints ────────────────────────────────────────────────

@router.get("/columns", response_model=List[KanbanColumnResponse])
def list_columns(db: Session = Depends(get_db)):
    """List all kanban columns, ordered by position."""
    return db.query(KanbanColumn).order_by(KanbanColumn.position).all()


@router.post("/columns", response_model=KanbanColumnResponse, status_code=201)
def create_column(data: KanbanColumnCreate, db: Session = Depends(get_db)):
    """Create a new kanban column."""
    col = KanbanColumn(name=data.name, position=data.position, color=data.color)
    db.add(col)
    db.commit()
    db.refresh(col)
    return col


@router.put("/columns/{column_id}", response_model=KanbanColumnResponse)
def update_column(column_id: int, data: KanbanColumnUpdate, db: Session = Depends(get_db)):
    """Update a kanban column."""
    col = db.query(KanbanColumn).filter(KanbanColumn.id == column_id).first()
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")
    if data.name is not None:
        col.name = data.name
    if data.position is not None:
        col.position = data.position
    if data.color is not None:
        col.color = data.color
    db.commit()
    db.refresh(col)
    return col


@router.delete("/columns/{column_id}", status_code=204)
def delete_column(column_id: int, db: Session = Depends(get_db)):
    """Delete a column. Cards in this column are moved to the first available column."""
    col = db.query(KanbanColumn).filter(KanbanColumn.id == column_id).first()
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")

    # Move cards to first remaining column, or unset column_id
    other = db.query(KanbanColumn).filter(KanbanColumn.id != column_id).order_by(KanbanColumn.position).first()
    if other:
        for card in col.cards:
            card.column_id = other.id

    db.delete(col)
    db.commit()


# ── Card Endpoints ──────────────────────────────────────────────────

# ── Swimlane Schemas ────────────────────────────────────────────────

class KanbanSwimlaneCreate(BaseModel):
    name: str
    position: int = 0
    color: str = "#444466"


class KanbanSwimlaneUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[int] = None
    color: Optional[str] = None


class KanbanSwimlaneResponse(BaseModel):
    id: int
    name: str
    position: int
    color: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Swimlane Endpoints ──────────────────────────────────────────────

@router.get("/swimlanes", response_model=List[KanbanSwimlaneResponse])
def list_swimlanes(db: Session = Depends(get_db)):
    return db.query(KanbanSwimlane).order_by(KanbanSwimlane.position).all()


@router.post("/swimlanes", response_model=KanbanSwimlaneResponse, status_code=201)
def create_swimlane(data: KanbanSwimlaneCreate, db: Session = Depends(get_db)):
    sw = KanbanSwimlane(name=data.name, position=data.position, color=data.color)
    db.add(sw)
    db.commit()
    db.refresh(sw)
    return sw


@router.put("/swimlanes/{swimlane_id}", response_model=KanbanSwimlaneResponse)
def update_swimlane(swimlane_id: int, data: KanbanSwimlaneUpdate, db: Session = Depends(get_db)):
    sw = db.query(KanbanSwimlane).filter(KanbanSwimlane.id == swimlane_id).first()
    if not sw:
        raise HTTPException(status_code=404, detail="Swimlane not found")
    if data.name is not None: sw.name = data.name
    if data.position is not None: sw.position = data.position
    if data.color is not None: sw.color = data.color
    db.commit()
    db.refresh(sw)
    return sw


@router.delete("/swimlanes/{swimlane_id}", status_code=204)
def delete_swimlane(swimlane_id: int, db: Session = Depends(get_db)):
    sw = db.query(KanbanSwimlane).filter(KanbanSwimlane.id == swimlane_id).first()
    if not sw:
        raise HTTPException(status_code=404, detail="Swimlane not found")
    for card in sw.cards:
        card.swimlane_id = None
    db.delete(sw)
    db.commit()

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
    """If no column_id given, assign to first column."""
    if data.column_id is None:
        first_col = db.query(KanbanColumn).order_by(KanbanColumn.position).first()
        if not first_col:
            raise HTTPException(status_code=400, detail="No columns exist. Create a column first.")
        col_id = first_col.id
    else:
        col_id = data.column_id

    card = KanbanCard(
        title=data.title, description=data.description,
        column_id=col_id, position=data.position, due_date=data.due_date,
        swimlane_id=data.swimlane_id,
    )
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
    if data.column_id is not None:
        card.column_id = data.column_id
    if data.position is not None:
        card.position = data.position
    if data.swimlane_id is not None:
        card.swimlane_id = data.swimlane_id
    if data.due_date is not None:
        card.due_date = data.due_date
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