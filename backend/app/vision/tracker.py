from dataclasses import dataclass, field
from time import monotonic

import numpy as np

from app.vision.types import BoundingBox


@dataclass(slots=True)
class Track:
    track_id: int
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBox
    first_seen: float
    last_seen: float
    history: list[tuple[float, float]] = field(default_factory=list)

    @property
    def center(self) -> tuple[float, float]:
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


class YoloByteTracker:
    def __init__(
        self,
        model_name: str = "yolo11n.pt",
        confidence: float = 0.35,
        iou: float = 0.45,
        image_size: int = 640,
        target_classes: set[str] | None = None,
    ) -> None:
        from ultralytics import YOLO

        self.model = YOLO(model_name)
        self.confidence = confidence
        self.iou = iou
        self.image_size = image_size
        self.target_classes = target_classes
        self._tracks: dict[int, Track] = {}
        self._active_track_ids: set[int] = set()

    @property
    def track_count(self) -> int:
        return len(getattr(self, "_active_track_ids", set()))

    def update(self, frame: np.ndarray, timestamp_seconds: float | None = None) -> list[Track]:
        now = timestamp_seconds if timestamp_seconds is not None else monotonic()
        result = self.model.track(
            source=frame,
            persist=True,
            tracker="bytetrack.yaml",
            conf=self.confidence,
            iou=self.iou,
            imgsz=self.image_size,
            verbose=False,
        )[0]

        if result.boxes is None or result.boxes.id is None:
            self._active_track_ids = set()
            return []

        names = result.names
        active: list[Track] = []

        for box in result.boxes:
            if box.id is None:
                continue

            track_id = int(box.id.item())
            class_id = int(box.cls.item())
            class_name = str(names[class_id])

            if self.target_classes and class_name not in self.target_classes:
                continue

            x1, y1, x2, y2 = (float(value) for value in box.xyxy[0].tolist())
            confidence = float(box.conf.item())
            center = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

            existing = self._tracks.get(track_id)
            first_seen = existing.first_seen if existing else now
            history = list(existing.history[-29:]) if existing else []
            history.append(center)

            track = Track(
                track_id=track_id,
                class_id=class_id,
                class_name=class_name,
                confidence=confidence,
                bbox=(x1, y1, x2, y2),
                first_seen=first_seen,
                last_seen=now,
                history=history,
            )
            self._tracks[track_id] = track
            active.append(track)

        self._active_track_ids = {track.track_id for track in active}
        return active

    def reset(self) -> None:
        self._tracks.clear()
        self._active_track_ids.clear()
        predictor = getattr(self.model, "predictor", None)
        if predictor is not None and hasattr(predictor, "trackers"):
            predictor.trackers = None
