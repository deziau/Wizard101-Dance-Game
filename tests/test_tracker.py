import unittest
from src.detector import Detection
from src.tracker import SequenceTracker


class TestSequenceTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = SequenceTracker(hit_zone_x=80, matching_radius=40, expire_frames=5)

    def test_new_detection_creates_track(self):
        detections = [Detection("up", 400, 50, 0.9, 30, 30)]
        self.tracker.update(detections, timestamp=1.0)
        upcoming = self.tracker.get_upcoming_sequence()
        self.assertEqual(len(upcoming), 1)
        self.assertEqual(upcoming[0].direction, "up")

    def test_matching_detection_updates_track(self):
        self.tracker.update([Detection("up", 400, 50, 0.9, 30, 30)], timestamp=1.0)
        self.tracker.update([Detection("up", 380, 50, 0.9, 30, 30)], timestamp=1.05)
        upcoming = self.tracker.get_upcoming_sequence()
        self.assertEqual(len(upcoming), 1)
        self.assertEqual(upcoming[0].last_seen_x, 380)

    def test_different_directions_separate_tracks(self):
        detections = [
            Detection("up", 400, 50, 0.9, 30, 30),
            Detection("down", 300, 50, 0.85, 30, 30),
        ]
        self.tracker.update(detections, timestamp=1.0)
        upcoming = self.tracker.get_upcoming_sequence()
        self.assertEqual(len(upcoming), 2)

    def test_hit_zone_triggers_action(self):
        self.tracker.update([Detection("left", 100, 50, 0.9, 30, 30)], timestamp=1.0)
        actions = self.tracker.get_hit_zone_arrows()
        self.assertEqual(len(actions), 0)

        self.tracker.update([Detection("left", 70, 50, 0.9, 30, 30)], timestamp=1.1)
        actions = self.tracker.get_hit_zone_arrows()
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].direction, "left")

    def test_action_fires_only_once(self):
        self.tracker.update([Detection("right", 70, 50, 0.9, 30, 30)], timestamp=1.0)
        actions1 = self.tracker.get_hit_zone_arrows()
        self.assertEqual(len(actions1), 1)

        self.tracker.update([Detection("right", 60, 50, 0.9, 30, 30)], timestamp=1.1)
        actions2 = self.tracker.get_hit_zone_arrows()
        self.assertEqual(len(actions2), 0)

    def test_upcoming_sorted_by_x(self):
        detections = [
            Detection("up", 500, 50, 0.9, 30, 30),
            Detection("down", 200, 50, 0.9, 30, 30),
            Detection("left", 350, 50, 0.9, 30, 30),
        ]
        self.tracker.update(detections, timestamp=1.0)
        upcoming = self.tracker.get_upcoming_sequence()
        xs = [t.last_seen_x for t in upcoming]
        self.assertEqual(xs, sorted(xs))

    def test_reset_clears_state(self):
        self.tracker.update([Detection("up", 400, 50, 0.9, 30, 30)], timestamp=1.0)
        self.tracker.reset()
        self.assertEqual(len(self.tracker.get_upcoming_sequence()), 0)

    def test_expired_tracks_removed(self):
        self.tracker.update([Detection("up", 400, 50, 0.9, 30, 30)], timestamp=1.0)
        for i in range(10):
            self.tracker.update([], timestamp=1.1 + i * 0.05)
        upcoming = self.tracker.get_upcoming_sequence()
        self.assertEqual(len(upcoming), 0)


if __name__ == "__main__":
    unittest.main()
