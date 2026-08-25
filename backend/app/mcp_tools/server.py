"""
MCP Server for swissknife-productivity (MCP SDK v2.1.0).

Run with: python -m app.mcp.server
Register in Hermes config.yaml:
  mcp_servers:
    swissknife:
      command: "python"
      args: ["-m", "app.mcp.server"]
"""

import sys, os, asyncio, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db


def create_server():
    from mcp.server.mcpserver import MCPServer
    from mcp.server import runner

    server = MCPServer(
        name="swissknife-productivity",
        instructions="Tools for the swissknife-productivity personal productivity app. "
        "Manage notes, tasks, kanban cards, pomodoro sessions, wiki pages, and code snippets.",
        version="0.1.0",
    )

    # Register all tools
    from app.mcp_tools.tools_notes import register_notes_tools
    from app.mcp_tools.tools_tasks import register_tasks_tools
    from app.mcp_tools.tools_kanban import register_kanban_tools
    from app.mcp_tools.tools_pomodoro import register_pomodoro_tools
    from app.mcp_tools.tools_wiki import register_wiki_tools
    from app.mcp_tools.tools_snippets import register_snippets_tools

    register_notes_tools(server)
    register_tasks_tools(server)
    register_kanban_tools(server)
    register_pomodoro_tools(server)
    register_wiki_tools(server)
    register_snippets_tools(server)

    return server, runner


def main():
    init_db()
    server, runner_module = create_server()
    asyncio.run(runner_module.run(server))


if __name__ == "__main__":
    main()