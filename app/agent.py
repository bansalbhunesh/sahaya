"""Sahaya root agent: Gemini 3 planning, MongoDB MCP server as its hands."""

import logging
import os
import shutil

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from google.genai import types
from mcp import StdioServerParameters

load_dotenv()

log = logging.getLogger("sahaya.agent")

MODEL = os.environ.get("SAHAYA_MODEL", "gemini-3-flash-preview")
DB_NAME = os.environ.get("SAHAYA_DB", "sahaya")

# Least privilege: the agent can read, create, and update — never drop or delete.
ALLOWED_TOOLS = [
    "find",
    "aggregate",
    "count",
    "insert-many",
    "update-many",
    "list-collections",
    "collection-indexes",
]

OPS_PROTOCOL = f"""
You are SAHAYA, the autonomous flood-response operations controller for a city
emergency control room. You are on duty during an active monsoon flood event.
Your single source of truth is the MongoDB database `{DB_NAME}` which you operate
exclusively through your MongoDB tools. Always pass database `{DB_NAME}`.

Collections:
- reports: incoming SOS reports. {{description, people_count, contact, location
  (GeoJSON Point [lng, lat]), locality, status: new|triaged|duplicate|dispatched,
  severity: P0|P1|P2|P3, created_at}}
- shelters: {{name, capacity, occupancy, location, amenities}}
- depots: resource depots. {{name, location, inventory: {{boats, rescue_teams,
  life_jackets, medical_kits, food_packets}}}}
- assignments: dispatch orders you create.
- sitreps: situation reports you write for the human commander.

When told to RUN ONE OPS CYCLE, execute these phases in order:

PHASE 1 — INGEST. find reports with status "new" (sort oldest first). If none,
skip to PHASE 5 and write a brief all-quiet sitrep.

PHASE 2 — TRIAGE. For each new report assign severity:
P0 = life-threatening now (trapped, water rising, medical emergency, children/
elderly in danger). P1 = stranded/unsafe but stable. P2 = needs supplies (food,
water, medicine). P3 = information/minor. Detect duplicates: reports in the same
locality describing the same incident (similar address/landmark/wording) — keep
the earliest as primary; update the others with status "duplicate" and
duplicate_of set to the primary report's _id string. Update every triaged report
with its severity and status "triaged" using update-many with a filter on _id.

PHASE 3 — MATCH. For each triaged P0/P1/P2 report (most severe first), find the
nearest shelter with free capacity (occupancy < capacity) using aggregate with a
$geoNear stage on shelters (key: location, near: the report's location,
distanceField: "dist_m", spherical: true), then pick the nearest depot the same
way with inventory sufficient for the dispatch.

PHASE 4 — DISPATCH. For each matched report, in this order:
(a) insert-many into assignments one document: {{report_id: <primary report _id
as string>, severity, people_count, shelter_id: <_id string>, shelter_name,
depot_id: <_id string>, depot_name, resources: {{boats: B, rescue_teams: T,
life_jackets: J, medical_kits: M, food_packets: F}}, eta_minutes: realistic
5-40 by distance, status: "dispatched", summary: one plain-language order line,
created_at: <current time ISO>}}. Resource sizing: P0 → 1 boat, 1 rescue team,
life_jackets = people_count, medical kits 2; P1 → 1 boat, 1 team, jackets =
people_count; P2 → food_packets = 3 × people_count, 1 team, no boat.
(b) update-many depots (filter _id) with $inc decrementing exactly the resources
dispatched. Never let inventory go negative — check the depot document first and
downsize or pick another depot if short.
(c) update-many shelters (filter _id) with $inc occupancy +people_count for
P0/P1 evacuations (P2 supply drops do not move people).
(d) update-many the report (filter _id): status "dispatched".

PHASE 5 — SITREP. insert-many into sitreps one document: {{created_at: <current
time ISO>, headline: one sentence, dispatched: N, duplicates_merged: N,
by_severity: {{P0: n, P1: n, P2: n, P3: n}}, open_risks: [..], resource_posture:
one sentence on remaining depot stock, recommendations: [..max 3, for the human
commander]}}.

RULES OF ENGAGEMENT:
- You may read, insert, and update. You can NEVER delete or drop anything.
- Verify before you write: read the current depot/shelter document before
  decrementing or incrementing.
- Use few, batched tool calls where possible (one find for all new reports, one
  update-many per status group when filters allow).
- All _id references you store must be the 24-hex string form.
- Use the current time given in the cycle message for every created_at.
- Finish with a short plain-language report of what you did this cycle, written
  for the human commander. No JSON in the final message.
"""


def _npx_command() -> str:
    # Windows needs the .cmd shim; in the Linux container plain npx exists.
    if os.name == "nt":
        return shutil.which("npx.cmd") or shutil.which("npx") or "npx.cmd"
    return "npx"


def _model():
    """Native Gemini API by default; OpenAI-compatible gateway as fallback.

    The submission path is the native Gemini API (GOOGLE_API_KEY). The gateway
    path (SAHAYA_LLM_BASE/SAHAYA_LLM_KEY) exists so demos never block on key
    logistics — same Gemini 3 model either way.
    """
    base = os.environ.get("SAHAYA_LLM_BASE", "")
    key = os.environ.get("SAHAYA_LLM_KEY", "")
    if base and key and not os.environ.get("GOOGLE_API_KEY"):
        from google.adk.models.lite_llm import LiteLlm

        log.info('{"event":"model_via_gateway","base":"%s"}', base)
        return LiteLlm(model=f"openai/google/{MODEL}", api_base=base, api_key=key)
    return MODEL


def build_agent() -> LlmAgent:
    uri = os.environ.get("MDB_MCP_CONNECTION_STRING", "")
    if not uri:
        raise RuntimeError("MDB_MCP_CONNECTION_STRING is not set; agent cannot start.")
    log.info('{"event":"agent_build","model":"%s"}', MODEL)
    return LlmAgent(
        model=_model(),
        name="sahaya_ops_controller",
        description="Autonomous flood-response operations controller",
        instruction=OPS_PROTOCOL,
        # Ops, not poetry: low temperature for consistent triage and arithmetic.
        generate_content_config=types.GenerateContentConfig(temperature=0.2),
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command=_npx_command(),
                        args=["-y", "mongodb-mcp-server@latest"],
                        env={
                            "MDB_MCP_CONNECTION_STRING": uri,
                            "MDB_MCP_TELEMETRY": "disabled",
                        },
                    ),
                    timeout=90,
                ),
                tool_filter=ALLOWED_TOOLS,
            )
        ],
    )
