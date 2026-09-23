import json
import subprocess
from types import SimpleNamespace

import cv2
import numpy as np

from app.core.config import get_settings
from app.services import video_analysis
from app.vision.tracker import Track, YoloByteTracker


def test_active_count_drops_when_no_tracks_are_visible():
    tracker = YoloByteTracker.__new__(YoloByteTracker)
    tracker._tracks = {7: Track(7, 0, "person", 0.9, (0, 0, 10, 10), 0, 0)}
    tracker.confidence, tracker.iou, tracker.image_size = 0.35, 0.45, 640
    tracker.model = SimpleNamespace(track=lambda **kwargs: [SimpleNamespace(boxes=None)])
    assert tracker.update(np.zeros((32, 32, 3), dtype=np.uint8), 1) == []
    assert tracker.track_count == 0


def test_analysis_uses_settings_and_produces_browser_video(tmp_path, monkeypatch):
    # Only inference is replaced: actual decode, annotation, encoding and probing run.
    options = {}

    class EmptyTracker:
        track_count = 0

        def __init__(self, **kwargs):
            options.update(kwargs)

        def update(self, frame, timestamp):
            return []

    monkeypatch.setattr(video_analysis, "YoloByteTracker", EmptyTracker)
    monkeypatch.setenv("VIGILIX_YOLO_MODEL", "custom.pt")
    monkeypatch.setenv("VIGILIX_CONFIDENCE_THRESHOLD", "0.61")
    monkeypatch.setenv("VIGILIX_IOU_THRESHOLD", "0.52")
    monkeypatch.setenv("VIGILIX_INFERENCE_SIZE", "320")
    get_settings.cache_clear()
    source, output = tmp_path / "input.mp4", tmp_path / "output.mp4"
    writer = cv2.VideoWriter(str(source), cv2.VideoWriter_fourcc(*"mp4v"), 5, (64, 48))
    assert writer.isOpened()
    for _ in range(3):
        writer.write(np.zeros((48, 64, 3), dtype=np.uint8))
    writer.release()
    try:
        result = video_analysis.VideoAnalysisService().analyze(source, output)
        assert result.frame_count == 3
        assert result.analytics["active_tracks"] == 0
        assert options["model_name"] == "custom.pt"
        assert options["confidence"] == 0.61
        assert options["iou"] == 0.52
        assert options["image_size"] == 320
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(output)],
            capture_output=True, text=True, check=True,
        )
        stream = json.loads(probe.stdout)["streams"][0]
        assert stream["codec_name"] == "h264"
        assert stream["pix_fmt"] == "yuv420p"
        assert int(stream["nb_frames"]) == 3
    finally:
        get_settings.cache_clear()
