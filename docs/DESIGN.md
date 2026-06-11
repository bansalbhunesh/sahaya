# DESIGN.md — Sahaya system design

## Problem

During urban floods in India, the bottleneck is not resources — it is *coordination*.
Control rooms receive thousands of unstructured SOS messages (calls, WhatsApp, social
media) and must manually triage, dedupe, match victims to shelters with capacity, and
dispatch boats/medics/supplies from depots. Minutes of human latency cost lives.
Sahaya is the control-room operator that never sleeps: it autonomously turns a chaotic
SOS inbox into dispatched, tracked, inventory-accounted rescue operations.

## Agent architecture

```
 citizen / control room                    ┌────────────────────────────┐
   POST /api/sos  ──────────────┐          │  MongoDB Atlas (db: sahaya)│
                                ▼          │  reports    shelters       │
 ┌──────────────────────────────────────┐  │  depots     assignments    │
 │ FastAPI (Cloud Run, asia-south1)     │  │  sitreps                   │
 │  /            ops-console dashboard  │  └──────▲─────────────────────┘
 │  /api/state   pymongo reads (poll)   │─────────┘ direct reads (dashboard only)
 │  /api/events  agent activity feed    │
 │  /api/run     one ops cycle          │
 │      └─► ADK Runner ─► LlmAgent      │
 │           (Gemini 3,                 │
 │            gemini-3-flash-preview)   │
 │              └─► McpToolset ── stdio ──► npx mongodb-mcp-server ──► Atlas
 │                  ALL agent writes    │      (find, aggregate, insert-many,
 └──────────────────────────────────────┘       update-many, count, ...)
```

- **Planning loop**: ADK `LlmAgent` running `OPS_PROTOCOL`, a numbered five-phase
  doctrine: (1) INGEST — find unprocessed reports; (2) TRIAGE — severity P0–P3 +
  dedupe against open reports (same locality + similar text ⇒ merge, increment
  `duplicate_count`); (3) MATCH — geo-nearest shelter with free capacity via
  `aggregate` `$geoNear`; (4) DISPATCH — `insert-many` assignments (rescue team,
  depot, resources, ETA), `update-many` to decrement depot inventory and shelter
  capacity, mark reports `dispatched`; (5) SITREP — insert a situation report
  summarizing actions, open risks, and resource posture.
- **Why single agent, multi-phase** (not a multi-agent graph): one Gemini 3 agent
  with an explicit doctrine is more reliable under tool-call-heavy workloads, easier
  to audit in the event feed, and the phases are inherently sequential. The protocol
  *is* the planning loop; ADK handles tool orchestration and retries within it.
- **Gemini 3 usage**: `gemini-3-flash-preview` by default (fast agentic tool-calling;
  the demo runs many tool rounds); `SAHAYA_MODEL` env switches to
  `gemini-3.1-pro-preview` for higher-stakes reasoning. Temperature low (0.2) —
  ops, not poetry.

## MCP surface (MongoDB MCP server — the agent's only hands)

Tool filter (least privilege): `find`, `aggregate`, `count`, `insert-many`,
`update-many`, `list-collections`, `collection-indexes`. Excluded: `drop-*`,
`delete-many`, `create-collection`, Atlas admin tools. The agent cannot destroy
data; it can only read, create, and update. Seeding/reset is a human-run script,
not an agent capability.

## Data flow (one ops cycle)

1. SOS reports arrive (`/api/sos` or seeded) → `reports` with `status:"new"`,
   GeoJSON `location`.
2. `/api/run` → Runner streams agent events → each tool call/result/thought is
   appended to the activity feed (`/api/events`) with timestamps.
3. Agent executes OPS_PROTOCOL via MCP tools; Atlas state mutates.
4. Dashboard polls `/api/state` (2s): map markers (reports by severity, shelters
   by occupancy, depots), assignment table, sitrep panel, live activity feed.

## Failure handling

- MCP spawn failure (no Node/npx): server starts anyway; `/api/run` returns 503
  with a clear message; dashboard shows "agent offline".
- Gemini errors/quota: cycle aborts, partial actions remain consistent (each
  dispatch is one insert + paired updates, ordered so inventory never goes
  negative; agent instructed to verify with `count`/`find` before writes).
- Atlas unreachable: `/api/state` returns last-known snapshot + `degraded:true`.
- Runaway loops: ADK max iterations + 120s cycle budget enforced in `/api/run`.

## Human-in-the-loop

The agent acts autonomously per cycle but every action is (a) journaled in the
activity feed in plain language, (b) reversible (assignments have status; a human
can cancel from the data layer), (c) bounded — the agent may never delete and runs
only when a cycle is triggered (button/cron), never as an unbounded daemon. The
sitrep is written *for the human commander*; the dashboard is the oversight surface
("under your oversight" per the hackathon brief).

## Deployment topology

Cloud Run (asia-south1), single container: Python 3.12 + Node 22 (for the stdio MCP
server). Min instances 1 for the judging window (cold starts spawn npx). Atlas M0
(AWS Mumbai) — same region, low latency. Secrets as Cloud Run env vars (GOOGLE_API_KEY,
MDB_MCP_CONNECTION_STRING). The hosted URL serves the dashboard and live demo.
