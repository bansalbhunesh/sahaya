"""End-to-end smoke test: seed -> one agent cycle -> assert real mutations.

Run: python -m app.smoke
"""

import asyncio
import logging
import sys

from . import db, seed
from .cycle import CYCLE, EVENTS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
log = logging.getLogger("sahaya.smoke")


async def main() -> int:
    seed.run()
    d = db.db()
    depots_before = {x["name"]: x["inventory"] for x in d.depots.find()}

    result = await CYCLE.run_cycle()
    log.info('{"event":"cycle_result","tool_calls":%d}', result["tool_calls"])

    failures = []
    assignments = d.assignments.count_documents({})
    if assignments < 1:
        failures.append("no assignments created")
    if d.sitreps.count_documents({}) < 1:
        failures.append("no sitrep written")
    if d.reports.count_documents({"status": "new"}) == d.reports.count_documents({}):
        failures.append("no report statuses changed")
    inventory_moved = any(
        x["inventory"] != depots_before.get(x["name"]) for x in d.depots.find()
    )
    if not inventory_moved:
        failures.append("no depot inventory decremented")

    print("\n=== ACTIVITY FEED (last 30) ===")
    for e in list(EVENTS)[-30:]:
        print(f"[{e['kind']:7}] {e['text'][:160]}")

    if failures:
        print(f"\nSMOKE FAILED: {failures}")
        return 1
    print(
        f"\nSMOKE PASSED: {assignments} assignments, "
        f"{d.reports.count_documents({'status': 'dispatched'})} dispatched, "
        f"{d.reports.count_documents({'status': 'duplicate'})} duplicates merged"
    )
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
