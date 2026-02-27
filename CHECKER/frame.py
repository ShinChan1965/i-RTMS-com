import cv2

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Better for Windows

# Probe max
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 4096)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Max supported: {width} x {height}")

ret, frame = cap.read()
if ret:
    print(f"Confirmed: {frame.shape[1]} x {frame.shape[0]}")

cap.release()
