"""
MCP tools for the Kanban module.
"""
import json
from app.database import SessionLocal
from app.mcp_tools._shared import _format_item, _format_list, _format_error, _format_deleted
from app.models.kanban import KanbanCard, KanbanColumn


# ── Column Tools ────────────────────────────────────────────────────

def _column_to_json(col):
    return _format_item({
        "id": col.id, "name": col.name,
        "position": col.position, "color": col.color,
        "created_at": col.created_at,
    })


def _columns_to_json(cols):
    return _format_list([json.loads(_column_to_json(c)) for c in cols])


# ── Card Tools ──────────────────────────────────────────────────────

def _card_to_json(card):
    return _format_item({
        "id": card.id, "title": card.title, "description": card.description,
        "column_id": card.column_id, "position": card.position,
        "created_at": card.created_at, "updated_at": card.updated_at,
    })


def _cards_to_json(cards):
    return _format_list([json.loads(_card_to_json(c)) for c in cards])


# ── Registration ────────────────────────────────────────────────────

def register_kanban_tools(mcp, mcp_prefix="swissknife"):
    # ── Column Management ──────────────────────────────────────────

    @mcp.tool(name=f"{mcp_prefix}_kanban_columns_list")
    def kanban_columns_list() -> str:
        """List all kanban columns/steps, ordered by position."""
        db = SessionLocal()
        try:
            cols = db.query(KanbanColumn).order_by(KanbanColumn.position).all()
            return _columns_to_json(cols)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_kanban_columns_create")
    def kanban_columns_create(name: str, position: int = 0, color: str = "#6b7280") -> str:
        """Create a new kanban column/step."""
        db = SessionLocal()
        try:
            col = KanbanColumn(name=name, position=position, color=color)
            db.add(col)
            db.commit()
            db.refresh(col)
            return _column_to_json(col)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_kanban_columns_rename")
    def kanban_columns_rename(column_id: int, name: str) -> str:
        """Rename a kanban column/step."""
        db = SessionLocal()
        try:
            col = db.query(KanbanColumn).filter(KanbanColumn.id == column_id).first()
            if not col:
                return _format_error("Column not found")
            col.name = name
            db.commit()
            db.refresh(col)
            return _column_to_json(col)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_kanban_columns_delete")
    def kanban_columns_delete(column_id: int) -> str:
        """Delete a kanban column/step. Cards are moved to the first remaining column."""
        db = SessionLocal()
        try:
            col = db.query(KanbanColumn).filter(KanbanColumn.id == column_id).first()
            if not col:
                return _format_error("Column not found")
            other = db.query(KanbanColumn).filter(KanbanColumn.id != column_id)\
                .order_by(KanbanColumn.position).first()
            if other:
                for card in col.cards:
                    card.column_id = other.id
            db.delete(col)
            db.commit()
            return _format_deleted(column_id)
        finally:
            db.close()

    # ── Card Management ───────────────────────────────────────────

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
    def kanban_create(title: str, description: str = "", column_id: int = None, position: int = 0) -> str:
        """Create a new kanban card. If no column_id given, assigns to first column."""
        db = SessionLocal()
        try:
            if column_id is None:
                first = db.query(KanbanColumn).order_by(KanbanColumn.position).first()
                if not first:
                    return _format_error("No columns exist. Create a column first.")
                column_id = first.id
            card = KanbanCard(title=title, description=description, column_id=column_id, position=position)
            db.add(card)
            db.commit()
            db.refresh(card)
            return _card_to_json(card)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_kanban_edit")
    def kanban_edit(card_id: int, title: str = None, description: str = None,
                    column_id: int = None, position: int = None) -> str:
        """Edit an existing kanban card. Only provided fields are updated."""
        db = SessionLocal()
        try:
            card = db.query(KanbanCard).filter(KanbanCard.id == card_id).first()
            if not card:
                return _format_error("Kanban card not found")
            if title is not None:
                card.title = title
            if description is not None:
                card.description = description
            if column_id is not None:
                card.column_id = column_id
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
    def kanban_move(card_id: int, column_id: int, position: int = 0) -> str:
        """Move a kanban card to a different column and optionally set position."""
        db = SessionLocal()
        try:
            card = db.query(KanbanCard).filter(KanbanCard.id == card_id).first()
            if not card:
                return _format_error("Kanban card not found")
            card.column_id = column_id
            card.position = position
            db.commit()
            db.refresh(card)
            return _card_to_json(card)
        finally:
            db.close()