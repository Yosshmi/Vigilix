from dataclasses import dataclass, field

from app.vision.geometry import Point, side_of_line


@dataclass(slots=True)
class LineCrossingRule:
    line_id: str
    start: Point
    end: Point
    previous_sides: dict[int, float] = field(default_factory=dict)

    def update(self, track_id: int, center: Point) -> str | None:
        current_side = side_of_line(center, self.start, self.end)
        previous_side = self.previous_sides.get(track_id)
        self.previous_sides[track_id] = current_side

        if previous_side is None or previous_side == 0 or current_side == 0:
            return None

        if previous_side < 0 < current_side:
            return "IN"
        if previous_side > 0 > current_side:
            return "OUT"

        return None
