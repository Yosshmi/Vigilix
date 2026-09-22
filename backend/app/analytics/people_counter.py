from dataclasses import dataclass

from app.analytics.line_crossing import LineCrossingRule
from app.vision.geometry import Point


@dataclass(slots=True)
class CountSnapshot:
    entries: int
    exits: int

    @property
    def occupancy(self) -> int:
        return max(0, self.entries - self.exits)


class PeopleCounter:
    def __init__(self, line_id: str, start: Point, end: Point) -> None:
        self.rule = LineCrossingRule(line_id=line_id, start=start, end=end)
        self.entries = 0
        self.exits = 0
        self._counted_crossings: set[tuple[int, str]] = set()

    def update(self, track_id: int, center: Point) -> str | None:
        direction = self.rule.update(track_id, center)
        if direction is None:
            return None

        key = (track_id, direction)
        if key in self._counted_crossings:
            return None

        self._counted_crossings.add(key)
        if direction == "IN":
            self.entries += 1
        else:
            self.exits += 1
        return direction

    def snapshot(self) -> CountSnapshot:
        return CountSnapshot(entries=self.entries, exits=self.exits)
