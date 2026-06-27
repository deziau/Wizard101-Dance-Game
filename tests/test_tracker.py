import unittest
from src.detector import Detection
from src.tracker import SequenceRecorder, Phase


class TestSequenceRecorder(unittest.TestCase):
    def setUp(self):
        self.recorder = SequenceRecorder(no_arrow_threshold=5)

    def test_starts_idle(self):
        self.assertEqual(self.recorder.phase, Phase.IDLE)
        self.assertEqual(self.recorder.sequence, [])

    def test_first_detection_starts_recording(self):
        self.recorder.update([Detection("up", 100, 50, 0.9, 30, 30)])
        self.assertEqual(self.recorder.phase, Phase.RECORDING)
        self.assertEqual(self.recorder.sequence, ["up"])

    def test_same_arrow_not_duplicated(self):
        for _ in range(5):
            self.recorder.update([Detection("up", 100, 50, 0.9, 30, 30)])
        self.assertEqual(self.recorder.sequence, ["up"])

    def test_new_direction_appended(self):
        self.recorder.update([Detection("up", 100, 50, 0.9, 30, 30)])
        self.recorder.update([Detection("up", 100, 50, 0.9, 30, 30)])
        self.recorder.update([Detection("down", 100, 50, 0.9, 30, 30)])
        self.assertEqual(self.recorder.sequence, ["up", "down"])

    def test_records_full_sequence(self):
        arrows = ["up", "right", "down", "left", "up"]
        for direction in arrows:
            for _ in range(3):
                self.recorder.update([Detection(direction, 100, 50, 0.9, 30, 30)])
        self.assertEqual(self.recorder.sequence, arrows)

    def test_no_arrow_transitions_to_ready(self):
        self.recorder.update([Detection("up", 100, 50, 0.9, 30, 30)])
        self.assertEqual(self.recorder.phase, Phase.RECORDING)

        for _ in range(10):
            self.recorder.update([])
        self.assertEqual(self.recorder.phase, Phase.READY)

    def test_ready_preserves_sequence(self):
        self.recorder.update([Detection("left", 100, 50, 0.9, 30, 30)])
        self.recorder.update([Detection("right", 100, 50, 0.9, 30, 30)])
        for _ in range(10):
            self.recorder.update([])
        self.assertEqual(self.recorder.phase, Phase.READY)
        self.assertEqual(self.recorder.sequence, ["left", "right"])

    def test_get_next_input(self):
        self.recorder.update([Detection("up", 100, 50, 0.9, 30, 30)])
        self.recorder.update([Detection("down", 100, 50, 0.9, 30, 30)])
        for _ in range(10):
            self.recorder.update([])

        self.recorder.start_input()
        self.assertEqual(self.recorder.phase, Phase.INPUTTING)
        self.assertEqual(self.recorder.get_next_input(), "up")
        self.assertEqual(self.recorder.get_next_input(), "down")
        self.assertIsNone(self.recorder.get_next_input())

    def test_input_exhausted_returns_to_idle(self):
        self.recorder.update([Detection("up", 100, 50, 0.9, 30, 30)])
        for _ in range(10):
            self.recorder.update([])

        self.recorder.start_input()
        self.recorder.get_next_input()
        self.assertEqual(self.recorder.phase, Phase.IDLE)

    def test_picks_highest_confidence(self):
        self.recorder.update([
            Detection("up", 100, 50, 0.7, 30, 30),
            Detection("down", 100, 50, 0.9, 30, 30),
        ])
        self.assertEqual(self.recorder.sequence, ["down"])

    def test_reset_clears_everything(self):
        self.recorder.update([Detection("up", 100, 50, 0.9, 30, 30)])
        self.recorder.reset()
        self.assertEqual(self.recorder.phase, Phase.IDLE)
        self.assertEqual(self.recorder.sequence, [])

    def test_new_recording_after_idle(self):
        self.recorder.update([Detection("up", 100, 50, 0.9, 30, 30)])
        for _ in range(10):
            self.recorder.update([])
        self.recorder.start_input()
        self.recorder.get_next_input()
        self.assertEqual(self.recorder.phase, Phase.IDLE)

        self.recorder.update([Detection("left", 100, 50, 0.9, 30, 30)])
        self.assertEqual(self.recorder.phase, Phase.RECORDING)
        self.assertEqual(self.recorder.sequence, ["left"])


if __name__ == "__main__":
    unittest.main()
