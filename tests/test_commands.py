import unittest

from disbot.commands import parse_command
from disbot.simulator import OfficeSimulator


class CommandParsingTest(unittest.TestCase):
    def setUp(self):
        self.simulator = OfficeSimulator(seed=1)

    def test_status_command_uses_summary(self):
        response = parse_command("!status", self.simulator.summary, lambda room: {"devices": []})

        self.assertIn("Office status:", response)
        self.assertIn("Drawing Room", response)

    def test_usage_command_reports_watts(self):
        response = parse_command("!usage", self.simulator.summary, lambda room: {"devices": []})

        self.assertIn("Current draw:", response)
        self.assertIn("kWh", response)

    def test_room_command_reports_devices(self):
        response = parse_command("!room work1", self.simulator.summary, self._room_payload)

        self.assertIn("Work Room 1:", response)
        self.assertIn("Fan 1", response)

    def test_non_command_returns_none(self):
        response = parse_command("hello bot", self.simulator.summary, self._room_payload)

        self.assertIsNone(response)

    def _room_payload(self, room_id):
        devices = self.simulator.room_devices(room_id)
        return {"room_id": room_id, "room_name": devices[0]["room_name"], "devices": devices}
