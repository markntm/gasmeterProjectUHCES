from secret import *
import cv2
import requests


# Model Configuration
API_KEY = GM_API
API_URL = f"https://detect.roboflow.com/{GM_ID}"


def print_results(result):
    """Outputting Detection Results"""
    if "predictions" in result:
        for pred in result["predictions"]:
            print(f"Detected {pred['class']} at ({pred['x']}, {pred['y']}) "
                  f"with confidence {pred['confidence']:.2f}")


def four_gauge_filter(boxes, tolerance):
    """Working 4 gauge straight filter: Removes boxes whose y1 coordinate is too far from the median y1 value."""
    if not boxes:
        return []
    y_values = [b["y1"] for b in boxes]
    median_y = sorted(y_values)[len(y_values)//2]
    row = [b for b in boxes if abs(b["y1"] - median_y) <= tolerance]
    return sorted(row, key=lambda b: b["x1"], reverse=True)


def sketchy_five_gauge_filter(boxes, tolerance):
    """Working 5 gauge filter"""
    if not boxes:
        return []
    y_values = [b["y1"] for b in boxes]
    median_y = sorted(y_values)[len(y_values)//2]
    row = [b for b in boxes if abs(b["y1"] - median_y) <= tolerance]
    sorted_row = sorted(row, key=lambda b: b["x1"], reverse=True)
    if len(sorted_row) >= 2:
        sorted_row[-1], sorted_row[-2] = sorted_row[-2], sorted_row[-1]
    return sorted_row


def five_gauge_filter(boxes, tolerance):
    """Not working 5 gauge filter"""
    if not boxes or len(boxes) < 5:
        return []
    y_values = [b["y1"] for b in boxes]
    median_y = sorted(y_values)[len(y_values)//2]
    top_row = [b for b in boxes if abs(b["y1"] - median_y) <= tolerance]
    bottom_row = [b for b in boxes if b["y1"] - median_y > tolerance]
    if len(top_row) != 4 or len(bottom_row) == 0:
        # Fallback: if detection is off, return the 5 boxes sorted by x
        if len(top_row):
            print("More or less than four gauges detected: Top Row.")
        else:
            print("Zero gauges detected: Bottom Row.")
        return sorted(boxes, key=lambda b: b["x1"])

    top_row_sorted = sorted(top_row, key=lambda b: b["x1"])
    ten6gauge = top_row_sorted[0]
    print(ten6gauge["x1"])
    bottom_gauge = min(bottom_row, key=lambda b: abs(b["x1"] - ten6gauge["x1"]))
    gauges_ordered = top_row_sorted[::-1].append(bottom_gauge)
    # gauges_ordered.insert(-1, bottom_gauge)
    return gauges_ordered


def d_main(image_path, filter_type, debug, y_tolerance_ratio=0.065):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    # Run API Model
    with open(image_path, "rb") as f:
        response = requests.post(
            API_URL,
            params={"api_key": API_KEY},
            files={"file": f},
        )
    result = response.json()
    # print(result)
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
    if filter_type == 5:
        boxes = sketchy_five_gauge_filter(boxes, y_tolerance)
    elif filter_type == 4:
        boxes = four_gauge_filter(boxes, y_tolerance)

    if not boxes:
        print("No horizontally aligned gauges found.")
        return []

    # Crop gauges
    cropped_gauges = []
    for i, b in enumerate(boxes):
        crop = image[b["y1"]:b["y2"], b["x1"]:b["x2"]]
        cropped_gauges.append(crop)
        if debug:
            cv2.imwrite(f"cropped_gauge_{i}.png", crop) # optional debug output

    print(f"\nDetected and cropped {len(cropped_gauges)} gauges.\n")
    return cropped_gauges
