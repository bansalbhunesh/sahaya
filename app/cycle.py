"""Runs one agent ops cycle and journals every event to the activity feed."""

import asyncio
import datetime
import logging
import uuid
from collections import deque

from google.adk.agents.run_config import RunConfig
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agent import build_agent

log = logging.getLogger("sahaya.cycle")

CYCLE_BUDGET_SECONDS = 240

# Activity feed: list of {seq, ts, kind, text} consumed by the dashboard.
EVENTS: deque = deque(maxlen=500)
_seq = 0


def _emit(kind: str, text: str) -> None:
    global _seq
    _seq += 1
    EVENTS.append(
        {
            "seq": _seq,
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "kind": kind,
            "text": text[:2000],
        }
    )


def _describe_args(args: dict) -> str:
    if not isinstance(args, dict):
        return ""
    parts = []
    for key in ("collection", "database"):
        if key in args:
            parts.append(f"{key}={args[key]}")
    if "filter" in args:
        parts.append(f"filter={str(args['filter'])[:120]}")
    if "documents" in args:
        parts.append(f"{len(args['documents'])} doc(s)")
    if "update" in args:
        parts.append(f"update={str(args['update'])[:120]}")
    if "pipeline" in args:
        parts.append(f"pipeline={str(args['pipeline'])[:160]}")
    return " ".join(parts)


class CycleRunner:
    """Owns the ADK Runner; one ops cycle at a time."""

    def __init__(self) -> None:
        self._runner: Runner | None = None
        self._lock = asyncio.Lock()
        self.running = False
        self.last_error: str | None = None

    def _ensure_runner(self) -> Runner:
        if self._runner is None:
            self._runner = Runner(
                agent=build_agent(),
                app_name="sahaya",
                session_service=InMemorySessionService(),
            )
        return self._runner

    async def run_cycle(self) -> dict:
        if self._lock.locked():
            raise RuntimeError("cycle_already_running")
        async with self._lock:
            self.running = True
            self.last_error = None
            try:
                return await asyncio.wait_for(
                    self._run_cycle_inner(), timeout=CYCLE_BUDGET_SECONDS
                )
            except Exception as exc:  # surface every failure in the feed
                self.last_error = f"{type(exc).__name__}: {exc}"
                _emit("error", f"Cycle failed: {self.last_error}")
                log.error('{"event":"cycle_failed","error":"%s"}', self.last_error)
                raise
            finally:
                self.running = False

    async def _run_cycle_inner(self) -> dict:
        runner = self._ensure_runner()
        user_id = "commander"
        session = await runner.session_service.create_session(
            app_name="sahaya", user_id=user_id, session_id=f"cycle-{uuid.uuid4().hex[:8]}"
        )
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _emit("cycle", "OPS CYCLE started - agent taking control")
        message = types.Content(
            role="user",
            parts=[types.Part(text=f"RUN ONE OPS CYCLE. Current time: {now}")],
        )
        final_text = ""
        tool_calls = 0
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=message,
            # Hard cap alongside the wall-clock budget: a confused model can
            # never spiral into an unbounded tool loop.
            run_config=RunConfig(max_llm_calls=40),
        ):
            content = getattr(event, "content", None)
            for part in getattr(content, "parts", None) or []:
                fc = getattr(part, "function_call", None)
                if fc is not None:
                    tool_calls += 1
                    _emit("tool", f">> {fc.name} {_describe_args(fc.args or {})}")
                fr = getattr(part, "function_response", None)
                if fr is not None:
                    _emit("result", f"OK {fr.name} responded")
                text = getattr(part, "text", None)
                if text and text.strip():
                    if event.is_final_response():
                        final_text = text.strip()
                    else:
                        _emit("thought", text.strip())
        _emit("sitrep", final_text or "Cycle finished with no commander report.")
        _emit("cycle", f"OPS CYCLE complete - {tool_calls} tool actions")
        log.info('{"event":"cycle_done","tool_calls":%d}', tool_calls)
        return {"final": final_text, "tool_calls": tool_calls}


CYCLE = CycleRunner()
