import unittest

from disbot.simulator import OfficeSimulator


class OfficeSimulatorTest(unittest.TestCase):
    def test_builds_expected_room_breakdown(self):
        simulator = OfficeSimulator(seed=1)
        summary = simulator.summary()

        self.assertEqual(summary["device_count"], 15)
        self.assertEqual(set(summary["rooms"]), {"drawing", "work1", "work2"})
        for room in summary["rooms"].values():
            self.assertEqual(room["device_count"], 5)

    def test_toggle_changes_device_status(self):
        simulator = OfficeSimulator(seed=1)
        before = next(device for device in simulator.devices() if device["id"] == "drawing-fan-1")
        after = simulator.toggle("drawing-fan-1")

        self.assertNotEqual(before["status"], after["status"])

    def test_summary_contains_usage_estimate(self):
        simulator = OfficeSimulator(seed=1)
        summary = simulator.summary()

        self.assertIn("total_power_watts", summary)
        self.assertIn("estimated_daily_kwh", summary)

