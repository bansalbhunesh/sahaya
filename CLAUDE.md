# CLAUDE.md — Sahaya operating manual

Sahaya is an autonomous flood-response operations agent. Gemini 3 (via Google Cloud
Agent Builder / ADK) plans; the MongoDB MCP server is its hands; MongoDB Atlas is the
single source of truth; a live ops-console dashboard shows every mutation.

Built for the Google Cloud Rapid Agent Hackathon (MongoDB track), June 2026.

## Architecture in one paragraph

`app/agent.py` defines the ADK `LlmAgent` (model from `$SAHAYA_MODEL`, default
`gemini-3-flash-preview`) whose only tools come from `McpToolset` spawning
`npx -y mongodb-mcp-server@latest` over stdio with `MDB_MCP_CONNECTION_STRING`.
`app/server.py` is a FastAPI app: serves `web/` (static dashboard), `POST /api/sos`
(citizen report intake → inserts into `reports`), `POST /api/run` (one agent ops
cycle via ADK `Runner`; agent events are pushed to an in-memory feed), `GET
/api/state` (dashboard polling — reads Atlas directly with pymongo), `GET
/api/events` (agent activity feed). `app/seed.py` resets + seeds the Mumbai
monsoon scenario. Collections: `reports`, `shelters`, `depots`, `assignments`,
`sitreps` in db `sahaya` (2dsphere indexes on location fields).

## Commands

```powershell
# env (Windows dev box)
.venv\Scripts\Activate.ps1
# secrets live in .env (never committed): GOOGLE_API_KEY, MDB_MCP_CONNECTION_STRING, SAHAYA_MODEL

python -m app.seed          # reset + seed the demo scenario (destructive on db 'sahaya')
uvicorn app.server:app --reload --port 8080   # run locally → http://localhost:8080
python -m app.smoke         # end-to-end smoke: seed → one agent cycle → assert assignments exist
pytest tests/ -q            # API tests (needs reachable Mongo; agent/LLM not exercised)
```

Deploy (Cloud Run, from repo root — Dockerfile installs Node for npx):

```bash
gcloud run deploy sahaya --source . --region asia-south1 --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=...,MDB_MCP_CONNECTION_STRING=...
```

## Conventions

- Python 3.12+, no ORM — pymongo direct for reads, **all agent writes go through the
  MCP server** (this is the hackathon's point; never bypass it in agent code).
- Dashboard is dependency-free vanilla JS + Leaflet from CDN. No build step, ever.
- The agent instruction (the ops protocol) lives in `app/agent.py` as `OPS_PROTOCOL`.
  It is the product. Edit deliberately; keep phases numbered.
- Logging: stdlib `logging`, JSON-ish single lines, logger name = module.
- Demo-critical path > everything. If a change risks the seed → run → dashboard loop
  within 2h of a demo, don't.

## Gotchas

- mongodb-mcp-server needs Node ≥20.19; the Dockerfile installs Node 22 in the
  Python image — keep that if you touch the Dockerfile.
- ADK class is `McpToolset` (lowercase 'cp' in 'Mcp'), import
  `StdioConnectionParams` from `google.adk.tools.mcp_tool.mcp_session_manager`,
  `StdioServerParameters` from `mcp`.
- Atlas M0: 500-connection cap; don't create pymongo clients per request — module
  singleton in `app/db.py`.
- `python -m app.seed` drops collections. Fine for demo; obviously not for prod.
