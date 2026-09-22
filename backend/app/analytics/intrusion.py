from dataclasses import dataclass, field

from app.vision.geometry import Point, point_in_polygon


@dataclass(slots=True)
class IntrusionRule:
    zone_id: str
    polygon: list[Point]
    active_tracks: set[int] = field(default_factory=set)

    def update(self, track_id: int, center: Point) -> bool:
        inside = point_in_polygon(center, self.polygon)

        if inside and track_id not in self.active_tracks:
            self.active_tracks.add(track_id)
            return True

        if not inside:
            self.active_tracks.discard(track_id)

        return False
