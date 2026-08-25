"""
MCP tools for the Kanban module.
"""
import json
from app.database import SessionLocal
from app.mcp_tools._shared import _format_item, _format_list, _format_error, _format_deleted
from app.models.kanban import KanbanCard, KanbanStatus


def _card_to_json(card):
    return _format_item({
        "id": card.id, "title": card.title, "description": card.description,
        "status": card.status.value, "position": card.position,
        "created_at": card.created_at, "updated_at": card.updated_at,
    })


def _cards_to_json(cards):
    return _format_list([json.loads(_card_to_json(c)) for c in cards])




def register_kanban_tools(mcp, mcp_prefix="swissknife"):
    @mcp.tool(name=f"{mcp_prefix}_kanban_list")
    def kanban_list() -> str:
        """List all kanban cards, ordered by position."""
        db = SessionLocal()
        try:
            cards = db.query(KanbanCard).order_by(KanbanCard.position).all()
            return _cards_to_json(cards)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_kanban_get")
    def kanban_get(card_id: int) -> str:
        """Get a single kanban card by its ID."""
        db = SessionLocal()
        try:
            card = db.query(KanbanCard).filter(KanbanCard.id == card_id).first()
            if not card:
                return _format_error("Kanban card not found")
            return _card_to_json(card)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_kanban_create")
    def kanban_create(title: str, description: str = "", status: str = "todo", position: int = 0) -> str:
        """Create a new kanban card. Status: todo, doing, done."""
        db = SessionLocal()
        try:
            card = KanbanCard(title=title, description=description, status=KanbanStatus(status), position=position)
            db.add(card)
            db.commit()
            db.refresh(card)
            return _card_to_json(card)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_kanban_edit")
    def kanban_edit(card_id: int, title: str = None, description: str = None, status: str = None, position: int = None) -> str:
        """Edit an existing kanban card. Only provided fields are updated. Status: todo, doing, done."""
        db = SessionLocal()
        try:
            card = db.query(KanbanCard).filter(KanbanCard.id == card_id).first()
            if not card:
                return _format_error("Kanban card not found")
            if title is not None:
                card.title = title
            if description is not None:
                card.description = description
            if status is not None:
                card.status = KanbanStatus(status)
            if position is not None:
                card.position = position
            db.commit()
            db.refresh(card)
            return _card_to_json(card)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_kanban_delete")
    def kanban_delete(card_id: int) -> str:
        """Delete a kanban card by its ID."""
        db = SessionLocal()
        try:
            card = db.query(KanbanCard).filter(KanbanCard.id == card_id).first()
            if not card:
                return _format_error("Kanban card not found")
            db.delete(card)
            db.commit()
            return _format_deleted(card_id)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_kanban_move")
    def kanban_move(card_id: int, status: str, position: int = 0) -> str:
        """Move a kanban card to a new column (todo/doing/done) and optionally set position."""
        db = SessionLocal()
        try:
            card = db.query(KanbanCard).filter(KanbanCard.id == card_id).first()
            if not card:
                return _format_error("Kanban card not found")
            card.status = KanbanStatus(status)
            card.position = position
            db.commit()
            db.refresh(card)
            return _card_to_json(card)
        finally:
            db.close()