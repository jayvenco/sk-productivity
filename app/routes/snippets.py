from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.snippets import Snippet


# ---- Schemas ----
class SnippetCreate(BaseModel):
    title: str
    language: str = "text"
    code: str = ""


class SnippetUpdate(BaseModel):
    title: Optional[str] = None
    language: Optional[str] = None
    code: Optional[str] = None


class SnippetResponse(BaseModel):
    id: int
    title: str
    language: str
    code: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SnippetListResponse(BaseModel):
    items: List[SnippetResponse]
    total: int


# ---- Routes ----
router = APIRouter(prefix="/api/snippets", tags=["snippets"])


@router.get("", response_model=SnippetListResponse)
def list_snippets(db: Session = Depends(get_db)):
    items = db.query(Snippet).order_by(Snippet.created_at.desc()).all()
    return SnippetListResponse(
        items=[SnippetResponse.model_validate(s) for s in items],
        total=len(items),
    )


@router.get("/{snippet_id}", response_model=SnippetResponse)
def get_snippet(snippet_id: int, db: Session = Depends(get_db)):
    snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return SnippetResponse.model_validate(snippet)


@router.post("", response_model=SnippetResponse, status_code=201)
def create_snippet(data: SnippetCreate, db: Session = Depends(get_db)):
    snippet = Snippet(title=data.title, language=data.language, code=data.code)
    db.add(snippet)
    db.commit()
    db.refresh(snippet)
    return SnippetResponse.model_validate(snippet)


@router.put("/{snippet_id}", response_model=SnippetResponse)
def update_snippet(snippet_id: int, data: SnippetUpdate, db: Session = Depends(get_db)):
    snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    if data.title is not None:
        snippet.title = data.title
    if data.language is not None:
        snippet.language = data.language
    if data.code is not None:
        snippet.code = data.code
    db.commit()
    db.refresh(snippet)
    return SnippetResponse.model_validate(snippet)


@router.delete("/{snippet_id}", status_code=204)
def delete_snippet(snippet_id: int, db: Session = Depends(get_db)):
    snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    db.delete(snippet)
    db.commit()