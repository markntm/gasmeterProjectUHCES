from ultralytics import YOLO
from secret import GMmodelV1
import cv2
from inference_sdk import InferenceHTTPClient


model = YOLO("runs/detect/train/weights/best.pt")
results = model("test_meter.jpg")


# create an inference client
CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="YOUR_API_KEY"
)

# run inference on a local image
print(CLIENT.infer(
    "your_image.jpg",
    model_id="gauges_object_detection-9smis/2"
))


