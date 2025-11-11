from pathlib import Path
from time import sleep
import datetime

# from RP_Camera.capture import CameraController
from GM_reading.reading_main import r_main
from GM_detection_cropping.detection_main import d_main
from GM_data.db_utilities import *


period = 15  # seconds
gauge_type = 5  # number of gauges to read
debug = False  # output images of the deciphering process

# Define directories
base_dir = Path(__file__).resolve().parent
img_dir = base_dir / "GM_sample_images"  # "GM_captured_images" or "GM_sample_images" for testing


def reading_loop():
    # camera = CameraController(save_dir=str(img_dir))

    try:
        """camera.start()
        filename, capture_time = camera.capture()
        camera.stop()"""

        capture_time = datetime.now()

        # Build file path string for processing
        filepath = img_dir / "GM5.png"  # filename or "GM5.png" for testing
        image_path = str(filepath)

        # Crops and orders all detected gauges on image
        cropped_gauges = d_main(image_path, gauge_type, debug)

        # Reads each gauge in order
        final_reading = r_main(cropped_gauges, gauge_type, debug)

        print(f"\n[{capture_time.strftime('%Y-%m-%d %H:%M:%S')}] " f"Final reading: {final_reading} Cubic Feet.")

        # Add readings to data log
        add_reading(final_reading, timestamp=capture_time, location="test_meter", confidence=None, image_path=image_path, status="success")

    except Exception as e:
        print(f"Error during reading cycle: {e}")

    finally:
        # Ensure camera resources are released properly
        try:
            # camera.stop()
            pass
        except Exception:
            pass


if __name__ == "__main__":
    while True:
        reading_loop()
        sleep(period)
        break
