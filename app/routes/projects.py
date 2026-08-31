"""
Project API — Todoist-style project/group management.
"""
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.project import Project
from app.routes.auth import require_auth

router = APIRouter(prefix="/api/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    name: str
    color: str = "#E44332"
    position: int = 0


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    position: Optional[int] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    color: str
    position: int
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    auth: str = Depends(require_auth),
    db: Session = Depends(get_db),
):
    return db.query(Project).order_by(Project.position).all()


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(
    data: ProjectCreate,
    auth: str = Depends(require_auth),
    db: Session = Depends(get_db),
):
    proj = Project(name=data.name, color=data.color, position=data.position)
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return proj


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    auth: str = Depends(require_auth),
    db: Session = Depends(get_db),
):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    if data.name is not None: proj.name = data.name
    if data.color is not None: proj.color = data.color
    if data.position is not None: proj.position = data.position
    db.commit()
    db.refresh(proj)
    return proj


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    auth: str = Depends(require_auth),
    db: Session = Depends(get_db),
):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(proj)
    db.commit()