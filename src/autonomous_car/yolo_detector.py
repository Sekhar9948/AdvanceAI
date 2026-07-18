"""
yolo_detector.py

Cross Platform YOLOv8 Object Detection

Windows:
    OpenCV Webcam

Raspberry Pi:
    Pi Camera Module 3 (Picamera2)
"""

import platform
import cv2

from ultralytics import YOLO

# -------------------------------------------------
# Detect Raspberry Pi
# -------------------------------------------------

IS_RASPBERRY_PI = (
    platform.system() == "Linux"
    and (
        "arm" in platform.machine().lower()
        or "aarch64" in platform.machine().lower()
    )
)

# -------------------------------------------------
# Raspberry Pi Camera
# -------------------------------------------------

if IS_RASPBERRY_PI:
    from picamera2 import Picamera2


# -------------------------------------------------
# YOLO Detector
# -------------------------------------------------

class YOLODetector:

    def __init__(self):

        print()
        print("Loading YOLOv8 Model...")

        self.model = YOLO("yolov8n.pt")

        print("YOLO Model Loaded Successfully")

        if IS_RASPBERRY_PI:

            self.camera = Picamera2()

            config = self.camera.create_preview_configuration(
                main={"size": (640, 480)}
            )

            self.camera.configure(config)

            self.camera.start()

            print("Pi Camera Started")

        else:

            self.camera = cv2.VideoCapture(0)

            if not self.camera.isOpened():
                raise Exception("Cannot open webcam")

            print("Webcam Started")

    # -------------------------------------------------

    def detect_single_frame(self):
        """
        Capture one frame and detect objects.

        Returns:
            annotated_frame, detected_objects
        """

        # -----------------------------
        # Capture Frame
        # -----------------------------

        if IS_RASPBERRY_PI:

            frame = self.camera.capture_array()

            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        else:

            ret, frame = self.camera.read()

            if not ret:
                return None, []

        # -----------------------------
        # Run YOLO
        # -----------------------------

        results = self.model(frame)

        detected_objects = []

        for box in results[0].boxes:

            class_id = int(box.cls[0])

            object_name = self.model.names[class_id]

            detected_objects.append(object_name)

        annotated = results[0].plot()

        return annotated, list(set(detected_objects))

    # -------------------------------------------------

    def detect_from_camera(self):
        """
        Continuous object detection.
        Press Q to quit.
        """

        while True:

            frame, objects = self.detect_single_frame()

            if frame is None:

                print("Camera Error")

                break

            cv2.imshow("AI Object Detection", frame)

            if objects:
                print("Detected :", objects)

            key = cv2.waitKey(1)

            if key & 0xFF == ord("q"):
                break

        self.cleanup()

    # -------------------------------------------------

    def cleanup(self):
        """
        Release camera resources.
        """

        if IS_RASPBERRY_PI:

            try:
                self.camera.stop()
            except Exception:
                pass

        else:

            try:
                self.camera.release()
            except Exception:
                pass

        cv2.destroyAllWindows()

        print("YOLO Detector Closed")

    # -------------------------------------------------

    def __del__(self):
        """
        Automatic cleanup.
        """

        try:
            self.cleanup()
        except Exception:
            pass


# =====================================================
# Testing
# =====================================================

if __name__ == "__main__":

    detector = YOLODetector()

    try:

        detector.detect_from_camera()

    except KeyboardInterrupt:

        print("\nStopping YOLO Detector...")

    finally:

        detector.cleanup()