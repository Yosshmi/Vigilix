from app.vision.types import Detection


def test_detection_geometry_helpers() -> None:
    detection = Detection(
        class_id=0,
        class_name="person",
        confidence=0.91,
        bbox=(10.0, 20.0, 50.0, 80.0),
    )

    assert detection.center == (30.0, 50.0)
    assert detection.width == 40.0
    assert detection.height == 60.0
