"""
Background image upload endpoint.
"""
import os
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from app.database import DATA_DIR
from app.routes.auth import require_auth

router = APIRouter(prefix="/api/background", tags=["background"])

BACKGROUND_DIR = os.path.join(DATA_DIR, "backgrounds")
os.makedirs(BACKGROUND_DIR, exist_ok=True)

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}


@router.post("/upload")
def upload_background(
    file: UploadFile = File(...),
    auth: str = Depends(require_auth),
):
    """Upload an image to use as background."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(
            status_code=400,
            detail=f"Ongeldig bestandstype: {ext}. Toegestaan: {', '.join(ALLOWED_EXT)}",
        )

    # Save as background.png for consistency
    dest = os.path.join(BACKGROUND_DIR, f"background{ext}")
    try:
        with open(dest, "wb") as f:
            shutil.copyfileobj(file.file, f)
    finally:
        file.file.close()

    # Remove old files with different extensions
    for old_ext in ALLOWED_EXT - {ext}:
        old_path = os.path.join(BACKGROUND_DIR, f"background{old_ext}")
        if os.path.isfile(old_path):
            os.remove(old_path)

    return {"success": True, "filename": f"background{ext}", "url": f"/api/background/image"}


@router.get("/image")
def get_background():
    """Serve the uploaded background image."""
    for ext in ALLOWED_EXT:
        path = os.path.join(BACKGROUND_DIR, f"background{ext}")
        if os.path.isfile(path):
            media_type = {
                ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".png": "image/png", ".webp": "image/webp",
                ".gif": "image/gif", ".bmp": "image/bmp",
            }.get(ext, "application/octet-stream")
            return FileResponse(path, media_type=media_type)

    raise HTTPException(status_code=404, detail="Geen achtergrondafbeelding geüpload")


@router.delete("")
def delete_background(
    auth: str = Depends(require_auth),
):
    """Remove the uploaded background image."""
    removed = False
    for ext in ALLOWED_EXT:
        path = os.path.join(BACKGROUND_DIR, f"background{ext}")
        if os.path.isfile(path):
            os.remove(path)
            removed = True
    if not removed:
        raise HTTPException(status_code=404, detail="Geen achtergrondafbeelding om te verwijderen")
    return {"success": True, "message": "Achtergrond verwijderd"}


@router.get("/status")
def background_status(
    auth: str = Depends(require_auth),
):
    """Check if a background image exists."""
    for ext in ALLOWED_EXT:
        path = os.path.join(BACKGROUND_DIR, f"background{ext}")
        if os.path.isfile(path):
            return {"has_image": True, "url": "/api/background/image"}
    return {"has_image": False}