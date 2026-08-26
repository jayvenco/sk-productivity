"""
MCP tools for the Tags module.
"""
import json
from app.database import SessionLocal
from app.models.tags import Tag, Tagging
from app.mcp_tools._shared import _format_item, _format_list, _format_error, _format_deleted


def _tag_to_json(tag):
    return _format_item({
        "id": tag.id, "name": tag.name, "color": tag.color,
    })


def register_tags_tools(mcp, mcp_prefix="swissknife"):
    @mcp.tool(name=f"{mcp_prefix}_tags_list")
    def tags_list() -> str:
        """List all tags."""
        db = SessionLocal()
        try:
            tags = db.query(Tag).order_by(Tag.name).all()
            return _format_list([json.loads(_tag_to_json(t)) for t in tags])
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_tags_create")
    def tags_create(name: str, color: str = "#4f8cff") -> str:
        """Create a new tag. Name must be unique."""
        db = SessionLocal()
        try:
            existing = db.query(Tag).filter(Tag.name == name).first()
            if existing:
                return _format_error("Tag already exists")
            tag = Tag(name=name, color=color)
            db.add(tag)
            db.commit()
            db.refresh(tag)
            return _tag_to_json(tag)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_tags_delete")
    def tags_delete(tag_id: int) -> str:
        """Delete a tag by ID."""
        db = SessionLocal()
        try:
            tag = db.query(Tag).filter(Tag.id == tag_id).first()
            if not tag:
                return _format_error("Tag not found")
            db.delete(tag)
            db.commit()
            return _format_deleted(tag_id)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_tags_attach")
    def tags_attach(tag_id: int, item_type: str, item_id: int) -> str:
        """Attach a tag to an item. item_type: note, task, kanban, wiki, snippet."""
        db = SessionLocal()
        try:
            existing = db.query(Tagging).filter(
                Tagging.tag_id == tag_id,
                Tagging.tagable_type == item_type,
                Tagging.tagable_id == item_id,
            ).first()
            if existing:
                return _format_error("Tag already attached")
            tagging = Tagging(tag_id=tag_id, tagable_type=item_type, tagable_id=item_id)
            db.add(tagging)
            db.commit()
            return json.dumps({"attached": True, "tag_id": tag_id})
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_tags_detach")
    def tags_detach(tag_id: int, item_type: str, item_id: int) -> str:
        """Detach a tag from an item."""
        db = SessionLocal()
        try:
            tagging = db.query(Tagging).filter(
                Tagging.tag_id == tag_id,
                Tagging.tagable_type == item_type,
                Tagging.tagable_id == item_id,
            ).first()
            if not tagging:
                return _format_error("Tag not attached")
            db.delete(tagging)
            db.commit()
            return json.dumps({"detached": True, "tag_id": tag_id})
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_tags_get_for_item")
    def tags_get_for_item(item_type: str, item_id: int) -> str:
        """Get all tags attached to an item."""
        db = SessionLocal()
        try:
            taggings = db.query(Tagging).filter(
                Tagging.tagable_type == item_type,
                Tagging.tagable_id == item_id,
            ).all()
            tag_ids = [t.tag_id for t in taggings]
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all() if tag_ids else []
            return _format_list([json.loads(_tag_to_json(t)) for t in tags])
        finally:
            db.close()