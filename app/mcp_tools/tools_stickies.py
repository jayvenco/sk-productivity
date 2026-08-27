"""
MCP tools for the Sticky Notes module.
"""
import json
from app.database import SessionLocal
from app.mcp_tools._shared import _format_item, _format_list, _format_error, _format_deleted
from app.models.stickies import StickyNote


def _sticky_to_json(s):
    return _format_item({
        "id": s.id, "title": s.title, "content": s.content,
        "color": s.color, "pos_x": s.pos_x, "pos_y": s.pos_y,
        "width": s.width, "height": s.height, "z_index": s.z_index,
        "created_at": s.created_at, "updated_at": s.updated_at,
    })


def _stickies_to_json(items):
    return _format_list([json.loads(_sticky_to_json(s)) for s in items])


def register_stickies_tools(mcp, mcp_prefix="swissknife"):
    @mcp.tool(name=f"{mcp_prefix}_stickies_list")
    def stickies_list() -> str:
        """List all sticky notes, ordered by z-index."""
        db = SessionLocal()
        try:
            items = db.query(StickyNote).order_by(StickyNote.z_index).all()
            return _stickies_to_json(items)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_stickies_get")
    def stickies_get(sticky_id: int) -> str:
        """Get a single sticky note by ID."""
        db = SessionLocal()
        try:
            s = db.query(StickyNote).filter(StickyNote.id == sticky_id).first()
            if not s:
                return _format_error("Sticky note not found")
            return _sticky_to_json(s)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_stickies_create")
    def stickies_create(title: str = "", content: str = "", color: str = "#fef08a") -> str:
        """Create a new sticky note. Color: hex like #fef08a (yellow), #fca5a5 (red), #86efac (green), #93c5fd (blue)."""
        db = SessionLocal()
        try:
            count = db.query(StickyNote).count()
            s = StickyNote(title=title, content=content, color=color,
                           pos_x=(count % 10) * 30, pos_y=(count % 10) * 30,
                           z_index=count)
            db.add(s)
            db.commit()
            db.refresh(s)
            return _sticky_to_json(s)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_stickies_edit")
    def stickies_edit(sticky_id: int, title: str = None, content: str = None,
                      color: str = None, pos_x: int = None, pos_y: int = None) -> str:
        """Edit a sticky note. Only provided fields are updated."""
        db = SessionLocal()
        try:
            s = db.query(StickyNote).filter(StickyNote.id == sticky_id).first()
            if not s:
                return _format_error("Sticky note not found")
            if title is not None: s.title = title
            if content is not None: s.content = content
            if color is not None: s.color = color
            if pos_x is not None: s.pos_x = pos_x
            if pos_y is not None: s.pos_y = pos_y
            db.commit()
            db.refresh(s)
            return _sticky_to_json(s)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_stickies_delete")
    def stickies_delete(sticky_id: int) -> str:
        """Delete a sticky note by ID."""
        db = SessionLocal()
        try:
            s = db.query(StickyNote).filter(StickyNote.id == sticky_id).first()
            if not s:
                return _format_error("Sticky note not found")
            db.delete(s)
            db.commit()
            return _format_deleted(sticky_id)
        finally:
            db.close()