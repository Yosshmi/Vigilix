from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter

import cv2

from app.analytics.intrusion import IntrusionRule
from app.analytics.loitering import LoiteringRule
from app.analytics.people_counter import PeopleCounter
from app.analytics.rules_engine import AnalyticsEngine
from app.vision.annotator import draw_counting_line, draw_tracks, draw_zone
from app.vision.tracker import YoloByteTracker
from app.vision.video import VideoReader


@dataclass(slots=True)
class AnalysisResult:
    output_path: str
    frame_count: int
    processing_seconds: float
    average_fps: float
    events: list[dict[str, object]]
    analytics: dict[str, int | float]


class VideoAnalysisService:
    def __init__(self, model_name: str = "yolo11n.pt") -> None:
        self.model_name = model_name

    def analyze(self, input_path: str | Path, output_path: str | Path) -> AnalysisResult:
        input_path = Path(input_path)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        tracker = YoloByteTracker(
            model_name=self.model_name,
            target_classes={"person", "car", "truck", "bus", "motorcycle", "bicycle"},
        )

        all_events: list[dict[str, object]] = []
        start_time = perf_counter()
        processed_frames = 0

        with VideoReader(input_path) as reader:
            metadata = reader.metadata
            zone = [
                (metadata.width * 0.58, metadata.height * 0.2),
                (metadata.width * 0.95, metadata.height * 0.2),
                (metadata.width * 0.95, metadata.height * 0.9),
                (metadata.width * 0.58, metadata.height * 0.9),
            ]
            line_start = (metadata.width * 0.5, metadata.height * 0.15)
            line_end = (metadata.width * 0.5, metadata.height * 0.9)

            engine = AnalyticsEngine(
                intrusion_rule=IntrusionRule("restricted-1", zone),
                people_counter=PeopleCounter("entrance-1", line_start, line_end),
                loitering_rule=LoiteringRule("restricted-1", zone, threshold_seconds=5.0),
            )

            writer = cv2.VideoWriter(
                str(output_path),
                cv2.VideoWriter_fourcc(*"mp4v"),
                metadata.fps or 24.0,
                (metadata.width, metadata.height),
            )

            try:
                for video_frame in reader.frames():
                    tracks = tracker.update(video_frame.image, video_frame.timestamp_seconds)
                    frame_events = []
                    for track in tracks:
                        frame_events.extend(
                            engine.process_track(track, video_frame.timestamp_seconds)
                        )

                    all_events.extend(event.as_dict() for event in frame_events)

                    annotated = draw_tracks(video_frame.image, tracks)
                    annotated = draw_zone(annotated, zone)
                    annotated = draw_counting_line(annotated, line_start, line_end)
                    writer.write(annotated)
                    processed_frames += 1
            finally:
                writer.release()

            snapshot = engine.snapshot(active_tracks=len(tracker._tracks))

        elapsed = max(perf_counter() - start_time, 1e-9)
        return AnalysisResult(
            output_path=str(output_path),
            frame_count=processed_frames,
            processing_seconds=elapsed,
            average_fps=processed_frames / elapsed,
            events=all_events,
            analytics=asdict(snapshot),
        )
