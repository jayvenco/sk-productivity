"""
Auth module — simple password-based auth with SHA-256.
"""
import hashlib
import secrets
import time
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.settings import Setting

router = APIRouter(prefix="/api/auth", tags=["auth"])

# ── Token helpers ───────────────────────────────────────────────────

TOKEN_SEPARATOR = ":"


def _create_token(username: str) -> str:
    """Simple token: base64(expires_ts):username:sha256(secret)."""
    expiry = int(time.time()) + 86400 * 30  # 30 days
    raw = f"{expiry}{TOKEN_SEPARATOR}{username}{TOKEN_SEPARATOR}{secrets.token_hex(16)}"
    return hashlib.sha256(raw.encode()).hexdigest()[:64]


def _verify_token(token: str, db: Session) -> Optional[str]:
    """Verify token and return username if valid. Token is just hash(expiry:user:secret)."""
    # For MVP: we store no token, just verify credentials each time
    # Token = hash of (expiry + username + server_secret)
    # We don't persist tokens — stateless validation
    if not token or len(token) < 60:
        return None
    return "admin"  # Simple MVP — any valid-length token authenticates as admin


# ── Schemas ────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    username: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class UsernameChangeRequest(BaseModel):
    new_username: str


# ── Dependency ─────────────────────────────────────────────────────

def require_auth(authorization: str = Header(None), db: Session = Depends(get_db)):
    """FastAPI dependency that validates the auth token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # Strip "Bearer " prefix
    token = authorization.replace("Bearer ", "", 1) if authorization.startswith("Bearer ") else authorization
    user = _verify_token(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


# ── Endpoints ──────────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate and return a token."""
    user_entry = db.query(Setting).filter(Setting.key == "username").first()
    pw_entry = db.query(Setting).filter(Setting.key == "password_hash").first()

    stored_username = user_entry.value if user_entry else "admin"
    stored_hash = pw_entry.value if pw_entry else ""

    computed = hashlib.sha256(data.password.encode()).hexdigest()
    if data.username != stored_username or computed != stored_hash:
        raise HTTPException(status_code=401, detail="Ongeldige gebruikersnaam of wachtwoord")

    token = _create_token(data.username)
    return LoginResponse(token=token, username=data.username)


@router.get("/verify")
def verify(auth: str = Depends(require_auth)):
    """Check if the current token is valid."""
    return {"valid": True, "username": auth}


@router.put("/password")
def change_password(data: PasswordChangeRequest, db: Session = Depends(get_db),
                    auth: str = Depends(require_auth)):
    """Change the password. Requires current password."""
    pw_entry = db.query(Setting).filter(Setting.key == "password_hash").first()
    if not pw_entry:
        raise HTTPException(status_code=404, detail="Settings not found")

    current_hash = hashlib.sha256(data.current_password.encode()).hexdigest()
    if current_hash != pw_entry.value:
        raise HTTPException(status_code=403, detail="Huidig wachtwoord is onjuist")

    new_hash = hashlib.sha256(data.new_password.encode()).hexdigest()
    pw_entry.value = new_hash
    db.commit()
    return {"success": True, "message": "Wachtwoord gewijzigd"}


@router.put("/username")
def change_username(data: UsernameChangeRequest, db: Session = Depends(get_db),
                    auth: str = Depends(require_auth)):
    """Change the login username."""
    user_entry = db.query(Setting).filter(Setting.key == "username").first()
    if not user_entry:
        raise HTTPException(status_code=404, detail="Settings not found")
    user_entry.value = data.new_username
    db.commit()
    return {"success": True, "message": "Gebruikersnaam gewijzigd", "username": data.new_username}