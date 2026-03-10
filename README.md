project: YOLO-DEEPSORT-BASED INTELLIGENT RURAL TRANSPORT MANAGEMENT SYSTEM

Install python 3.9

Use dedicated gpu processors like RTX 3060 or other
Use usb webcam or laptop cam

To create a virtual environment ->  py -3.9 -m venv venv
To activate a virtual environment  ->  venv\Scripts\activate
To install required packages  ->  pip install -r requirements.txt   (or) python -m pip install -r requirements.txt

Run as -> python main.py      (can run on both deployment and development mode) 
(Take 20-30 secs to run)

Description:
AI-based Passenger Detection, Tracking, and Counting System for improving rural transport monitoring using Computer Vision and Machine Learning.
The system detects passengers using YOLOv8 and tracks them with DeepSORT to maintain unique IDs and prevent duplicate counting.

Features
1. Real-time passenger detection
2. Multi-object tracking with stable IDs
3. Automated passenger counting
4. Works with live webcam or CCTV feed
5. Designed for rural transport monitoring systems

Camera Input
     ↓
Frame Capture (OpenCV)
     ↓
YOLOv8 Person Detection
     ↓
Bounding Boxes
     ↓
DeepSORT Tracking
     ↓
Unique Track IDs
     ↓
Passenger Counting
     ↓
Real-time Visualization

