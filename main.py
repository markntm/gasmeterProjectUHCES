from pathlib import Path
from GM_reading.reading_main import r_main
from GM_detection_cropping.detection_main import d_main


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    img_dir = base_dir / "GM_sample_images"
    filename = img_dir / "GM5.png"  # <-- put your image path here
    image_path = str(filename)
    gauge_type = 0

    # Crops and orders all detected gauges on image.
    cropped_gauges = d_main(image_path, gauge_type)

    # Reads each gauge in order.
    final_reading = r_main(cropped_gauges)

    print(f"\nFinal reading: {final_reading} Cubic Feet.")
