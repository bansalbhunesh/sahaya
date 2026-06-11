"""Sahaya web service: ops-console dashboard + agent control plane."""

import datetime
import logging
import pathlib

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import db
from .cycle import CYCLE, EVENTS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
log = logging.getLogger("sahaya.server")

app = FastAPI(title="Sahaya", version="1.0.0")

WEB_DIR = pathlib.Path(__file__).resolve().parent.parent / "web"


def _jsonable(doc: dict) -> dict:
    out = {}
    for k, v in doc.items():
        if k == "_id":
            out["_id"] = str(v)
        elif isinstance(v, datetime.datetime):
            out[k] = v.isoformat()
        elif isinstance(v, dict):
            out[k] = _jsonable(v)
        else:
            out[k] = v
    return out


class SosReport(BaseModel):
    description: str = Field(min_length=3, max_length=2000)
    people_count: int = Field(ge=1, le=500, default=1)
    contact: str = Field(default="", max_length=120)
    locality: str = Field(default="", max_length=120)
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.get("/api/state")
def state():
    try:
        d = db.db()
        return {
            "degraded": False,
            "reports": [_jsonable(r) for r in d.reports.find().sort("created_at", -1).limit(150)],
            "shelters": [_jsonable(s) for s in d.shelters.find()],
            "depots": [_jsonable(x) for x in d.depots.find()],
            "assignments": [
                _jsonable(a) for a in d.assignments.find().sort("created_at", -1).limit(50)
            ],
            "sitreps": [_jsonable(s) for s in d.sitreps.find().sort("created_at", -1).limit(3)],
            "agent": {"running": CYCLE.running, "last_error": CYCLE.last_error},
        }
    except Exception as exc:
        log.error('{"event":"state_failed","error":"%s"}', exc)
        return JSONResponse(status_code=200, content={"degraded": True, "error": str(exc)})


@app.post("/api/sos")
def sos(report: SosReport):
    doc = {
        "description": report.description,
        "people_count": report.people_count,
        "contact": report.contact,
        "locality": report.locality,
        "location": {"type": "Point", "coordinates": [report.lng, report.lat]},
        "status": "new",
        "severity": None,
        "source": "citizen-web",
        "created_at": datetime.datetime.now(datetime.timezone.utc),
    }
    result = db.db().reports.insert_one(doc)
    log.info('{"event":"sos_received","id":"%s"}', result.inserted_id)
    return {"ok": True, "id": str(result.inserted_id)}


@app.post("/api/run")
async def run_cycle():
    if CYCLE.running:
        raise HTTPException(status_code=409, detail="A cycle is already running")
    try:
        result = await CYCLE.run_cycle()
        return {"ok": True, **result}
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Agent cycle failed: {exc}")


@app.get("/api/events")
def events(after: int = 0):
    return {"events": [e for e in EVENTS if e["seq"] > after]}


@app.get("/")
def index():
    return FileResponse(WEB_DIR / "index.html")


app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")
