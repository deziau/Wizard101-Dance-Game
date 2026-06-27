import unittest
from src.detector import Detection
from src.tracker import SequenceRecorder, Phase


def det(direction, confidence=0.9):
    return Detection(direction, 100, 50, confidence, 30, 30)


class TestSequenceRecorder(unittest.TestCase):
    def setUp(self):
        self.recorder = SequenceRecorder(
            no_arrow_threshold=5,
            confirm_frames=3,
            gap_frames=2,
        )

    def _show_arrow(self, direction, frames=5):
        """Simulate an arrow being shown for N frames."""
        for _ in range(frames):
            self.recorder.update([det(direction)])

    def _show_gap(self, frames=3):
        """Simulate no arrow for N frames."""
        for _ in range(frames):
            self.recorder.update([])

    def test_starts_idle(self):
        self.assertEqual(self.recorder.phase, Phase.IDLE)
        self.assertEqual(self.recorder.sequence, [])

    def test_single_frame_does_not_record(self):
        self.recorder.update([det("up")])
        self.assertEqual(self.recorder.phase, Phase.IDLE)

    def test_confirmed_detection_starts_recording(self):
        self._show_arrow("up")
        self.assertEqual(self.recorder.phase, Phase.RECORDING)
        self.assertEqual(self.recorder.sequence, ["up"])

    def test_same_arrow_not_duplicated(self):
        self._show_arrow("up", frames=10)
        self.assertEqual(self.recorder.sequence, ["up"])

    def test_brief_false_detection_ignored(self):
        self._show_arrow("up")
        self._show_gap()
        # One brief false frame of "left" then back to gap
        self.recorder.update([det("left")])
        self._show_gap()
        # Should NOT have recorded "left"
        self.assertEqual(self.recorder.sequence, ["up"])

    def test_new_arrow_after_gap(self):
        self._show_arrow("up")
        self._show_gap()
        self._show_arrow("down")
        self.assertEqual(self.recorder.sequence, ["up", "down"])

    def test_full_sequence(self):
        arrows = ["up", "right", "down", "left", "up"]
        for direction in arrows:
            self._show_arrow(direction)
            self._show_gap()
        self.assertEqual(self.recorder.sequence, arrows)

    def test_no_arrow_transitions_to_ready(self):
        self._show_arrow("up")
        self._show_gap(frames=10)
        self.assertEqual(self.recorder.phase, Phase.READY)

    def test_ready_preserves_sequence(self):
        self._show_arrow("left")
        self._show_gap()
        self._show_arrow("right")
        self._show_gap(frames=10)
        self.assertEqual(self.recorder.phase, Phase.READY)
        self.assertEqual(self.recorder.sequence, ["left", "right"])

    def test_get_next_input(self):
        self._show_arrow("up")
        self._show_gap()
        self._show_arrow("down")
        self._show_gap(frames=10)

        self.recorder.start_input()
        self.assertEqual(self.recorder.phase, Phase.INPUTTING)
        self.assertEqual(self.recorder.get_next_input(), "up")
        self.assertEqual(self.recorder.get_next_input(), "down")
        self.assertIsNone(self.recorder.get_next_input())

    def test_input_exhausted_returns_to_idle(self):
        self._show_arrow("up")
        self._show_gap(frames=10)

        self.recorder.start_input()
        self.recorder.get_next_input()
        self.assertEqual(self.recorder.phase, Phase.IDLE)

    def test_picks_highest_confidence(self):
        for _ in range(5):
            self.recorder.update([det("up", 0.7), det("down", 0.9)])
        self.assertEqual(self.recorder.sequence, ["down"])

    def test_reset_clears_everything(self):
        self._show_arrow("up")
        self.recorder.reset()
        self.assertEqual(self.recorder.phase, Phase.IDLE)
        self.assertEqual(self.recorder.sequence, [])

    def test_new_round_resets_from_ready(self):
        self._show_arrow("up")
        self._show_gap()
        self._show_arrow("right")
        self._show_gap(frames=10)
        self.assertEqual(self.recorder.phase, Phase.READY)

        self._show_arrow("down")
        self.assertEqual(self.recorder.phase, Phase.RECORDING)
        self.assertEqual(self.recorder.sequence, ["down"])

    def test_new_recording_after_input_complete(self):
        self._show_arrow("up")
        self._show_gap(frames=10)
        self.recorder.start_input()
        self.recorder.get_next_input()
        self.assertEqual(self.recorder.phase, Phase.IDLE)

        self._show_arrow("left")
        self.assertEqual(self.recorder.phase, Phase.RECORDING)
        self.assertEqual(self.recorder.sequence, ["left"])

    def test_flickering_detection_not_recorded(self):
        """Alternating directions frame-by-frame should not record."""
        self._show_arrow("up")
        self._show_gap()
        # Flickering: alternating left/right each frame
        self.recorder.update([det("left")])
        self.recorder.update([det("right")])
        self.recorder.update([det("left")])
        self.recorder.update([det("right")])
        self.assertEqual(self.recorder.sequence, ["up"])


if __name__ == "__main__":
    unittest.main()
