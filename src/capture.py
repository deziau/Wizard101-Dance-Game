import numpy as np
import mss

from src.config import CaptureRegion


class ScreenCapture:
    def __init__(self, region: CaptureRegion):
        self.region = region
        self._sct = mss.mss()

    @property
    def monitor(self) -> dict:
        return {
            "left": self.region.x,
            "top": self.region.y,
            "width": self.region.width,
            "height": self.region.height,
        }

    def grab_frame(self) -> np.ndarray:
        img = self._sct.grab(self.monitor)
        frame = np.array(img)
        # mss returns BGRA; drop alpha channel for OpenCV (BGR)
        return frame[:, :, :3]

    def grab_fullscreen(self) -> np.ndarray:
        monitor = self._sct.monitors[1]
        img = self._sct.grab(monitor)
        frame = np.array(img)
        return frame[:, :, :3]

    def close(self):
        self._sct.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
