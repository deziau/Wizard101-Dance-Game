import time
import random
import pyautogui
from src.tracker import TrackedArrow
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

    def show(self, upcoming: list[TrackedArrow], detection_count: int = 0) -> None:
        directions = [t.direction for t in upcoming]
        self.overlay.update_arrows(directions, detection_count)

    def on_action(self, arrow: TrackedArrow) -> None:
        pass

    def set_status(self, text: str) -> None:
        self.overlay.set_status(text)

    def pump(self) -> None:
        self.overlay.pump()

    def destroy(self) -> None:
        self.overlay.destroy()


class AutoPlayOutput:
    def __init__(self, delay_ms: int = 50, jitter_ms: int = 20):
        self.delay_ms = delay_ms
        self.jitter_ms = jitter_ms
        self.enabled = True
        self.overlay = ArrowOverlay()

    def show(self, upcoming: list[TrackedArrow], detection_count: int = 0) -> None:
        directions = [t.direction for t in upcoming]
        self.overlay.update_arrows(directions, detection_count)

    def on_action(self, arrow: TrackedArrow) -> None:
        if not self.enabled:
            return
        key = DIRECTION_KEYS.get(arrow.direction)
        if key is None:
            return
        delay = self.delay_ms + random.randint(-self.jitter_ms, self.jitter_ms)
        delay = max(0, delay)
        time.sleep(delay / 1000.0)
        pyautogui.press(key)

    def toggle(self) -> bool:
        self.enabled = not self.enabled
        return self.enabled

    def set_status(self, text: str) -> None:
        self.overlay.set_status(text)

    def pump(self) -> None:
        self.overlay.pump()

    def destroy(self) -> None:
        self.overlay.destroy()
