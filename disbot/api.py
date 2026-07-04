from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .simulator import simulator


class DeviceStatusUpdate(BaseModel):
    status: bool


app = FastAPI(title="disbot Office Monitor", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).resolve().parents[1] / "web"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def dashboard() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/devices")
def devices() -> list[dict]:
    return simulator.devices()


@app.get("/api/summary")
def summary() -> dict:
    return simulator.summary()


@app.get("/api/rooms/{room_id}")
def room(room_id: str) -> dict:
    devices_for_room = simulator.room_devices(room_id)
    if not devices_for_room:
        raise HTTPException(status_code=404, detail="Unknown room")
    return {"room_id": devices_for_room[0]["room_id"], "room_name": devices_for_room[0]["room_name"], "devices": devices_for_room}


@app.get("/api/alerts")
def alerts() -> list[dict]:
    return simulator.alerts()


@app.post("/api/devices/{device_id}/toggle")
def toggle_device(device_id: str) -> dict:
    try:
        return simulator.toggle(device_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown device") from exc


@app.patch("/api/devices/{device_id}")
def update_device(device_id: str, payload: DeviceStatusUpdate) -> dict:
    try:
        return simulator.set_status(device_id, payload.status)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown device") from exc
