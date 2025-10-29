from ultralytics import YOLO
from secret import *
import cv2
import requests
import base64
from pathlib import Path


# Model Configuration
API_KEY = GM_API
API_URL = f"https://detect.roboflow.com/{GM_ID}"


# Image Selection
base_dir = Path(__file__).resolve().parent.parent
img_dir = base_dir / "GM_sample_images"
filename = img_dir / "GM2.png"  # <-- put your image path here
image_path = str(filename)


def d_main():
    with open(image_path, "rb") as f:
        response = requests.post(
            API_URL,
            params={"api_key": API_KEY},
            files={"file": f},
        )


    # Parse Output
    result = response.json()
    print(result)


    # Outputting Detection Results
    if "predictions" in result:
        for pred in result["predictions"]:
            print(f"Detected {pred['class']} at ({pred['x']}, {pred['y']}) "
                  f"with confidence {pred['confidence']:.2f}")


    # Visual Output
    img = cv2.imread(image_path)

    for pred in result["predictions"]:
        x, y, w, h = int(pred["x"]), int(pred["y"]), int(pred["width"]), int(pred["height"])
        cv2.rectangle(img, (x - w//2, y - h//2), (x + w//2, y + h//2), (0, 255, 0), 2)
        cv2.putText(img, f"{pred['class']} {pred['confidence']:.2f}",
                    (x - w//2, y - h//2 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("Detection", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
