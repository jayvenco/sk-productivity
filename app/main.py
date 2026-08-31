import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import init_db
from app.routes.notes import router as notes_router
from app.routes.tasks import router as tasks_router
from app.routes.kanban import router as kanban_router
from app.routes.pomodoro import router as pomodoro_router
from app.routes.wiki import router as wiki_router
from app.routes.snippets import router as snippets_router
from app.routes.tags import router as tags_router
from app.routes.auth import router as auth_router
from app.routes.backup import router as backup_router
from app.routes.stickies import router as stickies_router
from app.routes.calendar import router as calendar_router
from app.routes.reports import router as reports_router
from app.routes.background import router as background_router
from app.routes.projects import router as projects_router

app = FastAPI(title="swissknife-productivity", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routes ─────────────────────────────────────────────────────

app.include_router(notes_router)
app.include_router(tasks_router)
app.include_router(kanban_router)
app.include_router(pomodoro_router)
app.include_router(wiki_router)
app.include_router(snippets_router)
app.include_router(tags_router)
app.include_router(auth_router)
app.include_router(backup_router)
app.include_router(stickies_router)
app.include_router(calendar_router)
app.include_router(reports_router)
app.include_router(background_router)
app.include_router(projects_router)


# ── Startup ────────────────────────────────────────────────────────

@app.on_event("startup")
def on_startup():
    init_db()


# ── Health ─────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "app": "swissknife-productivity", "version": "0.1.0"}


@app.get("/api")
def api_root():
    return {
        "endpoints": {
            "notes": "/api/notes",
            "tasks": "/api/tasks",
            "kanban": "/api/kanban",
            "pomodoro": "/api/pomodoro",
            "wiki": "/api/wiki",
            "snippets": "/api/snippets",
        }
    }


# ── Static Frontend ────────────────────────────────────────────────

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if STATIC_DIR.is_dir() and any(STATIC_DIR.iterdir()):
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=4442, reload=not bool(os.environ.get("PRODUCTION")))