import cv2
import numpy as np
from dataclasses import dataclass


@dataclass
class Detection:
    direction: str
    x: int
    y: int
    confidence: float
    width: int
    height: int


class ArrowDetector:
    DIRECTIONS = ("up", "down", "left", "right")

    def __init__(self, template_paths: dict[str, str], threshold: float = 0.75):
        self.threshold = threshold
        self.templates: dict[str, np.ndarray] = {}
        for direction in self.DIRECTIONS:
            path = template_paths[direction]
            tmpl = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if tmpl is None:
                raise FileNotFoundError(f"Template not found: {path}")
            self.templates[direction] = tmpl

    def detect(self, frame: np.ndarray) -> list[Detection]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        all_detections: list[Detection] = []

        for direction, tmpl in self.templates.items():
            h, w = tmpl.shape
            result = cv2.matchTemplate(gray, tmpl, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= self.threshold)

            for pt_y, pt_x in zip(*locations):
                conf = result[pt_y, pt_x]
                all_detections.append(Detection(
                    direction=direction,
                    x=int(pt_x),
                    y=int(pt_y),
                    confidence=float(conf),
                    width=w,
                    height=h,
                ))

        return self._non_max_suppression(all_detections)

    def _non_max_suppression(self, detections: list[Detection], overlap_px: int = 20) -> list[Detection]:
        if not detections:
            return []

        detections.sort(key=lambda d: d.confidence, reverse=True)
        kept: list[Detection] = []

        for det in detections:
            is_duplicate = False
            for existing in kept:
                if abs(det.x - existing.x) < overlap_px and abs(det.y - existing.y) < overlap_px:
                    is_duplicate = True
                    break
            if not is_duplicate:
                kept.append(det)

        return kept
