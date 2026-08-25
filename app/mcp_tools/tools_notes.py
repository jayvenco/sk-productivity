"""
MCP tools for the Notes module.
"""
import json
from app.database import SessionLocal
from app.mcp_tools._shared import _format_item, _format_list, _format_error, _format_deleted
from app.models.notes import Note


def _note_to_json(note):
    return _format_item({
        "id": note.id, "title": note.title, "content": note.content,
        "created_at": note.created_at, "updated_at": note.updated_at,
    })


def _notes_to_json(notes):
    return _format_list([json.loads(_note_to_json(n)) for n in notes])




def register_notes_tools(mcp, mcp_prefix="swissknife"):
    @mcp.tool(name=f"{mcp_prefix}_notes_list")
    def notes_list() -> str:
        """List all notes, ordered by most recent first."""
        db = SessionLocal()
        try:
            notes = db.query(Note).order_by(Note.created_at.desc()).all()
            return _notes_to_json(notes)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_notes_get")
    def notes_get(note_id: int) -> str:
        """Get a single note by its ID."""
        db = SessionLocal()
        try:
            note = db.query(Note).filter(Note.id == note_id).first()
            if not note:
                return _format_error("Note not found")
            return _note_to_json(note)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_notes_create")
    def notes_create(title: str, content: str = "") -> str:
        """Create a new note. Returns the created note."""
        db = SessionLocal()
        try:
            note = Note(title=title, content=content)
            db.add(note)
            db.commit()
            db.refresh(note)
            return _note_to_json(note)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_notes_edit")
    def notes_edit(note_id: int, title: str = None, content: str = None) -> str:
        """Edit an existing note. Only provided fields are updated."""
        db = SessionLocal()
        try:
            note = db.query(Note).filter(Note.id == note_id).first()
            if not note:
                return _format_error("Note not found")
            if title is not None:
                note.title = title
            if content is not None:
                note.content = content
            db.commit()
            db.refresh(note)
            return _note_to_json(note)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_notes_delete")
    def notes_delete(note_id: int) -> str:
        """Delete a note by its ID."""
        db = SessionLocal()
        try:
            note = db.query(Note).filter(Note.id == note_id).first()
            if not note:
                return _format_error("Note not found")
            db.delete(note)
            db.commit()
            return _format_deleted(note_id)
        finally:
            db.close()