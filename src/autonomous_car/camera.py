"""
camera.py

Cross Platform Camera Module

Supports:
1. Windows Laptop Webcam
2. Raspberry Pi Camera Module (Picamera2)

Automatically detects the platform.
"""

import cv2
import os
import platform
from datetime import datetime

IS_RASPBERRY_PI = (
    platform.system() == "Linux"
    and ("arm" in platform.machine().lower()
         or "aarch64" in platform.machine().lower())
)

if IS_RASPBERRY_PI:
    from picamera2 import Picamera2


class Camera:

    def __init__(self):

        self.camera = None
        self.picam2 = None

        self.width = 640
        self.height = 480

        self.image_folder = "captured_images"
        os.makedirs(self.image_folder, exist_ok=True)

    def start(self):

        if IS_RASPBERRY_PI:

            self.picam2 = Picamera2()

            config = self.picam2.create_preview_configuration(
                main={
                    "size": (self.width, self.height)
                }
            )

            self.picam2.configure(config)

            self.picam2.start()

            print("=================================")
            print(" Raspberry Pi Camera Started")
            print("=================================")

        else:

            self.camera = cv2.VideoCapture(0)

            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

            if not self.camera.isOpened():
                raise Exception("Cannot open webcam")

            print("=================================")
            print(" Laptop Camera Started")
            print("=================================")

    def read_frame(self):

        if IS_RASPBERRY_PI:

            frame = self.picam2.capture_array()

            frame = cv2.cvtColor(
                frame,
                cv2.COLOR_RGB2BGR
            )

            return True, frame

        else:

            return self.camera.read()

    def show_live(self):

        while True:

            ret, frame = self.read_frame()

            if not ret:
                break

            cv2.imshow("AdvanceAI Camera", frame)

            key = cv2.waitKey(1)

            if key == ord("q"):
                break

            if key == ord("p"):
                self.capture(frame)

        self.stop()

    def capture(self, frame=None):

        if frame is None:

            ret, frame = self.read_frame()

            if not ret:
                raise Exception("Cannot capture image")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = os.path.join(
            self.image_folder,
            f"image_{timestamp}.jpg"
        )

        cv2.imwrite(filename, frame)

        print(f"Image Saved : {filename}")

        return filename

    def stop(self):

        if IS_RASPBERRY_PI:

            if self.picam2 is not None:
                self.picam2.stop()

        else:

            if self.camera is not None:
                self.camera.release()

        cv2.destroyAllWindows()

        print("Camera Closed")


if __name__ == "__main__":

    cam = Camera()

    cam.start()

    cam.show_live()