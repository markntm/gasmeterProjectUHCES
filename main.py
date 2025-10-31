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
        if i > 4:
            print("ERROR: More than five gauge readings!")
            break
        # when increment is even (True), arrow turns counter-clockwise 0, 1, 2, 3, 4
        final_reading += r_main(gauge, (i % 2 == 0)) * (10 ** (i + 3))

    print(final_reading)
