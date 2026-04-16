# Camera configuration
CAMERA_INDEX = 0

FRAME_WIDTH = 960
FRAME_HEIGHT = 540

USE_ROI = True 

# ROI SETTINGS 
ROI_X1_RATIO = 0.45  # 35% from left
ROI_X2_RATIO = 0.98  # 98% from left
ROI_Y1_RATIO = 0.10  # 20% from top
ROI_Y2_RATIO = 0.98  # 98% from top


# MongoDB Atlas Configuration
MONGO_URI = (
    "mongodb+srv://shin104051_db_user:uaIrqrgzc061Jc5v@cluster1.cawpy2t.mongodb.net/?appName=Cluster1"
)
DB_NAME = "iRTMS"

# RYZEN 5 OR I5
# MAX_AGE = 20
# MIN_HITS = 3
# IOU_THRESHOLD = 0.3
# MAX_COSINE_DISTANCE = 0.4
# NN_BUDGET = 50
# CONFIDENCE_THRESHOLD = 0.5
# FRAME_SKIP = 3
# input_resolution = 640*360

# RYZEN 7
# MAX_AGE = 40
# MIN_HITS = 5
# MAX_COSINE_DISTANCE = 0.3
# NN_BUDGET = 100
# FRAME_SKIP = 1

# Parvathi & Aarthi
# MODEL_PATH = yolov8s.pt
# IMAGE_SIZE  = 640
# CONFIDENCE_THRESHOLD = 0.35
# IOU_THRESHOLD = 0.5
# MAX_DETECTIONS = 50
# DEVICE= "cpu"
# MAX_AGE = 20
# n_init = 3
# IOU_THRESHOLD_TRACK = 0.7
# MAX_COSINE_DISTANCE = 0.2
# NN_BUDGET = 100

# kaviya v8s
# MODEL_PATH = yolov8s.pt
# IMAGE_SIZE = 640
# CONFIDENCE_THRESHOLD = 0.35
# IOU_THRESHOLD= 0.5
# MAX_DETECTIONS = 40
# DEVICE = "cpu"
# MAX_AGE = 15
# n_init = 3
# IOU_THRESHOLD_TRACK = 0.7
# MAX_COSINE_DISTANCE = 0.2
# NN_BUDGET = 50

# Ponce v8s
# MODEL_PATH = yolov8s.pt
# IMAGE_SIZE  = 768        # You can safely use 768
# CONFIDENCE_THRESHOLD = 0.35
# IOU_THRESHOLD = 0.5
# MAX_DETECTIONS = 60
# DEVICE = 0         # GPU
# HALF_PRECISION = True        # Enable FP16 (important for 4GB VRAM)
# MAX_AGE = 25
# n_init = 3
# IOU_THRESHOLD_TRACK = 0.7
# MAX_COSINE_DISTANCE= 0.2
# NN_BUDGET = 100

# ponce v8m
# MODEL_PATH = yolov8m.pt
# IMAGE_SIZE  = 640        # Do NOT go above 640
# CONFIDENCE_THRESHOLD = 0.35
# IOU_THRESHOLD= 0.5
# MAX_DETECTIONS = 50
# DEVICE = 0
# HALF_PRECISION = True
# MAX_AGE = 20
# n_init = 3
# IOU_THRESHOLD_TRACK = 0.7
# MAX_COSINE_DISTANCE = 0.2
# NN_BUDGET = 100

# MADDY
# YOLO SETTINGS
# MODEL_PATH = "yolov8m.pt"
# MODAL_PATH = r"C:\Users\SELVARAGAVAN\OneDrive\Documents\Team3Pro\RUN LOGS\Data3k\runs\detect\train3\weights\best.pt"
# MODEL_PATH = r"C:\Users\SELVARAGAVAN\OneDrive\Documents\Team3Pro\RUN LOGS\Data7k\runs\detect\train\weights\best.pt"
MODEL_PATH = r"C:\Users\SELVARAGAVAN\OneDrive\Documents\Team3Pro\runs\detect\train9\weights\best.pt"
IMAGE_SIZE = 640  
CONFIDENCE_THRESHOLD = 0.30  
IOU_THRESHOLD = 0.5
MAX_DETECTIONS = 40  
DEVICE = 0                    
HALF_PRECISION = True         # Use FP16
TARGET_CLASSES = [0]          
MIN_BOX_AREA = 1500        

# DEEPSORT SETTINGS
MAX_AGE = 30                  
MIN_HITS = 2                  
IOU_THRESHOLD_TRACK = 0.5     
MAX_COSINE_DISTANCE = 0.25
NN_BUDGET = 100

# LINE CROSSING (anti ID-switch)
LINE_POSITION_RATIO = 0.50    
LINE_HYSTERESIS_RATIO = 0.02  
CROSSING_COOLDOWN_FRAMES = 20

INVERT_COUNTING_DIRECTION = True

# SYSTEM SETTINGS
FRAME_SKIP = 1  
INPUT_RESOLUTION = (640, 480) 