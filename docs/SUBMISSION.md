# SUBMISSION.md — Devpost form, copy-paste ready

**Project name:** Sahaya

**Tagline (≤60 chars):** Autonomous flood-response ops agent — triage to dispatch.

**Partner track:** MongoDB

**Hosted URL:** <CLOUD RUN URL — fill after deploy>

**Repo:** <GITHUB URL — fill after push> (public, MIT license at root)

**Video:** <YOUTUBE URL — fill after upload>

**Built with:** google-cloud-agent-builder, adk, gemini-3, mongodb-atlas,
mongodb-mcp-server, model-context-protocol, cloud-run, fastapi, python, leaflet

---

## Description (long form)

### Inspiration
Every monsoon, Indian cities flood and the same failure repeats: not a lack of boats
or shelters, but coordination collapse. Control rooms receive thousands of
unstructured SOS messages — duplicated across phone calls, WhatsApp forwards, and
social media, in multiple languages — while dispatchers manually match victims to
shelters and depots. Minutes of latency cost lives. We built the control-room
operator that never sleeps.

### What it does
Sahaya is an autonomous flood-response operations agent. In one ops cycle it ingests
every unprocessed SOS report, triages severity P0–P3, detects and merges duplicate
reports (including cross-language duplicates — "family trapped on roof" and "paani
badh raha hai, bachche hain" describing the same building), geo-matches victims to
the nearest shelter with free capacity and the nearest depot with sufficient stock,
writes dispatch orders, decrements depot inventory, updates shelter occupancy, and
files a commander's situation report — all visible live on an ops-console dashboard
with a real-time journal of every agent decision and database action. Citizens (or
the control room) can submit new SOS reports from the dashboard and watch the agent
handle them on the next cycle.

### How we built it
- **Google Cloud Agent Builder / ADK (Python)**: the agent core — an `LlmAgent`
  running a five-phase operations doctrine, orchestrated by the ADK Runner.
- **Gemini 3** (`gemini-3-flash-preview`): the reasoning engine — severity judgment,
  multilingual dedupe, resource sizing, and the human-readable sitrep.
- **MongoDB MCP server**: the agent's *only* hands. Every read and write is an MCP
  tool call (`find`, `aggregate` with `$geoNear`, `insert-many`, `update-many`)
  against MongoDB Atlas — least-privilege filtered so the agent can never delete or
  drop. The MCP server is spawned over stdio by ADK's native `McpToolset`.
- **MongoDB Atlas**: source of truth — reports, shelters, depots, assignments,
  sitreps, with 2dsphere geo-indexes powering the matching.
- **Cloud Run**: single container (Python + Node for the MCP server) serving the
  FastAPI control plane and the dependency-free Leaflet ops console.

### Challenges
Making an agent *trustworthy enough to act*: we solved it with least-privilege MCP
tool filtering (no delete/drop), verify-before-write doctrine (read depot stock
before decrementing; never go negative), a journaled activity feed for human
oversight, and bounded execution (cycles run on demand with a hard time budget).

### Accomplishments
A real agent that *does* things: in a single cycle it performs 20+ MCP tool calls,
merges multilingual duplicates, and mutates live Atlas data you can watch change on
a map. No mock data, no canned demo path — judges can submit their own SOS on the
hosted URL and watch it get dispatched.

### What we learned
MCP turns "an LLM with a database" into "an operator with hands" — the tool-filter
boundary is where safety policy lives, and an explicit numbered doctrine in the
instruction beats freeform multi-agent choreography for reliability under pressure.

### What's next
WhatsApp/SMS ingestion (the real SOS channel in India), Atlas Vector Search for
semantic dedupe at scale, multi-city federation, and NDMA control-room pilots.
