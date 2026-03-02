from config.config import (
    CONFIDENCE_THRESHOLD, IOU_THRESHOLD, MAX_DETECTIONS,
    DEVICE, HALF_PRECISION, IMAGE_SIZE,
)

class YOLODetector:
    def __init__(self, model):
        self.model = model

    def detect(self, frame):
        detections = []

        results = self.model.predict(
            source=frame,
            conf=CONFIDENCE_THRESHOLD,
            iou=IOU_THRESHOLD,
            classes=[0],
            max_det=MAX_DETECTIONS,
            imgsz=IMAGE_SIZE,
            device=DEVICE,
            half=HALF_PRECISION,
            stream=False,
            verbose=False,
        )

        for r in results:
            if r.boxes is None:
                continue

            for box in r.boxes:
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Remove very small boxes (noise filtering)
                if (x2 - x1) * (y2 - y1) < 1500:
                    continue

                detections.append([x1, y1, x2, y2, conf])

        return detections