from ultralytics import YOLO
import cv2
import time

model = YOLO("yolov8m.pt")
model.to("cuda")

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    start = time.time()
    
    model(frame, imgsz=640)
    
    end = time.time()
    print("Inference time:", end - start)