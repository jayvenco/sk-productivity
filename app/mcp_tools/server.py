"""
MCP Server for swissknife-productivity (FastMCP).

Run with: python -m app.mcp_tools.server
Register in Hermes config.yaml:
  mcp_servers:
    swissknife:
      command: "python"
      args: ["-m", "app.mcp_tools.server"]
"""

import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import init_db
from app.mcp_tools.tools_notes import register_notes_tools
from app.mcp_tools.tools_tasks import register_tasks_tools
from app.mcp_tools.tools_kanban import register_kanban_tools
from app.mcp_tools.tools_pomodoro import register_pomodoro_tools
from app.mcp_tools.tools_wiki import register_wiki_tools
from app.mcp_tools.tools_snippets import register_snippets_tools


from app.mcp_tools.tools_tags import register_tags_tools


def create_server():
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP(
        "swissknife-productivity",
        instructions="Tools for the swissknife-productivity personal productivity app. "
        "Manage notes, tasks, kanban cards, pomodoro sessions, wiki pages, and code snippets.",
    )

    # Register all module tools via decorator-style
    register_notes_tools(mcp, mcp_prefix="mcp_swissknife")
    register_tasks_tools(mcp, mcp_prefix="mcp_swissknife")
    register_kanban_tools(mcp, mcp_prefix="mcp_swissknife")
    register_pomodoro_tools(mcp, mcp_prefix="mcp_swissknife")
    register_wiki_tools(mcp, mcp_prefix="mcp_swissknife")
    register_snippets_tools(mcp, mcp_prefix="mcp_swissknife")
    register_tags_tools(mcp, mcp_prefix="mcp_swissknife")

    return mcp


def main():
    init_db()
    mcp = create_server()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()