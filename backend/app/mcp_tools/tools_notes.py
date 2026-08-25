"""
MCP tools for the Notes module.
"""
from app.database import SessionLocal
from app.models.notes import Note


def _note_to_json(note):
    return (
        f'{{"id":{note.id},"title":"{_escape(note.title)}","content":"{_escape(note.content)}",'
        f'"created_at":"{note.created_at.isoformat()}","updated_at":"{note.updated_at.isoformat()}"}}'
    )


def _notes_to_json(notes):
    items = ",".join(_note_to_json(n) for n in notes)
    return f'{{"items":[{items}],"total":{len(notes)}}}'


def _escape(s):
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")


def list_notes() -> str:
    """List all notes, ordered by most recent first."""
    db = SessionLocal()
    try:
        notes = db.query(Note).order_by(Note.created_at.desc()).all()
        return _notes_to_json(notes)
    finally:
        db.close()


def get_note(note_id: int) -> str:
    """Get a single note by its ID."""
    db = SessionLocal()
    try:
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            return '{"error": "Note not found"}'
        return _note_to_json(note)
    finally:
        db.close()


def create_note(title: str, content: str = "") -> str:
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


def edit_note(note_id: int, title: str = None, content: str = None) -> str:
    """Edit an existing note. Only provided fields are updated."""
    db = SessionLocal()
    try:
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            return '{"error": "Note not found"}'
        if title is not None:
            note.title = title
        if content is not None:
            note.content = content
        db.commit()
        db.refresh(note)
        return _note_to_json(note)
    finally:
        db.close()


def delete_note(note_id: int) -> str:
    """Delete a note by its ID."""
    db = SessionLocal()
    try:
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            return '{"error": "Note not found"}'
        db.delete(note)
        db.commit()
        return f'{{"deleted": true, "id": {note_id}}}'
    finally:
        db.close()


def register_notes_tools(server):
    server.add_tool(list_notes, name="mcp_swissknife_notes_list")
    server.add_tool(get_note, name="mcp_swissknife_notes_get")
    server.add_tool(create_note, name="mcp_swissknife_notes_create")
    server.add_tool(edit_note, name="mcp_swissknife_notes_edit")
    server.add_tool(delete_note, name="mcp_swissknife_notes_delete")