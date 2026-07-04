from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta
import random
from typing import Iterable

from .models import Device


ROOMS = {
    "drawing": "Drawing Room",
    "work1": "Work Room 1",
    "work2": "Work Room 2",
}

POWER_WATTS = {
    "fan": 60,
    "light": 15,
}


class OfficeSimulator:
    """Deterministic in-memory simulator for the office device layer."""

    def __init__(self, seed: int = 42) -> None:
        self._random = random.Random(seed)
        self._devices = self._build_devices()
        self._last_tick = datetime.now()

    def _build_devices(self) -> dict[str, Device]:
        devices: dict[str, Device] = {}
        now = datetime.now()

        for room_id, room_name in ROOMS.items():
            for index in range(1, 3):
                device_id = f"{room_id}-fan-{index}"
                devices[device_id] = Device(
                    id=device_id,
                    name=f"Fan {index}",
                    type="fan",
                    room_id=room_id,
                    room_name=room_name,
                    status=self._random.choice([True, False]),
                    power_watts=POWER_WATTS["fan"],
                    last_changed=(now - timedelta(minutes=self._random.randint(5, 190))).isoformat(timespec="seconds"),
                )

            for index in range(1, 4):
                device_id = f"{room_id}-light-{index}"
                devices[device_id] = Device(
                    id=device_id,
                    name=f"Light {index}",
                    type="light",
                    room_id=room_id,
                    room_name=room_name,
                    status=self._random.choice([True, False]),
                    power_watts=POWER_WATTS["light"],
                    last_changed=(now - timedelta(minutes=self._random.randint(5, 190))).isoformat(timespec="seconds"),
                )

        return devices

    def _tick(self) -> None:
        """Occasionally flip one device to keep dashboard data alive."""
        now = datetime.now()
        elapsed = (now - self._last_tick).total_seconds()
        if elapsed < 20:
            return

        flips = max(1, int(elapsed // 45))
        for _ in range(flips):
            device = self._random.choice(list(self._devices.values()))
            self.set_status(device.id, not device.status, now=now)
        self._last_tick = now

    def devices(self) -> list[dict]:
        self._tick()
        return [device.to_dict() for device in self._devices.values()]

    def room_devices(self, room_id: str) -> list[dict]:
        normalized = room_id.lower().replace(" ", "")
        aliases = {
            "drawingroom": "drawing",
            "workroom1": "work1",
            "workroom2": "work2",
        }
        lookup = aliases.get(normalized, normalized)
        return [device for device in self.devices() if device["room_id"] == lookup]

    def set_status(self, device_id: str, status: bool, now: datetime | None = None) -> dict:
        if device_id not in self._devices:
            raise KeyError(device_id)

        device = self._devices[device_id]
        if device.status != status:
            device.status = status
            device.last_changed = (now or datetime.now()).isoformat(timespec="seconds")
        return device.to_dict()

    def toggle(self, device_id: str) -> dict:
        if device_id not in self._devices:
            raise KeyError(device_id)
        return self.set_status(device_id, not self._devices[device_id].status)

    def summary(self) -> dict:
        devices = self.devices()
        room_summary = {}

        for room_id, room_name in ROOMS.items():
            room_devices = [device for device in devices if device["room_id"] == room_id]
            on_devices = [device for device in room_devices if device["status"]]
            counts = Counter(device["type"] for device in on_devices)
            room_summary[room_id] = {
                "room_name": room_name,
                "device_count": len(room_devices),
                "on_count": len(on_devices),
                "fan_on_count": counts["fan"],
                "light_on_count": counts["light"],
                "power_watts": sum(device["current_power_watts"] for device in room_devices),
            }

        total_power = sum(room["power_watts"] for room in room_summary.values())
        return {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "device_count": len(devices),
            "on_count": sum(room["on_count"] for room in room_summary.values()),
            "total_power_watts": total_power,
            "estimated_daily_kwh": round(total_power * 24 / 1000, 2),
            "rooms": room_summary,
        }

    def alerts(self) -> list[dict]:
        devices = self.devices()
        now = datetime.now()
        outside_hours = now.hour < 9 or now.hour >= 17
        alerts: list[dict] = []

        if outside_hours:
            by_room = defaultdict(list)
            for device in devices:
                if device["status"]:
                    by_room[device["room_id"]].append(device)

            for room_id, room_devices in by_room.items():
                alerts.append(
                    {
                        "type": "outside_hours",
                        "severity": "high",
                        "room_id": room_id,
                        "room_name": ROOMS[room_id],
                        "message": f"{ROOMS[room_id]} has {len(room_devices)} device(s) on outside office hours.",
                    }
                )

        for device in devices:
            if not device["status"]:
                continue
            last_changed = datetime.fromisoformat(device["last_changed"])
            active_minutes = int((now - last_changed).total_seconds() // 60)
            if active_minutes >= 120:
                alerts.append(
                    {
                        "type": "long_running_device",
                        "severity": "medium",
                        "room_id": device["room_id"],
                        "room_name": device["room_name"],
                        "device_id": device["id"],
                        "message": f"{device['room_name']} {device['name']} has been on for {active_minutes} minutes.",
                    }
                )

        return alerts


simulator = OfficeSimulator()


def summarize_room_counts(devices: Iterable[dict]) -> Counter:
    return Counter(device["type"] for device in devices if device["status"])

