import cv2
import time

video = cv2.VideoCapture(0)  # 0 for default camera
num_frames = 120
start = time.time()

for i in range(num_frames):
    ret, frame = video.read()

end = time.time()
seconds = end - start
fps = num_frames / seconds
print(f"Estimated FPS: {fps}")

video.release()
