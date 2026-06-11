"""Reset and seed the Mumbai monsoon scenario. Destructive on db 'sahaya'.

Run: python -m app.seed
"""

import datetime
import logging
import random

from pymongo import GEOSPHERE

from . import db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
log = logging.getLogger("sahaya.seed")

NOW = datetime.datetime.now(datetime.timezone.utc)


def minutes_ago(m: int) -> datetime.datetime:
    return NOW - datetime.timedelta(minutes=m)


# [lng, lat] — GeoJSON order
SHELTERS = [
    {"name": "Andheri Sports Complex", "capacity": 800, "coords": [72.8336, 19.1197]},
    {"name": "Dadar Catering College Hall", "capacity": 350, "coords": [72.8410, 19.0178]},
    {"name": "BKC MMRDA Grounds Camp", "capacity": 1200, "coords": [72.8656, 19.0653]},
    {"name": "Sion Municipal School No. 6", "capacity": 300, "coords": [72.8643, 19.0390]},
    {"name": "Kurla Nehru Nagar School", "capacity": 250, "coords": [72.8822, 19.0726]},
    {"name": "Chembur Gymkhana Hall", "capacity": 400, "coords": [72.8957, 19.0522]},
    {"name": "Goregaon NESCO Grounds", "capacity": 1500, "coords": [72.8526, 19.1538]},
    {"name": "Byculla YMCA Centre", "capacity": 200, "coords": [72.8311, 18.9793]},
]

DEPOTS = [
    {
        "name": "NDRF Depot Worli",
        "coords": [72.8170, 19.0176],
        "inventory": {"boats": 14, "rescue_teams": 10, "life_jackets": 400, "medical_kits": 120, "food_packets": 5000},
    },
    {
        "name": "BMC Depot Andheri East",
        "coords": [72.8697, 19.1136],
        "inventory": {"boats": 8, "rescue_teams": 6, "life_jackets": 250, "medical_kits": 80, "food_packets": 3500},
    },
    {
        "name": "Civil Defence Depot Ghatkopar",
        "coords": [72.9081, 19.0790],
        "inventory": {"boats": 6, "rescue_teams": 5, "life_jackets": 180, "medical_kits": 60, "food_packets": 2500},
    },
]

REPORTS = [
    # P0 cluster — Kurla: same building reported three ways (dedupe test)
    {"description": "Water entering 2nd floor, Shivaji Nagar chawl building 4, Kurla West. 3 children and grandmother trapped on roof. Water rising fast!", "people_count": 6, "locality": "Kurla West", "contact": "+91 98XXXX1201", "coords": [72.8790, 19.0701], "mins": 42},
    {"description": "URGENT bldg no 4 shivaji nagar kurla — family stuck on terrace, paani badh raha hai, bachche hain", "people_count": 6, "locality": "Kurla West", "contact": "+91 98XXXX3344", "coords": [72.8792, 19.0703], "mins": 38},
    {"description": "Forwarded WhatsApp: Building 4 Shivaji Nagar Kurla roof pe log fase hain, koi rescue bhejo", "people_count": 5, "locality": "Kurla West", "contact": "", "coords": [72.8789, 19.0699], "mins": 31},
    # P0 — Sion hospital basement
    {"description": "Sion hospital ke paas basement clinic mein paani bhar gaya, 2 patients on oxygen cannot move, need boat and medics NOW", "people_count": 4, "locality": "Sion", "contact": "+91 99XXXX8090", "coords": [72.8620, 19.0411], "mins": 25},
    # P1 — stranded groups
    {"description": "Around 30 people stranded on Andheri subway footbridge, water chest deep below, safe for now but cannot get down", "people_count": 30, "locality": "Andheri East", "contact": "+91 98XXXX5566", "coords": [72.8485, 19.1190], "mins": 55},
    {"description": "School bus stuck near Milan subway, 18 students inside, driver says water at tyre level and rising slowly", "people_count": 20, "locality": "Santacruz", "contact": "+91 97XXXX2299", "coords": [72.8430, 19.0790], "mins": 19},
    {"description": "Elderly couple on 1st floor, Hindmata cinema area Dadar, water in ground floor, need evacuation when possible", "people_count": 2, "locality": "Dadar", "contact": "+91 98XXXX7711", "coords": [72.8447, 19.0070], "mins": 64},
    # P2 — supplies
    {"description": "Chembur Tilak Nagar society 200 families cut off since morning, need drinking water and food packets, no immediate danger", "people_count": 120, "locality": "Chembur", "contact": "+91 96XXXX4455", "coords": [72.8940, 19.0550], "mins": 90},
    {"description": "Diabetic patient needs insulin, Byculla Rani Baug area, roads waterlogged, 1 day supply left", "people_count": 1, "locality": "Byculla", "contact": "+91 95XXXX6677", "coords": [72.8330, 18.9780], "mins": 47},
    # P3 — info/minor
    {"description": "Tree fallen on parked autos near Goregaon station east, no injuries, blocking lane", "people_count": 1, "locality": "Goregaon", "contact": "", "coords": [72.8500, 19.1640], "mins": 110},
    {"description": "Is the Sion-Panvel highway open? Planning to move family to Navi Mumbai", "people_count": 4, "locality": "Sion", "contact": "", "coords": [72.8700, 19.0370], "mins": 12},
]


def run() -> None:
    d = db.db()
    for name in ("reports", "shelters", "depots", "assignments", "sitreps"):
        d.drop_collection(name)
        log.info('{"event":"dropped","collection":"%s"}', name)

    d.shelters.insert_many(
        {
            "name": s["name"],
            "capacity": s["capacity"],
            "occupancy": random.randint(0, s["capacity"] // 10),
            "amenities": ["water", "food", "first-aid"],
            "location": {"type": "Point", "coordinates": s["coords"]},
        }
        for s in SHELTERS
    )
    d.depots.insert_many(
        {
            "name": x["name"],
            "inventory": x["inventory"],
            "location": {"type": "Point", "coordinates": x["coords"]},
        }
        for x in DEPOTS
    )
    d.reports.insert_many(
        {
            "description": r["description"],
            "people_count": r["people_count"],
            "locality": r["locality"],
            "contact": r["contact"],
            "location": {"type": "Point", "coordinates": r["coords"]},
            "status": "new",
            "severity": None,
            "source": "seed-control-room",
            "created_at": minutes_ago(r["mins"]),
        }
        for r in REPORTS
    )
    for coll in ("reports", "shelters", "depots"):
        d[coll].create_index([("location", GEOSPHERE)])
    log.info(
        '{"event":"seeded","reports":%d,"shelters":%d,"depots":%d}',
        d.reports.count_documents({}),
        d.shelters.count_documents({}),
        d.depots.count_documents({}),
    )


if __name__ == "__main__":
    run()
