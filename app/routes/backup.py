"""
Backup module — create and restore SQLite database backups.
"""
import os
import shutil
from datetime import datetime, timezone
from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from app.database import DATA_DIR, SessionLocal
from app.routes.auth import require_auth

router = APIRouter(prefix="/api/backup", tags=["backup"])

BACKUP_DIR = os.path.join(DATA_DIR, "backups")
DB_PATH = os.path.join(DATA_DIR, "swissknife.db")


class BackupInfo(BaseModel):
    filename: str
    size_bytes: int
    created_at: str


class BackupCreateResponse(BaseModel):
    filename: str
    size_bytes: int
    created_at: str


def _ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


@router.post("", response_model=BackupCreateResponse)
def create_backup(auth: str = Depends(require_auth)):
    """Create a timestamped backup of the SQLite database."""
    _ensure_backup_dir()

    if not os.path.isfile(DB_PATH):
        raise HTTPException(status_code=404, detail="Database not found")

    # Flush writes to DB first
    db = SessionLocal()
    db.close()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"swissknife_{timestamp}.db"
    dest = os.path.join(BACKUP_DIR, filename)

    try:
        shutil.copy2(DB_PATH, dest)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {e}")

    size = os.path.getsize(dest)
    return BackupCreateResponse(
        filename=filename,
        size_bytes=size,
        created_at=timestamp,
    )


@router.get("", response_model=List[BackupInfo])
def list_backups(auth: str = Depends(require_auth)):
    """List all available backups, sorted newest first."""
    _ensure_backup_dir()

    backups = []
    for fname in os.listdir(BACKUP_DIR):
        if not fname.endswith(".db"):
            continue
        fpath = os.path.join(BACKUP_DIR, fname)
        if not os.path.isfile(fpath):
            continue
        mtime = os.path.getmtime(fpath)
        created = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        backups.append(BackupInfo(
            filename=fname,
            size_bytes=os.path.getsize(fpath),
            created_at=created,
        ))

    backups.sort(key=lambda b: b.created_at, reverse=True)
    return backups


@router.post("/restore/{filename}")
def restore_backup(filename: str, auth: str = Depends(require_auth)):
    """Restore a backup by filename."""
    _ensure_backup_dir()

    # Security: prevent path traversal
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    src = os.path.join(BACKUP_DIR, filename)
    if not os.path.isfile(src):
        raise HTTPException(status_code=404, detail="Backup not found")

    try:
        shutil.copy2(src, DB_PATH)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {e}")

    return {"success": True, "message": f"Backup '{filename}' restored. Restart the server to apply changes."}


@router.delete("/{filename}")
def delete_backup(filename: str, auth: str = Depends(require_auth)):
    """Delete a backup by filename."""
    _ensure_backup_dir()

    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    fpath = os.path.join(BACKUP_DIR, filename)
    if not os.path.isfile(fpath):
        raise HTTPException(status_code=404, detail="Backup not found")

    os.remove(fpath)
    return {"success": True, "message": f"Backup '{filename}' verwijderd"}