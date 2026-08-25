from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.notes import Note


# ---- Schemas ----
class NoteCreate(BaseModel):
    title: str
    content: str = ""


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NoteListResponse(BaseModel):
    items: List[NoteResponse]
    total: int


# ---- Routes ----
router = APIRouter(prefix="/api/notes", tags=["notes"])


@router.get("", response_model=NoteListResponse)
def list_notes(db: Session = Depends(get_db)):
    items = db.query(Note).order_by(Note.created_at.desc()).all()
    return NoteListResponse(
        items=[NoteResponse.model_validate(n) for n in items],
        total=len(items),
    )


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteResponse.model_validate(note)


@router.post("", response_model=NoteResponse, status_code=201)
def create_note(data: NoteCreate, db: Session = Depends(get_db)):
    note = Note(title=data.title, content=data.content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return NoteResponse.model_validate(note)


@router.put("/{note_id}", response_model=NoteResponse)
def update_note(note_id: int, data: NoteUpdate, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if data.title is not None:
        note.title = data.title
    if data.content is not None:
        note.content = data.content
    db.commit()
    db.refresh(note)
    return NoteResponse.model_validate(note)


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()