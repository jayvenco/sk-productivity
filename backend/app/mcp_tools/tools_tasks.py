"""
MCP tools for the Tasks module.
"""
from app.database import SessionLocal
from app.models.tasks import Task, TaskStatus


def _task_to_json(task):
    due = f'"{task.due_date.isoformat()}"' if task.due_date else "null"
    return (
        f'{{"id":{task.id},"title":"{_escape(task.title)}","description":"{_escape(task.description)}",'
        f'"status":"{task.status.value}","due_date":{due},'
        f'"created_at":"{task.created_at.isoformat()}","updated_at":"{task.updated_at.isoformat()}"}}'
    )


def _tasks_to_json(tasks):
    items = ",".join(_task_to_json(t) for t in tasks)
    return f'{{"items":[{items}],"total":{len(tasks)}}}'


def _escape(s):
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")


def list_tasks() -> str:
    """List all tasks, ordered by most recent first."""
    db = SessionLocal()
    try:
        tasks = db.query(Task).order_by(Task.created_at.desc()).all()
        return _tasks_to_json(tasks)
    finally:
        db.close()


def get_task(task_id: int) -> str:
    """Get a single task by its ID."""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return '{"error": "Task not found"}'
        return _task_to_json(task)
    finally:
        db.close()


def create_task(title: str, description: str = "") -> str:
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


def edit_task(task_id: int, title: str = None, description: str = None, status: str = None) -> str:
    """Edit an existing task. Only provided fields are updated. Status: pending, in_progress, completed."""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return '{"error": "Task not found"}'
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


def delete_task(task_id: int) -> str:
    """Delete a task by its ID."""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return '{"error": "Task not found"}'
        db.delete(task)
        db.commit()
        return f'{{"deleted": true, "id": {task_id}}}'
    finally:
        db.close()


def register_tasks_tools(server):
    server.add_tool(list_tasks, name="mcp_swissknife_tasks_list")
    server.add_tool(get_task, name="mcp_swissknife_tasks_get")
    server.add_tool(create_task, name="mcp_swissknife_tasks_create")
    server.add_tool(edit_task, name="mcp_swissknife_tasks_edit")
    server.add_tool(delete_task, name="mcp_swissknife_tasks_delete")