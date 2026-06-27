import time
from dataclasses import dataclass, field
from src.detector import Detection


@dataclass
class TrackedArrow:
    id: int
    direction: str
    first_seen_x: float
    last_seen_x: float
    first_seen_time: float
    last_seen_time: float
    actioned: bool = False
    frames_missing: int = 0

    @property
    def velocity(self) -> float:
        dt = self.last_seen_time - self.first_seen_time
        if dt <= 0:
            return 0.0
        return (self.first_seen_x - self.last_seen_x) / dt


class SequenceTracker:
    def __init__(self, hit_zone_x: int, matching_radius: int = 40, expire_frames: int = 15):
        self.hit_zone_x = hit_zone_x
        self.matching_radius = matching_radius
        self.expire_frames = expire_frames
        self._tracks: list[TrackedArrow] = []
        self._next_id = 0
        self._pending_actions: list[TrackedArrow] = []

    def update(self, detections: list[Detection], timestamp: float | None = None) -> None:
        ts = timestamp or time.time()
        self._pending_actions.clear()

        matched_track_ids: set[int] = set()
        matched_det_indices: set[int] = set()

        for i, det in enumerate(detections):
            best_track = None
            best_dist = float("inf")
            for track in self._tracks:
                if track.id in matched_track_ids:
                    continue
                if track.direction != det.direction:
                    continue
                dx = abs(det.x - track.last_seen_x)
                if dx < self.matching_radius and dx < best_dist:
                    best_dist = dx
                    best_track = track
            if best_track is not None:
                best_track.last_seen_x = det.x
                best_track.last_seen_time = ts
                best_track.frames_missing = 0
                matched_track_ids.add(best_track.id)
                matched_det_indices.add(i)

        for i, det in enumerate(detections):
            if i in matched_det_indices:
                continue
            new_track = TrackedArrow(
                id=self._next_id,
                direction=det.direction,
                first_seen_x=det.x,
                last_seen_x=det.x,
                first_seen_time=ts,
                last_seen_time=ts,
            )
            self._tracks.append(new_track)
            self._next_id += 1

        expired = []
        for track in self._tracks:
            if track.id not in matched_track_ids and track.last_seen_time < ts:
                track.frames_missing += 1
                if track.frames_missing > self.expire_frames:
                    expired.append(track)

        for track in expired:
            self._tracks.remove(track)

        for track in self._tracks:
            if not track.actioned and track.last_seen_x <= self.hit_zone_x:
                track.actioned = True
                self._pending_actions.append(track)

    def get_hit_zone_arrows(self) -> list[TrackedArrow]:
        return list(self._pending_actions)

    def get_upcoming_sequence(self) -> list[TrackedArrow]:
        active = [t for t in self._tracks if not t.actioned]
        active.sort(key=lambda t: t.last_seen_x)
        return active

    def reset(self) -> None:
        self._tracks.clear()
        self._pending_actions.clear()
        self._next_id = 0
