from picamera2 import Picamera2, Preview
from datetime import datetime
import os


class CameraController:
    def __init__(self, save_dir="", resolution=(3280, 2464)):
        # Upon making the instance, ensures it has a dir to save images
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

        # Initializes camera
        self.picam2 = Picamera2()
        self.resolution = resolution

        # Configue camera for resolution and still image capture
        config = self.picam2.create_still_configuration(main={"size": resolution})
        self.picam2.configure(config)
        self.picam2 = None

        print(f"Camera initialized at {resolution[0]}x{resolution[1]}")

    def start(self):
        """Start the camera and capture the image"""
        if self.picam2 is None:
            self.picam2 = Picamera2()
            config = self.picam2.create_still_configuration(main={"size": self.resolution})
            self.picam2.configure(config)
            self.picam2.start()
            print("Camera powered on.")

    def capture(self, filename=None):
        """Captures a single image and saves it to a file at 'filename'"""
        capture_time = datetime.now()
        # Recalls or sets directory to place captured images
        if filename is None:
            filename = "GMCapture_" + capture_time.strftime("%Y%m%d_%H%M%S") + ".jpg"
        filepath = os.path.join(self.save_dir, filename)

        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            print(f"Created directory: {self.save_dir}")

        self.picam2.capture_file(filepath)
        print(f"Captured image saved at: {filename}")
        return filepath, capture_time

    def stop(self):
        """Stop the camera"""
        if self.picam2:
            self.picam2.stop()
            self.picam2 = None
            print("Camera powered off.")

    def set_resolution(self, width=3280, height=2464):
        """Manually set the resolution of the camera"""
        self.resolution = (width, height)
        self.picam2.stop()
        config = self.picam2.create_still_configuration(main={"size": self.resolution})
        self.picam2.configure(config)
        self.picam2.start()
        print(f"Resolution changed to {width}x{height}")