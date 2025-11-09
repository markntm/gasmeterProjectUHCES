from picamera2 import Picamera2, Preview
from datetime import datetime
import os


class CameraController:
    def __init__(self, save_dir="", resolution=(2592, 1944)):
        # Upon making the instance, ensures it has a dir to save images
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

        # Configures camera for still image capture
        self.picam2 = Picamera2()
        self.resolution = resolution

        config = self.picam2.create_still_configuration(main={"size": resolution})
        self.picam2.configure(config)
        self.picam2 = None

        print(f"Camera initialized at {resolution[0]}x{resolution[1]}")

    def capture(self, filename=None):
        """Captures a single image and saves it to a file at 'filename'"""
        # Recalls or sets directory to place captured images
        if filename is None:
            filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
        filepath = os.path.join(self.save_dir, filename)

        self.picam2.capture_file(filepath)
        print(f"Captured image saved at: {filename}")
        return filepath

    def set_resolution(self, width=2592, height=1944):
        """Manually set the resolution of the camera"""
        self.resolution = (width, height)
        self.picam2.stop()
        config = self.picam2.create_still_configuration(main={"size": self.resolution})
        self.picam2.configure(config)
        self.picam2.start()
        print(f"Resolution changed to {width}x{height}")

    def start(self):
        """Start the camera and capture the image"""
        if self.picam2 is None:
            self.picam2 = Picamera2()
            config = self.picam2.create_still_configuration(main={"size": self.resolution})
            self.picam2.configure(config)
            self.picam2.start()
            print("Camera powered on.")

    def stop(self):
        """Stop the camera"""
        if self.picam2:
            self.picam2.stop()
            self.picam2 = None
            print("Camera powered off.")
