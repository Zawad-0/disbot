from __future__ import annotations

import json
from urllib.request import urlopen


class BackendClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        self.base_url = base_url.rstrip("/")

    def _get(self, path: str) -> dict | list:
        with urlopen(f"{self.base_url}{path}", timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))

    def devices(self) -> list[dict]:
        return self._get("/api/devices")

    def summary(self) -> dict:
        return self._get("/api/summary")

    def room(self, room_id: str) -> dict:
        return self._get(f"/api/rooms/{room_id}")

    def alerts(self) -> list[dict]:
        return self._get("/api/alerts")

