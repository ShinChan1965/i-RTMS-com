from deep_sort_realtime.deepsort_tracker import DeepSort
# import time

# start = time.time()
from config.config import (
    MAX_AGE,
    MIN_HITS,
    MAX_COSINE_DISTANCE,
    NN_BUDGET,
    IOU_THRESHOLD_TRACK,
)

class DeepSORTTracker:
    def __init__(self):
        self.tracker = DeepSort(
            max_age=MAX_AGE,
            n_init=MIN_HITS,
            max_cosine_distance=MAX_COSINE_DISTANCE,
            nn_budget=NN_BUDGET,
            nms_max_overlap=IOU_THRESHOLD_TRACK,
            embedder="mobilenet",
            embedder_gpu=True,
            half=True,
            bgr=True
        )

    def update(self, detections, frame):
       
        formatted = []

        for d in detections:
            x1, y1, x2, y2, conf = d

            formatted.append((
                [x1, y1, x2 - x1, y2 - y1],  # xywh
                conf,
                "person"
            ))
        # tracks = self.tracker.update_tracks(formatted, frame=frame)
        # print("DeepSORT time:", time.time() - start)
        return self.tracker.update_tracks(formatted, frame=frame)