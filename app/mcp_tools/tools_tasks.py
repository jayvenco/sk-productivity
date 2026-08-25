"""
MCP tools for the Tasks module.
"""
import json
from app.database import SessionLocal
from app.mcp_tools._shared import _format_item, _format_list, _format_error, _format_deleted
from app.models.tasks import Task, TaskStatus


def _task_to_json(task):
    return _format_item({
        "id": task.id, "title": task.title, "description": task.description,
        "status": task.status.value, "due_date": task.due_date,
        "created_at": task.created_at, "updated_at": task.updated_at,
    })


def _tasks_to_json(tasks):
    return _format_list([json.loads(_task_to_json(t)) for t in tasks])




def register_tasks_tools(mcp, mcp_prefix="swissknife"):
    @mcp.tool(name=f"{mcp_prefix}_tasks_list")
    def tasks_list() -> str:
        """List all tasks, ordered by most recent first."""
        db = SessionLocal()
        try:
            tasks = db.query(Task).order_by(Task.created_at.desc()).all()
            return _tasks_to_json(tasks)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_tasks_get")
    def tasks_get(task_id: int) -> str:
        """Get a single task by its ID."""
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return _format_error("Task not found")
            return _task_to_json(task)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_tasks_create")
    def tasks_create(title: str, description: str = "") -> str:
        """Create a new task. Returns the created task."""
        db = SessionLocal()
        try:
            task = Task(title=title, description=description)
            db.add(task)
            db.commit()
            db.refresh(task)
            return _task_to_json(task)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_tasks_edit")
    def tasks_edit(task_id: int, title: str = None, description: str = None, status: str = None) -> str:
        """Edit an existing task. Only provided fields are updated. Status: pending, in_progress, completed."""
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return _format_error("Task not found")
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if status is not None:
                task.status = TaskStatus(status)
            db.commit()
            db.refresh(task)
            return _task_to_json(task)
        finally:
            db.close()

    @mcp.tool(name=f"{mcp_prefix}_tasks_delete")
    def tasks_delete(task_id: int) -> str:
        """Delete a task by its ID."""
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return _format_error("Task not found")
            db.delete(task)
            db.commit()
            return _format_deleted(task_id)
        finally:
            db.close()