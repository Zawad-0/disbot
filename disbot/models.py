from dataclasses import asdict, dataclass


@dataclass
class Device:
    id: str
    name: str
    type: str
    room_id: str
    room_name: str
    status: bool
    power_watts: int
    last_changed: str

    @property
    def current_power_watts(self) -> int:
        return self.power_watts if self.status else 0

    def to_dict(self) -> dict:
        data = asdict(self)
        data["current_power_watts"] = self.current_power_watts
        data["status_label"] = "on" if self.status else "off"
        return data

