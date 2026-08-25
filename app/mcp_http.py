"""
Lightweight MCP server for swissknife-productivity.

Runs on the Hermes Python (no project deps needed - talks to REST API via HTTP).
"""
import json, urllib.request, urllib.error
from urllib.parse import quote

API_BASE = "http://localhost:4442/api"


def _api(method, path, data=None):
    url = f"{API_BASE}{path}"
    if data is not None:
        body = json.dumps(data).encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method=method)
    else:
        req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode()) if resp.status != 204 else json.dumps({"deleted": True})
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        return json.dumps({"error": f"HTTP {e.code}: {detail}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def create_server():
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP(
        "swissknife-productivity",
        instructions="Tools for the swissknife-productivity personal productivity app. "
        "Manage notes, tasks, kanban cards, pomodoro sessions, wiki pages, and code snippets.",
    )

    # ---- Health ----
    @mcp.tool(name="mcp_swissknife_health")
    def health() -> str:
        """Check if the backend is running."""
        return json.dumps({"status": "ok", "app": "swissknife-productivity"})

    # ---- Notes ----
    @mcp.tool(name="mcp_swissknife_notes_list")
    def notes_list() -> str:
        """List all notes."""
        return json.dumps(_api("GET", "/notes"))

    @mcp.tool(name="mcp_swissknife_notes_get")
    def notes_get(note_id: int) -> str:
        """Get a note by ID."""
        return json.dumps(_api("GET", f"/notes/{note_id}"))

    @mcp.tool(name="mcp_swissknife_notes_create")
    def notes_create(title: str, content: str = "") -> str:
        """Create a note."""
        return json.dumps(_api("POST", "/notes", {"title": title, "content": content}))

    @mcp.tool(name="mcp_swissknife_notes_edit")
    def notes_edit(note_id: int, title: str = None, content: str = None) -> str:
        """Edit a note."""
        data = {}
        if title: data["title"] = title
        if content: data["content"] = content
        return json.dumps(_api("PUT", f"/notes/{note_id}", data))

    @mcp.tool(name="mcp_swissknife_notes_delete")
    def notes_delete(note_id: int) -> str:
        """Delete a note."""
        return json.dumps(_api("DELETE", f"/notes/{note_id}"))

    # ---- Tasks ----
    @mcp.tool(name="mcp_swissknife_tasks_list")
    def tasks_list() -> str:
        """List all tasks."""
        return json.dumps(_api("GET", "/tasks"))

    @mcp.tool(name="mcp_swissknife_tasks_get")
    def tasks_get(task_id: int) -> str:
        """Get a task by ID."""
        return json.dumps(_api("GET", f"/tasks/{task_id}"))

    @mcp.tool(name="mcp_swissknife_tasks_create")
    def tasks_create(title: str, description: str = "") -> str:
        """Create a task."""
        return json.dumps(_api("POST", "/tasks", {"title": title, "description": description}))

    @mcp.tool(name="mcp_swissknife_tasks_edit")
    def tasks_edit(task_id: int, title: str = None, description: str = None, status: str = None) -> str:
        """Edit a task. Status: pending, in_progress, completed."""
        data = {}
        if title: data["title"] = title
        if description: data["description"] = description
        if status: data["status"] = status
        return json.dumps(_api("PUT", f"/tasks/{task_id}", data))

    @mcp.tool(name="mcp_swissknife_tasks_delete")
    def tasks_delete(task_id: int) -> str:
        """Delete a task."""
        return json.dumps(_api("DELETE", f"/tasks/{task_id}"))

    # ---- Kanban ----
    @mcp.tool(name="mcp_swissknife_kanban_list")
    def kanban_list() -> str:
        """List all kanban cards."""
        return json.dumps(_api("GET", "/kanban"))

    @mcp.tool(name="mcp_swissknife_kanban_get")
    def kanban_get(card_id: int) -> str:
        """Get a kanban card by ID."""
        return json.dumps(_api("GET", f"/kanban/{card_id}"))

    @mcp.tool(name="mcp_swissknife_kanban_create")
    def kanban_create(title: str, description: str = "", status: str = "todo", position: int = 0) -> str:
        """Create a kanban card. Status: todo, doing, done."""
        return json.dumps(_api("POST", "/kanban", {"title": title, "description": description, "status": status, "position": position}))

    @mcp.tool(name="mcp_swissknife_kanban_edit")
    def kanban_edit(card_id: int, title: str = None, description: str = None, status: str = None, position: int = None) -> str:
        """Edit a kanban card."""
        data = {}
        if title: data["title"] = title
        if description: data["description"] = description
        if status: data["status"] = status
        if position: data["position"] = position
        return json.dumps(_api("PUT", f"/kanban/{card_id}", data))

    @mcp.tool(name="mcp_swissknife_kanban_delete")
    def kanban_delete(card_id: int) -> str:
        """Delete a kanban card."""
        return json.dumps(_api("DELETE", f"/kanban/{card_id}"))

    @mcp.tool(name="mcp_swissknife_kanban_move")
    def kanban_move(card_id: int, status: str, position: int = 0) -> str:
        """Move a kanban card to another column."""
        return json.dumps(_api("PUT", f"/kanban/{card_id}", {"status": status, "position": position}))

    # ---- Pomodoro ----
    @mcp.tool(name="mcp_swissknife_pomodoro_status")
    def pomodoro_status() -> str:
        """Check if a pomodoro session is running."""
        return json.dumps(_api("GET", "/pomodoro/status"))

    @mcp.tool(name="mcp_swissknife_pomodoro_start")
    def pomodoro_start(session_type: str = "focus", duration_minutes: int = 25) -> str:
        """Start a pomodoro session."""
        return json.dumps(_api("POST", "/pomodoro/start", {"session_type": session_type, "duration_minutes": duration_minutes}))

    @mcp.tool(name="mcp_swissknife_pomodoro_stop")
    def pomodoro_stop() -> str:
        """Stop the current pomodoro session."""
        return json.dumps(_api("POST", "/pomodoro/stop"))

    @mcp.tool(name="mcp_swissknife_pomodoro_list")
    def pomodoro_list() -> str:
        """List recent pomodoro sessions."""
        return json.dumps(_api("GET", "/pomodoro"))

    # ---- Wiki ----
    @mcp.tool(name="mcp_swissknife_wiki_list")
    def wiki_list() -> str:
        """List wiki pages."""
        return json.dumps(_api("GET", "/wiki"))

    @mcp.tool(name="mcp_swissknife_wiki_get")
    def wiki_get(page_id: int) -> str:
        """Get a wiki page by ID."""
        return json.dumps(_api("GET", f"/wiki/{page_id}"))

    @mcp.tool(name="mcp_swissknife_wiki_get_by_slug")
    def wiki_get_by_slug(slug: str) -> str:
        """Get a wiki page by URL slug."""
        return json.dumps(_api("GET", f"/wiki/by-slug/{slug}"))

    @mcp.tool(name="mcp_swissknife_wiki_search")
    def wiki_search(query: str) -> str:
        """Search wiki pages."""
        return json.dumps(_api("GET", f"/wiki?q={quote(query)}"))

    @mcp.tool(name="mcp_swissknife_wiki_create")
    def wiki_create(title: str, slug: str, content: str = "") -> str:
        """Create a wiki page."""
        return json.dumps(_api("POST", "/wiki", {"title": title, "slug": slug, "content": content}))

    @mcp.tool(name="mcp_swissknife_wiki_edit")
    def wiki_edit(page_id: int, title: str = None, slug: str = None, content: str = None) -> str:
        """Edit a wiki page."""
        data = {}
        if title: data["title"] = title
        if slug: data["slug"] = slug
        if content: data["content"] = content
        return json.dumps(_api("PUT", f"/wiki/{page_id}", data))

    @mcp.tool(name="mcp_swissknife_wiki_delete")
    def wiki_delete(page_id: int) -> str:
        """Delete a wiki page."""
        return json.dumps(_api("DELETE", f"/wiki/{page_id}"))

    # ---- Snippets ----
    @mcp.tool(name="mcp_swissknife_snippets_list")
    def snippets_list() -> str:
        """List all snippets."""
        return json.dumps(_api("GET", "/snippets"))

    @mcp.tool(name="mcp_swissknife_snippets_get")
    def snippets_get(snippet_id: int) -> str:
        """Get a snippet by ID."""
        return json.dumps(_api("GET", f"/snippets/{snippet_id}"))

    @mcp.tool(name="mcp_swissknife_snippets_create")
    def snippets_create(title: str, language: str = "text", code: str = "") -> str:
        """Create a code snippet."""
        return json.dumps(_api("POST", "/snippets", {"title": title, "language": language, "code": code}))

    @mcp.tool(name="mcp_swissknife_snippets_edit")
    def snippets_edit(snippet_id: int, title: str = None, language: str = None, code: str = None) -> str:
        """Edit a snippet."""
        data = {}
        if title: data["title"] = title
        if language: data["language"] = language
        if code: data["code"] = code
        return json.dumps(_api("PUT", f"/snippets/{snippet_id}", data))

    @mcp.tool(name="mcp_swissknife_snippets_delete")
    def snippets_delete(snippet_id: int) -> str:
        """Delete a snippet."""
        return json.dumps(_api("DELETE", f"/snippets/{snippet_id}"))

    return mcp


def main():
    mcp = create_server()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()