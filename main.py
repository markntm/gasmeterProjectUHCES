from pathlib import Path
from GM_reading.reading_main import r_main
from GM_detection_cropping.detection_main import d_main


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    img_dir = base_dir / "GM_sample_images"
    filename = img_dir / "GM3.png"  # <-- put your image path here
    image_path = str(filename)

    cropped_gauges = d_main(image_path)

    final_reading = 0
    for i, gauge in enumerate(cropped_gauges):
        final_reading += r_main(gauge) * (10 ** (i + 3))

    print(final_reading)
