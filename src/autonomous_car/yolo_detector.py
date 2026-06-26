"""
yolo_detector.py

AI Object Detection using YOLOv8
Windows Development Version
"""

import cv2
from ultralytics import YOLO


class YOLODetector:

    def __init__(self):

        print("Loading YOLO Model...")

        self.model = YOLO("yolov8n.pt")

        print("YOLO Model Loaded Successfully")

    def detect_from_camera(self):

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Cannot open webcam")
            return

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            results = self.model(frame)

            annotated = results[0].plot()

            cv2.imshow("AI Object Detection", annotated)

            detected_objects = []

            for box in results[0].boxes:

                class_id = int(box.cls[0])

                object_name = self.model.names[class_id]

                detected_objects.append(object_name)

            if detected_objects:

                print("Detected :", list(set(detected_objects)))

            key = cv2.waitKey(1)

            if key == ord("q"):
                break

        cap.release()

        cv2.destroyAllWindows()


if __name__ == "__main__":

    detector = YOLODetector()

    detector.detect_from_camera()
    