import cv2
import torch
torch.backends.cudnn.benchmark = True
from ultralytics import YOLO
import time
import os
from collections import deque

from camera.video_stream import VideoStream
from detection.yolo_detector import YOLODetector
from tracking.deepsort_tracker import DeepSORTTracker
from logic.line_crossing import LineCrossing
from logic.counter import PassengerCounter
from config.config import (
    USE_ROI,
    LINE_POSITION_RATIO,
    LINE_HYSTERESIS_RATIO,
    CROSSING_COOLDOWN_FRAMES,
    INVERT_COUNTING_DIRECTION,
    MODEL_PATH,
    ROI_X1_RATIO,
    ROI_X2_RATIO,
    ROI_Y1_RATIO,
    ROI_Y2_RATIO,
    FRAME_SKIP
)

DEBUG_MODE = True   
PROFILE_LOOP_TIME = False 


def _iou(boxA, boxB):
    """
    IoU between two boxes in (x1, y1, x2, y2) format.
    Used to suppress duplicate tracker boxes that heavily overlap.
    """
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    inter_w = max(0, xB - xA)
    inter_h = max(0, yB - yA)
    inter_area = inter_w * inter_h

    if inter_area <= 0:
        return 0.0

    boxA_area = max(0, boxA[2] - boxA[0]) * max(0, boxA[3] - boxA[1])
    boxB_area = max(0, boxB[2] - boxB[0]) * max(0, boxB[3] - boxB[1])

    if boxA_area <= 0 or boxB_area <= 0:
        return 0.0

    return inter_area / float(boxA_area + boxB_area - inter_area)


def main():
    
    video = VideoStream()
    tracker = DeepSORTTracker()
    line = LineCrossing(
        line_position_ratio=LINE_POSITION_RATIO,
        hysteresis_ratio=LINE_HYSTERESIS_RATIO,
        cooldown_frames=CROSSING_COOLDOWN_FRAMES,
        invert_direction=INVERT_COUNTING_DIRECTION,
    )
    counter = PassengerCounter()
    model_path = MODEL_PATH
    if os.path.isdir(model_path):
        model_path = os.path.join(model_path, "best.pt")
    model = YOLO(model_path)
    yolo = YOLODetector(model)
    current_stop = "Surandai"
    stop_index = 1

    print("🚍 Passenger Counting System Started")

    if DEBUG_MODE:
        print("🧪 Running in DEBUG MODE")
        print("Press 'n' → Next stop | Press 'q' → Quit")
    else:
        print("🚀 Running in DEPLOYMENT MODE (Auto-start)")

    frame_count = 0

    loop_times = deque(maxlen=60)
    last_profile_print = time.perf_counter()

    try:
        while True:
            loop_start = time.perf_counter()
            # READ FRAME
            frame = video.read()
    
            if frame is None:
                continue

            h, w = frame.shape[:2]

            ROI_X1 = int(w * ROI_X1_RATIO)
            ROI_X2 = int(w * ROI_X2_RATIO)
            ROI_Y1 = int(h * ROI_Y1_RATIO)
            ROI_Y2 = int(h * ROI_Y2_RATIO)

            if USE_ROI:
                detection_frame = frame[ROI_Y1:ROI_Y2, ROI_X1:ROI_X2]
            else:
                detection_frame = frame

            frame_count += 1
            run_detection = (FRAME_SKIP <= 1) or (frame_count % FRAME_SKIP == 0)

            if run_detection:
                detections = yolo.detect(detection_frame)
            else:
                detections = []

            tracks = tracker.update(detections, detection_frame)

            if DEBUG_MODE:
                line.draw_line(frame)

                if USE_ROI:
                    cv2.rectangle(
                        frame,
                        (ROI_X1, ROI_Y1),
                        (ROI_X2, ROI_Y2),
                        (255, 0, 0),
                        2
                    )

            confirmed_tracks = []
            for track in tracks:
                if not track.is_confirmed():
                    continue

                x1, y1, x2, y2 = map(int, track.to_ltrb())

                if USE_ROI:
                    x1 += ROI_X1
                    x2 += ROI_X1
                    y1 += ROI_Y1
                    y2 += ROI_Y1

                confirmed_tracks.append((track, (x1, y1, x2, y2)))

            deduped_tracks = []
            IOU_SUPPRESS_THRESHOLD = 0.7

            for track, box in confirmed_tracks:
                duplicate = False
                for _, kept_box in deduped_tracks:
                    if _iou(box, kept_box) > IOU_SUPPRESS_THRESHOLD:
                        duplicate = True
                        break
                if not duplicate:
                    deduped_tracks.append((track, box))

            for track, (x1, y1, x2, y2) in deduped_tracks:
                track_id = track.track_id

                centroid_x = (x1 + x2) // 2
                centroid_y = (y1 + y2) // 2
                direction = line.check_crossing(track_id, centroid_y, frame.shape[0])

                if direction:
                    counter.update(
                        track_id,
                        direction,
                        stop=current_stop,
                        stop_index=stop_index,
                        centroid_x=centroid_x,
                        centroid_y=centroid_y,
                    )

                    print(
                        f"[DB UPDATE] ID {track_id} → {direction} "
                        f"at stop {current_stop}"
                    )

                if DEBUG_MODE:
                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2
                    )

                    cv2.putText(
                        frame,
                        f"ID {track_id}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2
                    )

            if DEBUG_MODE:
                entered, exited, current = counter.get_counts()

                cv2.putText(frame, f"Entered: {entered}", (20, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (255, 255, 255), 2)

                cv2.putText(frame, f"Exited: {exited}", (20, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (255, 255, 255), 2)

                cv2.putText(frame, f"Inside: {current}", (20, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (255, 255, 255), 2)

                cv2.putText(frame, f"Stop: {current_stop}", (20, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0, 255, 255), 2)

                cv2.imshow("Passenger Counting System", frame)

                key = cv2.waitKey(1) & 0xFF

                if key == ord('n'):
                    counter.store_stop_data(current_stop, stop_index)
                    stop_index += 1
                    current_stop = f"Stop_{stop_index}"
                    print(f"📍 Reached new stop → {current_stop}")

                elif key == ord('q'):
                    print("🛑 Exiting system")
                    break

            line.tick()

            if PROFILE_LOOP_TIME:
                dt = time.perf_counter() - loop_start
                loop_times.append(dt)

                now = time.perf_counter()
                if (now - last_profile_print) >= 1.0:
                    avg_dt = sum(loop_times) / max(1, len(loop_times))
                    fps = (1.0 / avg_dt) if avg_dt > 0 else 0.0
                    print(f"[PERF] avg_loop={avg_dt:.3f}s (~{fps:.1f} FPS), last={dt:.3f}s")
                    last_profile_print = now

    except KeyboardInterrupt:
        print("\n🛑 Interrupted")

    finally:
        counter.store_stop_data(current_stop, stop_index)
        counter.close()
        video.release()

        if DEBUG_MODE:
            cv2.destroyAllWindows()

        print("✅ MongoDB updated")
        print("📦 Resources released")

if __name__ == "__main__":
    main()