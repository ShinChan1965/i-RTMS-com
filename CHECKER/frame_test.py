import cv2

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # try 0, then 1, etc.
if not cap.isOpened():
      print("Could not open camera")
      exit()

while True:
      ok, frame = cap.read()
      if not ok:
          print("Failed to grab frame")
          break
      cv2.imshow("test", frame)
      if cv2.waitKey(1) & 0xFF == ord('q'):
          break

cap.release()
cv2.destroyAllWindows()