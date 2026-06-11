# DEMO_SCRIPT.md — 3-minute video, shot by shot

Record at 1080p, screen + voiceover (no face needed). Use the **deployed Cloud Run
URL**, browser full-screen, dashboard pre-loaded with the seeded scenario (run
`python -m app.seed` just before recording so all reports show "new").
Practice once; record in one take if possible. Talk calmly — the agent provides the drama.

## 0:00–0:20 — The problem (over the loaded dashboard, do not click anything)
> "Every monsoon, Mumbai's flood control rooms drown in thousands of SOS messages —
> calls, WhatsApp, social media. Humans must triage them, spot duplicates, find
> shelters with space, and dispatch boats from depots with limited stock. Minutes of
> coordination latency cost lives. This is Sahaya — an autonomous flood-response
> operations agent."

Gesture (cursor) over: the SOS markers, a shelter popup, a depot popup showing inventory.

## 0:20–0:40 — The stack (stay on screen, point at the activity panel)
> "Sahaya is built with Google Cloud Agent Builder — an ADK agent reasoning with
> Gemini 3. Its only hands are MongoDB's MCP server: every read and write you're
> about to see is the agent calling MCP tools against a live Atlas database.
> It can insert and update — it is not allowed to delete anything."

## 0:40–2:10 — The agent works (the core of the video)
Click **▶ RUN OPS CYCLE**. Narrate what is actually happening as the feed streams:
> "Watch the activity feed. The agent finds eleven unprocessed reports… it's triaging —
> note these three: the same trapped family in Kurla reported three different ways, one
> in Hinglish. It marks two as duplicates and keeps one P0… Now geo-matching — geoNear
> aggregations find the nearest shelter with free capacity and the nearest depot with
> boats in stock… and it dispatches: assignment orders written, depot inventory
> decremented, shelter occupancy updated — every marker turning green is a real
> database mutation happening right now."

When the cycle ends, click a depot popup (inventory is visibly lower), then scroll
the Dispatch Orders panel, then read one line of the sitrep aloud.

## 2:10–2:40 — Live SOS (proves it's not canned)
Click the map somewhere flooded-looking, click **⚠ Report SOS**, type:
"Pregnant woman trapped on 1st floor, water rising, Bandra East", people: 3. Send.
Click **▶ RUN OPS CYCLE** again.
> "A new SOS comes in live — the agent triages it P0, finds the nearest shelter with
> space, and dispatches a boat with medics. End to end, no human in the loop — but
> every action journaled, reversible, and bounded for human oversight."

## 2:40–3:00 — Close (dashboard wide shot)
> "Sahaya: Gemini 3 for judgment, Agent Builder for orchestration, MongoDB MCP for
> action. Real writes, real geo-queries, deployed on Cloud Run. Coordination is the
> bottleneck in every disaster — Sahaya removes it. Thank you."

## Upload
YouTube, unlisted is fine. Title: "Sahaya — Autonomous Flood-Response Agent (Google
Cloud Rapid Agent Hackathon)". Paste URL into Devpost form.
