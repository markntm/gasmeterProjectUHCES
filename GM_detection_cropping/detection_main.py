from ultralytics import YOLO
import cv2

model = YOLO("runs/detect/train/weights/best.pt")
results = model("test_meter.jpg")
