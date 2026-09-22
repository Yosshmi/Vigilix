from dataclasses import dataclass
from typing import TypeAlias


BoundingBox: TypeAlias = tuple[float, float, float, float]


@dataclass(slots=True, frozen=True)
class Detection:
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBox

    @property
    def center(self) -> tuple[float, float]:
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

    @property
    def width(self) -> float:
        x1, _, x2, _ = self.bbox
        return max(0.0, x2 - x1)

    @property
    def height(self) -> float:
        _, y1, _, y2 = self.bbox
        return max(0.0, y2 - y1)
