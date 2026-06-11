# RESEARCH.md — Phase 0 Findings & Track Decision

> Compiled 2026-06-11 ~21:15 IST. **Submission deadline: June 11, 2026 2:00 PM PT = June 12, 2:30 AM IST — ~5 hours from compilation.** Research was deliberately compressed; every decision below is optimized for *win probability under that constraint*.

## 1. Hackathon Facts (verified from rapid-agent.devpost.com and /rules)

- **Event**: Google Cloud Rapid Agent Hackathon: Building Agents for Real-World Challenges
- **Submission period**: May 5, 2026 12:00 PM PT → **June 11, 2026 2:00 PM PT**
- **Judging**: June 22 – July 6, 2026. Winners announced ~July 7.
- **Eligibility**: India eligible. Solo entry allowed (teams up to 4).
- **Prizes per partner track**: $5,000 / $3,000 / $2,000 ($60k total across 6 tracks).
- **Hard requirements**:
  - Functional agent powered by **Gemini** + **Google Cloud Agent Builder**
  - Integrates **one Partner MCP server** (Arize, Elastic, Fivetran, GitLab, MongoDB, Dynatrace)
  - **Hosted project URL** (web, Android, or iOS)
  - **Public repo with visible open-source license**
  - **≤3-minute demo video**, English or subtitled
  - Newly created during the contest period; no services that compete with Google Cloud or the chosen partner
- **Judging criteria**: Technological Implementation, Design, Potential Impact, Quality of the Idea
- **Suggested domains**: 2026 World Cup, financial services, brick-and-mortar retail

## 2. Partner Track Evaluation

| Partner | MCP server maturity | Setup cost tonight | Demo "act on systems" potential | Verdict |
|---|---|---|---|---|
| **MongoDB** | Official `mongodb-mcp-server` (npm, stable, 25+ tools incl. `insert-many`, `update-many`, `aggregate`, `create-index`) | Atlas M0 free tier, **no billing**, ~10 min signup; server runs via `npx` with one env var | **Highest** — agent visibly mutates real data; geo queries + aggregations demo beautifully | ✅ **CHOSEN** |
| GitLab | Official MCP in beta; read-heavy surface | gitlab.com free, token setup | Medium (issues/MRs) — but "DevOps agent" is a crowded archetype | ❌ |
| Elastic | Official MCP, solid docs | Elastic Cloud trial (~15 min), serverless setup risk | Search-heavy = answers questions more than acts | ❌ |
| Dynatrace | Official MCP | Requires Dynatrace SaaS tenant trial + data flowing in | Needs observability data to be meaningful — can't fabricate credibly in 5h | ❌ |
| Arize | Phoenix MCP available | Easy locally, but value = LLM observability | Meta/inward-facing demo; weak "real-world challenge" story | ❌ |
| Fivetran | MCP newer | Needs connectors + destination warehouse | Pipeline plumbing is invisible in a 3-min demo | ❌ |

**Decision: MongoDB.** Honest tradeoff: MongoDB likely has the *most* competition of the six. Under normal runway, a contrarian pick (Fivetran/Dynatrace) would maximize odds. With ~5 hours, the dominant variable is **probability of submitting a complete, working, deployed project at all** — MongoDB is the only track whose entire credential + infra chain (free Atlas cluster → npx MCP server → ADK) can be assembled in under 30 minutes with zero billing. A finished 9/10 in a crowded track beats an unfinished 10/10 in an empty one.

## 3. "Built with Agent Builder" — what judges expect

Google Cloud **Agent Builder** is the umbrella for the **Agent Development Kit (ADK)**, Agent Engine, and Agent Garden. The canonical hackathon-compliant shape:

- **ADK (Python)** `LlmAgent` as the agent core — planning, tool orchestration, sessions
- **Gemini 3** as the reasoning model (`gemini-3-flash-preview` / `gemini-3.1-pro-preview` — verified current model IDs as of June 2026)
- **MCP integration** via ADK's first-class `McpToolset` + `StdioConnectionParams` → spawns `npx -y mongodb-mcp-server@latest` with `MDB_MCP_CONNECTION_STRING`
- **Deployment** to Cloud Run (a documented Agent Builder deployment target — satisfies "hosted URL" without competing-cloud risk)

## 4. What separates 1st place from honorable mention (pattern from past Devpost agent hackathons)

1. **Live deployed URL that judges can actually click** — many entries submit localhost videos; a working hosted app is an immediate top-quartile filter.
2. **The agent *does* things** — multi-step plans that mutate real state, visible consequences, not a chat wrapper.
3. **Deep partner integration** — the MCP server must be load-bearing (the agent's hands), not a garnish.
4. **A 3-minute video with a story arc** — problem (15s) → agent autonomously working (2 min, real data, live UI) → impact (30s).
5. **Clean repo** — license visible, README with architecture diagram, one-command reproducibility.

## 5. Chosen concept (Phase 1 output, compressed)

**Sahaya** (Sanskrit: "aid") — an autonomous monsoon flood-response operations agent for Indian cities. See DESIGN.md. Justification against criteria:

- **Quality of Idea**: India loses ~₹1 lakh crore/yr to floods; coordination (not resources) is the bottleneck. Timely — June = monsoon onset. Globally relatable (flooding is universal).
- **Potential Impact**: maps directly to real NDMA/municipal control-room workflows.
- **Technological Implementation**: genuine multi-step autonomy — triage → dedupe → geo-match → dispatch → inventory mutation → sitrep — every step through the MongoDB MCP server against live Atlas data.
- **Design**: live ops-console dashboard (map + agent activity feed) gives the 3-min video its wow arc: SOS reports flood in, the agent visibly clears the board.

Alternates considered and dropped: kirana supply-chain restock agent (weaker urgency arc), 2026 World Cup fan-ops agent (suggested domain = likely overdone).
