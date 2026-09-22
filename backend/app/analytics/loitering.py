from dataclasses import dataclass, field

from app.vision.geometry import Point, point_in_polygon


@dataclass(slots=True)
class LoiteringRule:
    zone_id: str
    polygon: list[Point]
    threshold_seconds: float = 10.0
    entered_at: dict[int, float] = field(default_factory=dict)
    alerted_tracks: set[int] = field(default_factory=set)

    def update(self, track_id: int, center: Point, timestamp_seconds: float) -> bool:
        inside = point_in_polygon(center, self.polygon)

        if not inside:
            self.entered_at.pop(track_id, None)
            self.alerted_tracks.discard(track_id)
            return False

        entered = self.entered_at.setdefault(track_id, timestamp_seconds)
        elapsed = timestamp_seconds - entered

        if elapsed >= self.threshold_seconds and track_id not in self.alerted_tracks:
            self.alerted_tracks.add(track_id)
            return True

        return False
