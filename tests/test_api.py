"""API tests. Need a reachable MongoDB (local Docker or Atlas) via
MDB_MCP_CONNECTION_STRING; the agent/LLM is NOT exercised here.

Run: pytest tests/ -q
"""

import os

os.environ.setdefault("MDB_MCP_CONNECTION_STRING", "mongodb://localhost:27017/")

from fastapi.testclient import TestClient

from app import seed
from app.server import app

client = TestClient(app)


def setup_module():
    seed.run()


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_state_shape():
    r = client.get("/api/state")
    body = r.json()
    assert r.status_code == 200
    assert body["degraded"] is False
    assert len(body["reports"]) == 11
    assert len(body["shelters"]) == 8
    assert len(body["depots"]) == 3
    assert all("_id" in s and isinstance(s["_id"], str) for s in body["shelters"])
    assert body["agent"]["running"] is False


def test_sos_intake_and_validation():
    ok = client.post(
        "/api/sos",
        json={"description": "Family on roof, water rising", "people_count": 4,
              "lat": 19.07, "lng": 72.88, "locality": "Kurla"},
    )
    assert ok.status_code == 200 and ok.json()["ok"] is True

    bad_geo = client.post(
        "/api/sos",
        json={"description": "test", "people_count": 1, "lat": 999, "lng": 72.88},
    )
    assert bad_geo.status_code == 422

    bad_people = client.post(
        "/api/sos",
        json={"description": "test", "people_count": 0, "lat": 19.0, "lng": 72.88},
    )
    assert bad_people.status_code == 422

    too_short = client.post(
        "/api/sos", json={"description": "ab", "people_count": 1, "lat": 19.0, "lng": 72.88}
    )
    assert too_short.status_code == 422


def test_new_sos_visible_in_state():
    before = len(client.get("/api/state").json()["reports"])
    client.post(
        "/api/sos",
        json={"description": "Stranded near station", "people_count": 2,
              "lat": 19.01, "lng": 72.84},
    )
    after = client.get("/api/state").json()["reports"]
    assert len(after) == before + 1
    newest = after[0]
    assert newest["status"] == "new" and newest["severity"] is None


def test_events_feed():
    r = client.get("/api/events?after=0")
    assert r.status_code == 200
    assert isinstance(r.json()["events"], list)


def test_dashboard_served():
    r = client.get("/")
    assert r.status_code == 200
    assert "SAHAYA" in r.text
