from enum import Enum
from src.detector import Detection


class Phase(Enum):
    IDLE = "idle"
    RECORDING = "recording"
    READY = "ready"
    INPUTTING = "inputting"


class SequenceRecorder:
    def __init__(
        self,
        no_arrow_threshold: int = 15,
        confirm_frames: int = 3,
        gap_frames: int = 3,
    ):
        self.no_arrow_threshold = no_arrow_threshold
        self.confirm_frames = confirm_frames
        self.gap_frames = gap_frames

        self._sequence: list[str] = []
        self._phase = Phase.IDLE
        self._current_arrow: str | None = None
        self._frames_without_arrow = 0
        self._input_index = 0

        # Debouncing state
        self._pending_direction: str | None = None
        self._pending_count = 0
        self._gap_count = 0
        self._waiting_for_gap = False

    @property
    def phase(self) -> Phase:
        return self._phase

    @property
    def sequence(self) -> list[str]:
        return list(self._sequence)

    @property
    def input_index(self) -> int:
        return self._input_index

    def _confirm_arrow(self, direction: str) -> bool:
        if direction == self._pending_direction:
            self._pending_count += 1
        else:
            self._pending_direction = direction
            self._pending_count = 1
        return self._pending_count >= self.confirm_frames

    def _reset_pending(self):
        self._pending_direction = None
        self._pending_count = 0

    def update(self, detections: list[Detection]) -> None:
        best = self._pick_best_detection(detections)

        if self._phase == Phase.IDLE:
            if best is not None and self._confirm_arrow(best.direction):
                self._phase = Phase.RECORDING
                self._sequence.clear()
                self._current_arrow = best.direction
                self._sequence.append(best.direction)
                self._frames_without_arrow = 0
                self._waiting_for_gap = True
                self._gap_count = 0
                self._reset_pending()

        elif self._phase == Phase.RECORDING:
            if best is not None:
                self._frames_without_arrow = 0

                if self._waiting_for_gap:
                    if best.direction == self._current_arrow:
                        self._gap_count = 0
                    else:
                        pass
                else:
                    if self._confirm_arrow(best.direction):
                        if best.direction != self._current_arrow:
                            self._current_arrow = best.direction
                            self._sequence.append(best.direction)
                            self._waiting_for_gap = True
                            self._gap_count = 0
                            self._reset_pending()
            else:
                self._frames_without_arrow += 1

                if self._waiting_for_gap:
                    self._gap_count += 1
                    if self._gap_count >= self.gap_frames:
                        self._waiting_for_gap = False
                        self._reset_pending()

                if self._frames_without_arrow >= self.no_arrow_threshold:
                    self._phase = Phase.READY
                    self._current_arrow = None
                    self._input_index = 0
                    self._reset_pending()
                    self._waiting_for_gap = False

        elif self._phase == Phase.READY:
            if best is not None and self._confirm_arrow(best.direction):
                self._phase = Phase.RECORDING
                self._sequence.clear()
                self._current_arrow = best.direction
                self._sequence.append(best.direction)
                self._frames_without_arrow = 0
                self._waiting_for_gap = True
                self._gap_count = 0
                self._reset_pending()

        elif self._phase == Phase.INPUTTING:
            if self._input_index >= len(self._sequence):
                self._phase = Phase.IDLE
                self._sequence.clear()

    def _pick_best_detection(self, detections: list[Detection]) -> Detection | None:
        if not detections:
            return None
        return max(detections, key=lambda d: d.confidence)

    def start_input(self) -> None:
        if self._phase == Phase.READY and self._sequence:
            self._phase = Phase.INPUTTING
            self._input_index = 0

    def get_next_input(self) -> str | None:
        if self._phase != Phase.INPUTTING:
            return None
        if self._input_index >= len(self._sequence):
            return None
        direction = self._sequence[self._input_index]
        self._input_index += 1
        if self._input_index >= len(self._sequence):
            self._phase = Phase.IDLE
        return direction

    def reset(self) -> None:
        self._sequence.clear()
        self._phase = Phase.IDLE
        self._current_arrow = None
        self._frames_without_arrow = 0
        self._input_index = 0
        self._reset_pending()
        self._waiting_for_gap = False
        self._gap_count = 0
