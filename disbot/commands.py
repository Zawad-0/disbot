from __future__ import annotations

from collections.abc import Callable


def format_status(summary: dict) -> str:
    lines = ["Office status:"]
    for room in summary["rooms"].values():
        lines.append(
            f"- {room['room_name']}: {room['fan_on_count']} fan(s) ON, "
            f"{room['light_on_count']} light(s) ON, {room['power_watts']} W"
        )
    lines.append(f"Total: {summary['on_count']} device(s) ON, {summary['total_power_watts']} W")
    return "\n".join(lines)


def format_room(room: dict) -> str:
    lines = [f"{room['room_name']}:"]
    for device in room["devices"]:
        lines.append(
            f"- {device['name']} ({device['type']}): {device['status_label'].upper()} "
            f"({device['current_power_watts']} W)"
        )
    return "\n".join(lines)


def format_usage(summary: dict) -> str:
    return (
        f"Current draw: {summary['total_power_watts']} W\n"
        f"Estimated daily usage at this rate: {summary['estimated_daily_kwh']} kWh"
    )


def parse_command(message: str, fetch_summary: Callable[[], dict], fetch_room: Callable[[str], dict]) -> str | None:
    text = message.strip()
    parts = text.split(maxsplit=1)
    command = parts[0].lower() if parts else ""

    if command == "!status":
        return format_status(fetch_summary())

    if command == "!usage":
        return format_usage(fetch_summary())

    if command == "!room":
        if len(parts) == 1:
            return "Usage: !room drawing | !room work1 | !room work2"
        try:
            return format_room(fetch_room(parts[1]))
        except Exception:
            return "I could not find that room. Try drawing, work1, or work2."

    return None

