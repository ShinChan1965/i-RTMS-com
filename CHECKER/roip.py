import cv2
import numpy as np

# Global variables for ROI selection
drawing = False
roi_pts = []
img_copy = None
video_path = "your_bus_video.mp4"  # Replace with your video file or 0 for webcam
pts = []

def mouse_callback(event, x, y, flags, param):
    global drawing, roi_pts, img_copy
    
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        roi_pts = [(x, y)]
    
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = img.clone()
            cv2.line(img_copy, roi_pts[0], (x, y), (0, 255, 0), 2)
            cv2.imshow('ROI Selector', img_copy)
    
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.rectangle(img_copy, roi_pts[0], (x, y), (0, 255, 0), 2)
        roi_pts.append((x, y))
        print(f"ROI coordinates: top-left={roi_pts[0]}, bottom-right={roi_pts[1]}")
        cv2.imshow('ROI Selector', img_copy)

# Open video
cap = cv2.VideoCapture(video_path)
ret, img = cap.read()
if not ret:
    print("Error loading video")
    exit()

img_copy = img.copy()
clone = img.copy()

cv2.namedWindow('ROI Selector')
cv2.setMouseCallback('ROI Selector', mouse_callback)

print("Instructions:")
print("- Drag mouse to draw ROI rectangle over door")
print("- Press SPACE to confirm ROI and proceed to video")
print("- Press ESC to quit")

while True:
    cv2.imshow('ROI Selector', img_copy)
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord(' '):  # Space: confirm and play video with ROI
        x1, y1 = roi_pts[0]
        x2, y2 = roi_pts[1]
        roi = clone[y1:y2, x1:x2]
        print(f"ROI saved: [{x1}, {y1}, {x2-x1}, {y2-y1}]")
        break
    elif key == 27:  # ESC: quit
        break

cap.release()
cv2.destroyAllWindows()

# Now play video with ROI overlay (fixed continuous stream)
cap = cv2.VideoCapture(video_path)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    if 'roi' in locals():  # Apply ROI if selected
        x1, y1, w, h = roi_pts[0][0], roi_pts[0][1], roi_pts[1][0]-roi_pts[0][0], roi_pts[1][1]-roi_pts[0][1]
        cv2.rectangle(frame, (x1, y1), (x1+w, y1+h), (0, 255, 0), 2)
    
    cv2.imshow('Video with ROI', frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
