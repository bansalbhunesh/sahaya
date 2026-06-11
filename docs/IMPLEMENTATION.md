# IMPLEMENTATION.md — build plan (compressed for a 5-hour runway)

Each milestone is independently demoable. Times are IST, June 11–12 2026.
Hard deadline: **submit on Devpost by 2:30 AM IST June 12** (2:00 PM PT June 11).

## M1 — Agent runs locally (target 22:30)
- venv + google-adk + deps installed; Node 24 already present
- `app/agent.py` (LlmAgent + McpToolset→mongodb-mcp-server), `app/db.py`,
  `app/seed.py`, `app/server.py`, `web/` dashboard
- Needs from user: **GOOGLE_API_KEY**, **MDB_MCP_CONNECTION_STRING**
- Demoable: localhost dashboard, seed → run cycle → assignments appear

## M2 — Smoke-tested end to end (target 23:30)
- `python -m app.smoke`: seed → one cycle → assert ≥1 assignment, inventory
  decremented, sitrep exists; fix what breaks
- Demoable: reliable repeated cycles, SOS submitted live gets dispatched

## M3 — Deployed (target 00:30)
- Dockerfile (python:3.12-slim + Node 22), `.dockerignore`
- gcloud installed; user runs `gcloud auth login`; `gcloud run deploy --source`
- Demoable: **hosted URL** — the submission artifact

## M4 — Public repo (target 00:45)
- GitHub repo `sahaya` via PAT, public, MIT LICENSE at root (About shows license)
- README with architecture diagram + judge-reproducible quickstart

## M5 — Submission package (target 01:30; buffer to 02:15)
- Demo video: user records per `docs/DEMO_SCRIPT.md` (~3 min), uploads (YouTube
  unlisted is fine for Devpost)
- Devpost form: text from `docs/SUBMISSION.md`; track = MongoDB; hosted URL; repo URL

## Submission checklist
- [ ] Hosted URL live (Cloud Run) and clickable by judges
- [ ] Public repo, MIT license visible in GitHub About
- [ ] ≤3-min video, English, shows the live deployed app (not localhost if possible)
- [ ] Devpost form: MongoDB track selected, video URL, repo URL, hosted URL, description
- [ ] Reproducibility: README quickstart works from a fresh clone (.env.example)

## Scope cuts, pre-authorized (in order, if time runs out)
1. SSE event stream → poll `/api/events`
2. Cloud Run min-instances/custom domain niceties
3. Sitrep panel styling
4. NEVER cut: seed → run → live dashboard mutation loop, deployed URL, license, video
