import cv2
import numpy as np

from app.vision.tracker import Track


def draw_tracks(frame: np.ndarray, tracks: list[Track]) -> np.ndarray:
    output = frame.copy()

    for track in tracks:
        x1, y1, x2, y2 = (int(value) for value in track.bbox)
        label = f"{track.class_name} #{track.track_id} {track.confidence:.2f}"

        cv2.rectangle(output, (x1, y1), (x2, y2), (255, 255, 255), 2)
        cv2.putText(
            output,
            label,
            (x1, max(18, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        if len(track.history) > 1:
            points = np.array(track.history, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(output, [points], False, (255, 255, 255), 2)

    return output


def draw_zone(frame: np.ndarray, polygon: list[tuple[float, float]]) -> np.ndarray:
    if len(polygon) < 3:
        return frame

    output = frame.copy()
    points = np.array(polygon, dtype=np.int32).reshape((-1, 1, 2))
    cv2.polylines(output, [points], True, (255, 255, 255), 2)
    return output


def draw_counting_line(
    frame: np.ndarray,
    start: tuple[float, float],
    end: tuple[float, float],
) -> np.ndarray:
    output = frame.copy()
    cv2.line(
        output,
        (int(start[0]), int(start[1])),
        (int(end[0]), int(end[1])),
        (255, 255, 255),
        2,
    )
    return output
