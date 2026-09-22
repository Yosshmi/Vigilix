from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass(slots=True, frozen=True)
class VideoMetadata:
    fps: float
    width: int
    height: int
    frame_count: int

    @property
    def duration_seconds(self) -> float:
        if self.fps <= 0:
            return 0.0
        return self.frame_count / self.fps


@dataclass(slots=True)
class VideoFrame:
    index: int
    timestamp_seconds: float
    image: np.ndarray


class VideoReader:
    def __init__(self, source: str | Path) -> None:
        self.source = str(source)
        self._capture = cv2.VideoCapture(self.source)
        if not self._capture.isOpened():
            raise ValueError(f"Unable to open video source: {self.source}")

    @property
    def metadata(self) -> VideoMetadata:
        return VideoMetadata(
            fps=float(self._capture.get(cv2.CAP_PROP_FPS) or 0.0),
            width=int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0),
            height=int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0),
            frame_count=int(self._capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0),
        )

    def frames(self) -> Iterator[VideoFrame]:
        fps = self.metadata.fps
        index = 0

        while True:
            ok, frame = self._capture.read()
            if not ok:
                break

            timestamp = index / fps if fps > 0 else 0.0
            yield VideoFrame(index=index, timestamp_seconds=timestamp, image=frame)
            index += 1

    def close(self) -> None:
        self._capture.release()

    def __enter__(self) -> "VideoReader":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
