# swissknife-productivity

Een lichtgewicht, zelf-gehoste productiviteitsapplicatie met Kanban-bord, notities, taken, pomodoro-timer, wiki en code snippets.

## Architectuur

- **Backend:** Python FastAPI + REST API (voor SvelteKit frontend)
- **MCP Server:** Hermes Agent krijgt gestructureerde tools via MCP
- **Frontend:** SvelteKit (responsive webinterface)
- **Database:** SQLite (gedeeld tussen REST API en MCP server)

## Snel starten

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.main
# Draait op http://localhost:4442
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Draait op http://localhost:4443
```

### MCP Server (voor Hermes Agent)
```bash
cd backend
source venv/bin/activate
python -m app.mcp_tools.server
```

Registreer in Hermes config.yaml:
```yaml
mcp_servers:
  swissknife:
    command: "python"
    args: ["-m", "app.mcp_tools.server"]
    env:
      PYTHONPATH: "/pad/naar/skp/backend"
```

## Modules

| Module | REST API | MCP Tools |
|--------|----------|-----------|
| Notities | `/api/notes` | `mcp_swissknife_notes_*` |
| Taken | `/api/tasks` | `mcp_swissknife_tasks_*` |
| Kanban | `/api/kanban` | `mcp_swissknife_kanban_*` |
| Pomodoro | `/api/pomodoro` | `mcp_swissknife_pomodoro_*` |
| Wiki | `/api/wiki` | `mcp_swissknife_wiki_*` |
| Snippets | `/api/snippets` | `mcp_swissknife_snippets_*` |

## Docker

```bash
docker-compose up
# Draait op http://localhost:4442
```