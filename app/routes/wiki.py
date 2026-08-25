from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.wiki import WikiPage


# ---- Schemas ----
class WikiCreate(BaseModel):
    title: str
    slug: str
    content: str = ""


class WikiUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None


class WikiResponse(BaseModel):
    id: int
    title: str
    slug: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WikiListResponse(BaseModel):
    items: List[WikiResponse]
    total: int


# ---- Routes ----
router = APIRouter(prefix="/api/wiki", tags=["wiki"])


@router.get("", response_model=WikiListResponse)
def list_wiki_pages(q: str = Query(None, description="Search query"), db: Session = Depends(get_db)):
    query = db.query(WikiPage)
    if q:
        like = f"%{q}%"
        query = query.filter(WikiPage.title.ilike(like) | WikiPage.content.ilike(like))
    items = query.order_by(WikiPage.created_at.desc()).all()
    return WikiListResponse(
        items=[WikiResponse.model_validate(p) for p in items],
        total=len(items),
    )


@router.get("/by-slug/{slug}", response_model=WikiResponse)
def get_wiki_page_by_slug(slug: str, db: Session = Depends(get_db)):
    page = db.query(WikiPage).filter(WikiPage.slug == slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Wiki page not found")
    return WikiResponse.model_validate(page)


@router.get("/{page_id}", response_model=WikiResponse)
def get_wiki_page(page_id: int, db: Session = Depends(get_db)):
    page = db.query(WikiPage).filter(WikiPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Wiki page not found")
    return WikiResponse.model_validate(page)


@router.post("", response_model=WikiResponse, status_code=201)
def create_wiki_page(data: WikiCreate, db: Session = Depends(get_db)):
    existing = db.query(WikiPage).filter(WikiPage.slug == data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="A page with this slug already exists")
    page = WikiPage(title=data.title, slug=data.slug, content=data.content)
    db.add(page)
    db.commit()
    db.refresh(page)
    return WikiResponse.model_validate(page)


@router.put("/{page_id}", response_model=WikiResponse)
def update_wiki_page(page_id: int, data: WikiUpdate, db: Session = Depends(get_db)):
    page = db.query(WikiPage).filter(WikiPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Wiki page not found")
    if data.title is not None:
        page.title = data.title
    if data.slug is not None:
        existing = db.query(WikiPage).filter(WikiPage.slug == data.slug, WikiPage.id != page_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="A page with this slug already exists")
        page.slug = data.slug
    if data.content is not None:
        page.content = data.content
    db.commit()
    db.refresh(page)
    return WikiResponse.model_validate(page)


@router.delete("/{page_id}", status_code=204)
def delete_wiki_page(page_id: int, db: Session = Depends(get_db)):
    page = db.query(WikiPage).filter(WikiPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Wiki page not found")
    db.delete(page)
    db.commit()