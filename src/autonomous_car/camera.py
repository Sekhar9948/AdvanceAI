"""
camera.py

Windows Development Version
Uses laptop webcam for image capture.
Later replace with Raspberry Pi Camera.
"""

import cv2
import os
from datetime import datetime


class Camera:

    def __init__(self):

        self.camera = None

        self.width = 640
        self.height = 480

        self.image_folder = "captured_images"

        os.makedirs(self.image_folder, exist_ok=True)

    def start(self):

        self.camera = cv2.VideoCapture(0)

        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        if not self.camera.isOpened():
            raise Exception("Cannot open webcam")

        print("=================================")
        print(" Camera Started Successfully")
        print("=================================")

    def show_live(self):

        while True:

            ret, frame = self.camera.read()

            if not ret:
                break

            cv2.imshow("AdvanceAI Camera", frame)

            key = cv2.waitKey(1)

            # Press Q to quit
            if key == ord('q'):
                break

            # Press P to capture photo
            if key == ord('p'):
                self.capture(frame)

        self.stop()

    def capture(self, frame=None):

        if frame is None:

            ret, frame = self.camera.read()

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

        if self.camera is not None:
            self.camera.release()

        cv2.destroyAllWindows()

        print("Camera Closed")


if __name__ == "__main__":

    cam = Camera()

    cam.start()

    cam.show_live()