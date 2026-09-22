from abc import ABC, abstractmethod

import numpy as np

from app.vision.types import Detection


class ObjectDetector(ABC):
    @abstractmethod
    def detect(self, frame: np.ndarray) -> list[Detection]:
        raise NotImplementedError


class YoloDetector(ObjectDetector):
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

    def detect(self, frame: np.ndarray) -> list[Detection]:
        result = self.model.predict(
            source=frame,
            conf=self.confidence,
            iou=self.iou,
            imgsz=self.image_size,
            verbose=False,
        )[0]

        detections: list[Detection] = []
        names = result.names

        for box in result.boxes:
            class_id = int(box.cls.item())
            class_name = str(names[class_id])

            if self.target_classes and class_name not in self.target_classes:
                continue

            x1, y1, x2, y2 = (float(value) for value in box.xyxy[0].tolist())
            detections.append(
                Detection(
                    class_id=class_id,
                    class_name=class_name,
                    confidence=float(box.conf.item()),
                    bbox=(x1, y1, x2, y2),
                )
            )

        return detections
