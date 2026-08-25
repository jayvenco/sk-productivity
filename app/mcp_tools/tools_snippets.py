"""
MCP tools for the Snippets module.
"""
import json
from app.database import SessionLocal
from app.mcp_tools._shared import _format_item, _format_list, _format_error, _format_deleted
from app.models.snippets import Snippet


def _snippet_to_json(snippet):
    return _format_item({
        "id": snippet.id, "title": snippet.title, "language": snippet.language, "code": snippet.code,
        "created_at": snippet.created_at, "updated_at": snippet.updated_at,
    })


def _snippets_to_json(snippets):
    return _format_list([json.loads(_snippet_to_json(s)) for s in snippets])




def register_snippets_tools(mcp, mcp_prefix="swissknife"):
    @mcp.tool(name=f"{mcp_prefix}_snippets_list")
    def snippets_list() -> str:
        """List all code snippets, ordered by most recent first."""
        db = SessionLocal()
        try:
            snippets = db.query(Snippet).order_by(Snippet.created_at.desc()).all()
            return _snippets_to_json(snippets)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_snippets_get")
    def snippets_get(snippet_id: int) -> str:
        """Get a single snippet by its ID."""
        db = SessionLocal()
        try:
            snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
            if not snippet:
                return _format_error("Snippet not found")
            return _snippet_to_json(snippet)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_snippets_create")
    def snippets_create(title: str, language: str = "text", code: str = "") -> str:
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

    @mcp.tool(name=f"{mcp_prefix}_snippets_edit")
    def snippets_edit(snippet_id: int, title: str = None, language: str = None, code: str = None) -> str:
        """Edit an existing snippet. Only provided fields are updated."""
        db = SessionLocal()
        try:
            snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
            if not snippet:
                return _format_error("Snippet not found")
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

    @mcp.tool(name=f"{mcp_prefix}_snippets_delete")
    def snippets_delete(snippet_id: int) -> str:
        """Delete a snippet by its ID."""
        db = SessionLocal()
        try:
            snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
            if not snippet:
                return _format_error("Snippet not found")
            db.delete(snippet)
            db.commit()
            return _format_deleted(snippet_id)
        finally:
            db.close()