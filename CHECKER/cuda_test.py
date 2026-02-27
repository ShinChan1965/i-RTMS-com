import torch
import cv2
ROI_X1 = 660
ROI_Y1 = 160
ROI_X2 = 1260
ROI_Y2 = 920
frame=1920*1080
print("CUDA Available:", torch.cuda.is_available())
print("GPU Name:", torch.cuda.get_device_name(0))
print(torch.__version__)
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
cv2.rectangle(frame,
              (ROI_X1, ROI_Y1),
              (ROI_X2, ROI_Y2),
              (255, 0, 0), 2)
cv2.imshow(frame)
