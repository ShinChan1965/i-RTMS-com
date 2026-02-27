import cv2

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("X:", x, "Y:", y)

cap = cv2.VideoCapture(0)
ret, frame = cap.read()

cv2.imshow("Frame", frame)
cv2.setMouseCallback("Frame", click_event)
cv2.waitKey(0)
