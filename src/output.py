import time
import random
import pyautogui
from src.tracker import SequenceRecorder, Phase
from src.overlay import ArrowOverlay

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.02

DIRECTION_KEYS = {
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
}


class DisplayOutput:
    def __init__(self):
        self.overlay = ArrowOverlay()

    def update(self, recorder: SequenceRecorder) -> None:
        self.overlay.show_sequence(
            recorder.sequence,
            recorder.phase.value,
            recorder.input_index,
        )

    def set_status(self, text: str) -> None:
        self.overlay.set_status(text)

    def pump(self) -> None:
        self.overlay.pump()

    def destroy(self) -> None:
        self.overlay.destroy()


class AutoPlayOutput:
    def __init__(self, delay_ms: int = 50, jitter_ms: int = 20, input_interval_ms: int = 200):
        self.delay_ms = delay_ms
        self.jitter_ms = jitter_ms
        self.input_interval_ms = input_interval_ms
        self.enabled = True
        self.overlay = ArrowOverlay()
        self._last_input_time = 0.0

    def update(self, recorder: SequenceRecorder) -> None:
        self.overlay.show_sequence(
            recorder.sequence,
            recorder.phase.value,
            recorder.input_index,
        )

        if not self.enabled:
            return

        if recorder.phase == Phase.READY:
            recorder.start_input()

        if recorder.phase == Phase.INPUTTING:
            now = time.time()
            if now - self._last_input_time >= self.input_interval_ms / 1000.0:
                direction = recorder.get_next_input()
                if direction:
                    key = DIRECTION_KEYS.get(direction)
                    if key:
                        delay = self.delay_ms + random.randint(-self.jitter_ms, self.jitter_ms)
                        delay = max(0, delay)
                        time.sleep(delay / 1000.0)
                        pyautogui.press(key)
                        self._last_input_time = time.time()

    def toggle(self) -> bool:
        self.enabled = not self.enabled
        return self.enabled

    def set_status(self, text: str) -> None:
        self.overlay.set_status(text)

    def pump(self) -> None:
        self.overlay.pump()

    def destroy(self) -> None:
        self.overlay.destroy()
