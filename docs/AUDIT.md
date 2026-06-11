# AUDIT.md — Ideal winner vs. Sahaya (gap analysis, 2026-06-11 ~22:40 IST)

Sources: Devpost judge advice posts, ADK Hackathon 2025 winners (SalesShortcut—an
autonomous multi-agent SDR system—plus Edu.AI, Energy Agent AI, GreenOps), GKE
hackathon winner pattern. Synthesized profile of what takes 1st in a partner track.

## The ideal winning submission

1. **Live hosted URL judges can use in 30 seconds** — no setup, preloaded data, a
   button that makes the agent visibly do something.
2. **Video with a story arc** — judges call the video the #1 signal of effort.
   ~60% story/explanation, 40% live demo, voiceover, no dead air, ends on impact.
3. **Devpost page that sells** — embedded screenshots/GIF, architecture diagram,
   markdown-formatted description, explicit mapping to the four judging criteria.
4. **Partner tech load-bearing, not garnish** — for MongoDB: geo-queries,
   aggregations, the MCP server as the agent's sole actuator. Winners exploit a
   partner feature competitors won't bother with.
5. **Visible multi-step autonomy** — the agent plans, acts, mutates real state,
   recovers from constraints (full shelter, short inventory), and reports.
6. **Real-world credibility** — a problem the judge already believes in; domain
   detail (Hinglish SOS texts, NDRF depots) that signals the builders know the space.
7. **Safety/oversight engineering** — the brief says "under your oversight"; winners
   make human-in-the-loop a designed feature, not an apology.
8. **Reproducible repo** — visible license, quickstart that works, clean structure.

## Scorecard: Sahaya today

| Dimension | Ideal | Ours | Gap |
|---|---|---|---|
| Hosted URL | Click → live agent | NOT DEPLOYED yet | **P0 — blocked on gcloud auth + Gemini key** |
| Working agent loop | Proven E2E | All parts proven separately; full loop unproven (key died) | **P0 — needs AIza key** |
| Video | Story arc, polished | Script ready (DEMO_SCRIPT.md); not recorded | **P0 — user records after deploy** |
| Devpost page | Images, GIF, diagram, criteria mapping | Text strong; no images, no diagram, no criteria section | **P1 — fixable now** |
| Architecture diagram | Clean image | ASCII only | **P1 — fixable now** |
| README polish | Badges, visuals | Screenshot ✓, no badges | P1 |
| MongoDB depth | Geo + aggregations + exclusive-actuator story | $geoNear ✓, write-tools ✓, least-privilege story ✓ | Minor — tell it louder |
| Multi-step autonomy | Visible planning + recovery | 5-phase doctrine + live activity feed ✓ | None — demo it well |
| Domain credibility | Real texture | Hinglish SOS, real Mumbai geography, NDRF/BMC depots ✓ | None |
| Oversight story | Designed-in | Feed + no-delete + bounded cycles + sitrep-for-commander ✓ | None — say it in video |
| Repo reproducibility | 5-min quickstart | ✓ (README), MIT detected ✓ | None |

## Verdict

Sahaya's *substance* already matches the winner profile — the two existential gaps
are operational (deploy + working key), and the remaining real gap is **packaging**
(images, diagram, explicit criteria mapping). Multi-agent conversion was considered
and rejected: single-agent five-phase doctrine is more reliable tonight and is an
articulated design choice (DESIGN.md), not a shortcut.

## Plan (prioritized, time-boxed)

**P0 — existential, in order (critical path untouched by everything below):**
1. User: free AI Studio key → full smoke test (~15 min after key)
2. User: `gcloud auth login` → deploy to Cloud Run (~15 min after auth)
3. Re-seed Atlas → verify hosted URL cold → user records video → Devpost form by 02:15 IST

**P1 — packaging, do now while blocked (no credentials needed):**
4. Architecture diagram as PNG (render HTML → headless screenshot) into README + Devpost
5. SUBMISSION.md: add "How we hit each judging criterion" section
6. README: shields.io badges (Gemini 3, ADK, MongoDB MCP, Cloud Run, MIT)
7. Devpost description: embed dashboard screenshot + diagram (images must be on a
   public URL — use raw.githubusercontent links once pushed)

**P2 — only if P0 done with ≥45 min spare:**
8. Animated GIF of an ops cycle for the Devpost page
9. Demo polish: pre-position map, rehearse one full cycle on the hosted URL

**Explicitly rejected tonight:** Atlas Vector Search semantic dedupe (needs
embeddings + index build time; mentioned as roadmap), multi-agent refactor,
WhatsApp ingestion. All risk the demo-critical path for marginal judge-visible gain.
