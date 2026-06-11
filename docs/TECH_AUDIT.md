# TECH_AUDIT.md — engineering-level: ideal winner's codebase vs. ours

Honest code review of Sahaya against what a top-tier winning team ships. Done
2026-06-11 ~23:00 IST. ✅ = we match/beat. 🟡 = gap, fixed tonight. 🔴 = gap,
consciously accepted (with reasoning).

## 1. Agent core

| Aspect | Ideal winner | Sahaya | Verdict |
|---|---|---|---|
| Orchestration | ADK Runner, clean session mgmt | ADK Runner + InMemorySessionService, fresh session per cycle (DB *is* the durable memory) | ✅ |
| Planning structure | Explicit, auditable plan | Five-phase numbered doctrine in `OPS_PROTOCOL`; every step journaled | ✅ |
| Model config | Tuned: low temperature for ops, thinking budget | **Temperature unset** (DESIGN.md promised 0.2) | 🟡 fixed: `GenerateContentConfig(temperature=0.2)` |
| Runaway protection | Hard cap on LLM calls + wall-clock budget | Wall-clock 240s ✓, **no LLM-call cap** | 🟡 fixed: `RunConfig(max_llm_calls=40)` |
| Multi-agent | Sometimes (SalesShortcut was multi-agent) | Single agent, multi-phase | 🔴 accepted: sequential domain; one auditable doctrine beats choreography under deadline; argued in DESIGN.md |
| Structured outputs | Schema-validated writes | Schemas defined in instruction; MongoDB is schemaless; dashboard tolerates missing fields | 🔴 accepted: validation at intake (`pydantic` on /api/sos) where input is untrusted |

## 2. MCP / partner-tech depth

| Aspect | Ideal winner | Sahaya | Verdict |
|---|---|---|---|
| MCP as actuator | Load-bearing | **Sole** write path for the agent; architecture enforces it | ✅ better than typical |
| Least privilege | Rarely done | `tool_filter` allowlist; no delete/drop/admin tools reachable | ✅ differentiator |
| Query sophistication | Basic CRUD | `$geoNear` geospatial matching, batched `update-many`, `$inc` inventory math, 2dsphere indexes | ✅ |
| Atlas Search / Vector Search | The flex move | Not used | 🔴 accepted: embeddings + index build on deadline night = demo risk; roadmap'd in submission |

## 3. Reliability engineering

| Aspect | Ideal winner | Sahaya | Verdict |
|---|---|---|---|
| Concurrency | Guarded | asyncio lock + 409 on concurrent cycles | ✅ |
| Partial failure | Consistent state | Ordered writes (assignment → inventory → status); verify-before-write; re-run safe because processed reports leave `new` status | ✅ |
| Idempotency | Exactly-once-ish | At-most-once per report via status transitions; no idempotency keys on assignments | 🟡 acceptable: re-dispatch impossible once status != new |
| Graceful degradation | Yes | MCP spawn failure → 503 + "agent offline"; Atlas down → `degraded` banner; LLM error → journaled, state consistent | ✅ |
| LLM fallback | Rarely | Dual model path (native Gemini / OpenAI-compatible gateway) behind env flags | ✅ |

## 4. Observability

| Aspect | Ideal winner | Sahaya | Verdict |
|---|---|---|---|
| Action audit trail | Logs | **User-facing live journal** of every tool call/thought/error (also the demo centerpiece) | ✅ better |
| Structured logging | JSON logs | Single-line JSON-ish events w/ logger names | ✅ adequate |
| Tracing (Cloud Trace) | Sometimes | Not enabled | 🔴 accepted: zero judge-visible value in 3-min demo; config risk |

## 5. Testing & reproducibility

| Aspect | Ideal winner | Sahaya | Verdict |
|---|---|---|---|
| E2E test | Sometimes | `python -m app.smoke`: seed → cycle → assert real mutations | ✅ |
| Unit/API tests | Yes | **None** | 🟡 fixed: `tests/test_api.py` (healthz, state, SOS validation, events, static) |
| Judge reproducibility | Clone-and-run | README 5-min quickstart, `.env.example`, seed script, Dockerfile | ✅ |
| CI | Sometimes | None | 🔴 accepted: zero value before deadline |

## 6. Security

| Aspect | Ideal winner | Sahaya | Verdict |
|---|---|---|---|
| Secrets | Env vars, never committed | ✓ (.env gitignored; Cloud Run env vars) | ✅ |
| Input validation | Yes | pydantic bounds on /api/sos (lengths, ranges, geo bounds) | ✅ |
| Agent blast radius | Rarely considered | No-delete tool filter + read-only dashboard client separation | ✅ differentiator |
| Public /api/run | Auth'd | Open (single concurrent cycle + budget caps abuse) | 🔴 accepted: judges must be able to press the button |

## Bottom line

Our engineering story is **stronger than the median winner** on the dimensions
judges can actually see (actuator-only-via-MCP, least privilege, live audit
journal, graceful failure, dual model path) and consciously thinner on invisible
ones (CI, tracing, vector search). The three real code gaps found — temperature,
LLM-call cap, API tests — are fixed in this commit. Remaining existential items
are operational, not code: working Gemini key, Cloud Run deploy, video.
