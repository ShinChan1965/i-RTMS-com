import cv2
import datetime
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

model = YOLO("yolov8n.pt")  # Use yolov8n.pt for CPU speed
tracker = DeepSort(max_age=30, n_init=3)
cap = cv2.VideoCapture(0)   # Webcam

while True:
    start = datetime.datetime.now()
    
    ret, frame = cap.read()
    if not ret: break
    
    # YOLO Detection
    detections = model(frame, imgsz=416, classes=[0], verbose=False)[0]

    results = []
    for data in detections.boxes.data.tolist():
        conf = data[4]
        if conf > 0.3:
            x, y, w, h = int(data[0]), int(data[1]), int(data[2]-data[0]), int(data[3]-data[1])
            results.append([[x, y, w, h], conf, int(data[5])])
    
    # DeepSORT Tracking
    tracks = tracker.update_tracks(results, frame=frame)
    for track in tracks:
        if not track.is_confirmed(): continue
        ltrb = track.to_ltrb()
        cv2.rectangle(frame, (int(ltrb[0]), int(ltrb[1])), (int(ltrb[2]), int(ltrb[3])), (0,255,0), 2)
        cv2.putText(frame, str(track.track_id), (int(ltrb[0]), int(ltrb[1])-10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,0,0), 2)
    
    # FPS Calculation (end-to-end processing)
    end = datetime.datetime.now()
    ms = (end - start).total_seconds() * 1000
    fps = 1 / (end - start).total_seconds()
    print(f"Processing time: {ms:.0f} ms, FPS: {fps:.1f}")
    
    cv2.putText(frame, f"FPS: {fps:.1f}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 3)
    cv2.imshow("YOLO + DeepSORT", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()
