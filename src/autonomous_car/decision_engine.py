"""
decision_engine.py

Brain of the AI Autonomous Car
"""

import time

from .motor_controller import MotorController
from .ultrasonic import UltrasonicSensor
from .yolo_detector import YOLODetector


class DecisionEngine:

    def __init__(self):

        print("=" * 50)
        print("Initializing Decision Engine...")
        print("=" * 50)

        self.motor = MotorController()
        self.sensor = UltrasonicSensor()
        self.detector = YOLODetector()

        print("Decision Engine Ready")

    def autonomous_drive(self):

        print("\nStarting Autonomous Drive...\n")

        while True:

            obstacle = self.sensor.obstacle_detected()

            if obstacle:

                self.motor.stop()

                print("Obstacle Found")

                print("Turning Left...")

                self.motor.turn_left()

                time.sleep(2)

            else:

                self.motor.move_forward()

            time.sleep(1)

    def stop_and_detect(self):

        print("\nSTOP Command Received\n")

        self.motor.stop()

        print("Launching AI Detection...")

        self.detector.detect_from_camera()


if __name__ == "__main__":

    car = DecisionEngine()

    while True:

        print("\n========== MENU ==========")
        print("1. Start Autonomous Drive")
        print("2. Stop and Detect Objects")
        print("3. Exit")

        choice = input("Enter Choice : ")

        if choice == "1":

            car.autonomous_drive()

        elif choice == "2":

            car.stop_and_detect()

        elif choice == "3":

            print("Goodbye")

            break

        else:

            print("Invalid Choice")
            