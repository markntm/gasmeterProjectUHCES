from secret import *
import cv2
import requests


# Model Configuration
API_KEY = GM_API
API_URL = f"https://detect.roboflow.com/{GM_ID}"


def print_results(result):
    # Outputting Detection Results
    if "predictions" in result:
        for pred in result["predictions"]:
            print(f"Detected {pred['class']} at ({pred['x']}, {pred['y']}) "
                  f"with confidence {pred['confidence']:.2f}")


# @TODO make it so it can read a 5 gauge meter
def filter_y_outliers(boxes, tolerance):
    # Removes boxes whose y1 coordinate is too far from the median y1 value.
    if not boxes:
        return []
    y_values = [b["y1"] for b in boxes]
    median_y = sorted(y_values)[len(y_values)//2]
    return [b for b in boxes if abs(b["y1"] - median_y) <= tolerance]


def d_main(image_path, y_tolerance_ratio=0.3):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    with open(image_path, "rb") as f:
        response = requests.post(
            API_URL,
            params={"api_key": API_KEY},
            files={"file": f},
        )
    result = response.json()
    print(result)
    print_results(result)

    predictions = result.get("predictions", [])
    if not predictions:
        print("No gauges detected.")
        return []

    # Extract bounding boxes and sort them by x-coordinate (rightmost first)
    boxes = []
    height, width = image.shape[:2]
    for pred in predictions:
        x_center, y_center = pred["x"], pred["y"]
        w, h = pred["width"], pred["height"]

        # Convert (x, y, w, h) to corner coordinates
        x1 = int(max(0, x_center - w / 2))
        y1 = int(max(0, y_center - h / 2))
        x2 = int(min(width, x_center + w / 2))
        y2 = int(min(height, y_center + h / 2))

        boxes.append({
            "x1": x1, "y1": y1, "x2": x2, "y2": y2,
        })

    # Filter vertically misaligned detections
    y_tolerance = int(height * y_tolerance_ratio)
    boxes = filter_y_outliers(boxes, y_tolerance)

    if not boxes:
        print("No horizontally aligned gauges found.")
        return []

    # Sort by x-coordinate (rightmost to leftmost)
    boxes.sort(key=lambda b: b["x1"], reverse=True)

    # Crop gauges
    cropped_gauges = []
    for i, b in enumerate(boxes):
        crop = image[b["y1"]:b["y2"], b["x1"]:b["x2"]]
        cropped_gauges.append(crop)
        cv2.imwrite(f"cropped_gauge_{i}.png", crop)  # optional debug output

    print(f"Detected and cropped {len(cropped_gauges)} gauges.")
    return cropped_gauges
