from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routes.notes import router as notes_router
from app.routes.tasks import router as tasks_router
from app.routes.kanban import router as kanban_router
from app.routes.pomodoro import router as pomodoro_router
from app.routes.wiki import router as wiki_router
from app.routes.snippets import router as snippets_router

app = FastAPI(title="swissknife-productivity", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notes_router)
app.include_router(tasks_router)
app.include_router(kanban_router)
app.include_router(pomodoro_router)
app.include_router(wiki_router)
app.include_router(snippets_router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=4442, reload=True)