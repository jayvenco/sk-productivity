"""Shared JSON formatting helpers for MCP tools.

Uses proper json.dumps() instead of hand-rolled f-string concatenation,
which handles all Unicode characters, null bytes, and control chars safely.
"""
import json
from datetime import datetime
from typing import Any


def _format_item(data: dict) -> str:
    """Format a single item dict to a JSON string."""
    return json.dumps(data, default=_json_serial)


def _format_list(items: list[dict]) -> str:
    """Format a list of item dicts to a JSON string."""
    return json.dumps({"items": items, "total": len(items)}, default=_json_serial)


def _format_error(message: str) -> str:
    """Format an error response."""
    return json.dumps({"error": message})


def _format_deleted(item_id: int) -> str:
    """Format a delete confirmation."""
    return json.dumps({"deleted": True, "id": item_id})


def _json_serial(obj: Any) -> str:
    """JSON serializer for objects not serializable by default json code."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if hasattr(obj, 'value'):  # Enum
        return obj.value
    raise TypeError(f"Type {type(obj)} not serializable")