import cv2
import threading
import time

from config.config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT

class VideoStream:
    def __init__(self):
        self.cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

        # USB2 webcams are much smoother with MJPG
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        try:
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass

        self._lock = threading.Lock()
        self._frame = None
        self._running = True

        t = threading.Thread(target=self._reader, daemon=True)
        t.start()

    def _reader(self):
        while self._running:
            ok, frame = self.cap.read()
            if not ok:
                time.sleep(0.01)
                continue
            with self._lock:
                self._frame = frame

    def read(self):
        with self._lock:
            if self._frame is None:
                return None
            return self._frame.copy()

    def release(self):
        self._running = False
        self.cap.release()

# import cv2
# from config.config import FRAME_WIDTH, FRAME_HEIGHT

# class VideoStream:
#     def __init__(self):
#         self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)     #self.cap = camera object for THIS VideoStream. 

#     def read(self):
#         ret, frame = self.cap.read()
#         if not ret:
#             return None

#         frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
#         return frame

#     def release(self):
#         self.cap.release()