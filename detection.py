import cv2
import numpy as np

class CCTVDetector:
    def __init__(self):
        # Load YOLO
        self.net = cv2.dnn.readNet('models/yolov4-tiny.weights', 'models/yolov4-tiny.cfg')
        with open("models/coco.names", "r") as f:
            self.classes = [line.strip() for line in f.readlines()]
        
        # Load Fire Detection
        self.fire_cascade = cv2.CascadeClassifier('models/fire_detection.xml')
        
        # Detection Parameters
        self.danger_objects = ['knife', 'gun', 'pistol', 'fire']
        self.conf_threshold = 0.5
        self.colors = {
            'danger': (0, 0, 255),  # Red
            'normal': (0, 255, 0),   # Green
            'fire': (0, 165, 255)    # Orange
        }

    def detect_objects(self, frame):
        height, width = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1/255, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward(self.net.getUnconnectedOutLayersNames())
        
        all_boxes = []
        all_classes = []
        danger_boxes = []
        
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > self.conf_threshold:
                    # Get bounding box coordinates
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(center_x - w/2)
                    y = int(center_y - h/2)
                    
                    # Store all detections
                    all_boxes.append((x, y, w, h))
                    all_classes.append(class_id)
                    
                    # Check if dangerous
                    if self.classes[class_id] in self.danger_objects:
                        danger_boxes.append((x, y, w, h))

        return all_boxes, all_classes, danger_boxes

    def detect_fire(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return self.fire_cascade.detectMultiScale(gray, 1.1, 5)
    
   
