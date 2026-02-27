# AUTO-RESTART + ROI + DEBUG/DEPLOYMENT VERSION
import cv2
import torch
torch.backends.cudnn.benchmark = True
from ultralytics import YOLO

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
)

# MODE SWITCH
DEBUG_MODE = True   # True = Debug | False = Deployment


def main():
    
    # INITIALIZATION
    video = VideoStream()
    tracker = DeepSORTTracker()
    line = LineCrossing(
        line_position_ratio=LINE_POSITION_RATIO,
        hysteresis_ratio=LINE_HYSTERESIS_RATIO,
        cooldown_frames=CROSSING_COOLDOWN_FRAMES,
        invert_direction=INVERT_COUNTING_DIRECTION,
    )
    counter = PassengerCounter()
    model = YOLO(MODEL_PATH)
    yolo = YOLODetector(model)
    current_stop = "Surandai"
    stop_index = 1

    print("🚍 Passenger Counting System Started")

    if DEBUG_MODE:
        print("🧪 Running in DEBUG MODE")
        print("Press 'n' → Next stop | Press 'q' → Quit")
    else:
        print("🚀 Running in DEPLOYMENT MODE (Auto-start)")

    try:
        while True:
            # READ FRAME
            frame = video.read()
            # With threaded capture, we may briefly get None before
            # the first frame arrives; just skip those iterations.
            if frame is None:
                continue
            # Dynamic ROI
            h, w = frame.shape[:2]

            ROI_X1 = int(w * 0.10)
            ROI_X2 = int(w * 0.75)
            ROI_Y1 = int(h * 0.08)
            ROI_Y2 = int(h * 0.97)


            # ROI SELECTION
            if USE_ROI:
                detection_frame = frame[ROI_Y1:ROI_Y2, ROI_X1:ROI_X2]
            else:
                detection_frame = frame

            # YOLO DETECTION
            detections = yolo.detect(detection_frame)
    
            # DEEPSORT TRACKING
            tracks = tracker.update(detections, detection_frame)

            # DRAW VIRTUAL LINE (DEBUG ONLY)
            if DEBUG_MODE:
                line.draw_line(frame)

                # Draw ROI box visually
                if USE_ROI:
                    cv2.rectangle(
                        frame,
                        (ROI_X1, ROI_Y1),
                        (ROI_X2, ROI_Y2),
                        (255, 0, 0),
                        2
                    )

            # PROCESS TRACKS
            for track in tracks:
                if not track.is_confirmed():
                    continue

                track_id = track.track_id
                x1, y1, x2, y2 = map(int, track.to_ltrb())

                # Convert ROI coords back to full frame
                if USE_ROI:
                    x1 += ROI_X1
                    x2 += ROI_X1
                    y1 += ROI_Y1
                    y2 += ROI_Y1

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

                # DEBUG visuals only
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

            # DISPLAY INFO (DEBUG ONLY)
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

            # Advance line-crossing frame index for cooldown
            line.tick()

    except KeyboardInterrupt:
        print("\n🛑 Interrupted")

    finally:
        counter.store_stop_data(current_stop, stop_index)
        video.release()

        if DEBUG_MODE:
            cv2.destroyAllWindows()

        print("✅ MongoDB updated")
        print("📦 Resources released")


if __name__ == "__main__":
    main()