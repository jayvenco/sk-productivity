"""
MCP tools for the Snippets module.
"""
from app.database import SessionLocal
from app.models.snippets import Snippet


def _snippet_to_json(snippet):
    return (
        f'{{"id":{snippet.id},"title":"{_escape(snippet.title)}","language":"{_escape(snippet.language)}",'
        f'"code":"{_escape(snippet.code)}",'
        f'"created_at":"{snippet.created_at.isoformat()}","updated_at":"{snippet.updated_at.isoformat()}"}}'
    )


def _snippets_to_json(snippets):
    items = ",".join(_snippet_to_json(s) for s in snippets)
    return f'{{"items":[{items}],"total":{len(snippets)}}}'


def _escape(s):
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")


def list_snippets() -> str:
    """List all code snippets, ordered by most recent first."""
    db = SessionLocal()
    try:
        snippets = db.query(Snippet).order_by(Snippet.created_at.desc()).all()
        return _snippets_to_json(snippets)
    finally:
        db.close()


def get_snippet(snippet_id: int) -> str:
    """Get a single snippet by its ID."""
    db = SessionLocal()
    try:
        snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
        if not snippet:
            return '{"error": "Snippet not found"}'
        return _snippet_to_json(snippet)
    finally:
        db.close()


def create_snippet(title: str, language: str = "text", code: str = "") -> str:
    """Create a new code snippet."""
    db = SessionLocal()
    try:
        snippet = Snippet(title=title, language=language, code=code)
        db.add(snippet)
        db.commit()
        db.refresh(snippet)
        return _snippet_to_json(snippet)
    finally:
        db.close()


def edit_snippet(snippet_id: int, title: str = None, language: str = None, code: str = None) -> str:
    """Edit an existing snippet. Only provided fields are updated."""
    db = SessionLocal()
    try:
        snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
        if not snippet:
            return '{"error": "Snippet not found"}'
        if title is not None:
            snippet.title = title
        if language is not None:
            snippet.language = language
        if code is not None:
            snippet.code = code
        db.commit()
        db.refresh(snippet)
        return _snippet_to_json(snippet)
    finally:
        db.close()


def delete_snippet(snippet_id: int) -> str:
    """Delete a snippet by its ID."""
    db = SessionLocal()
    try:
        snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
        if not snippet:
            return '{"error": "Snippet not found"}'
        db.delete(snippet)
        db.commit()
        return f'{{"deleted": true, "id": {snippet_id}}}'
    finally:
        db.close()


def register_snippets_tools(server):
    server.add_tool(list_snippets, name="mcp_swissknife_snippets_list")
    server.add_tool(get_snippet, name="mcp_swissknife_snippets_get")
    server.add_tool(create_snippet, name="mcp_swissknife_snippets_create")
    server.add_tool(edit_snippet, name="mcp_swissknife_snippets_edit")
    server.add_tool(delete_snippet, name="mcp_swissknife_snippets_delete")