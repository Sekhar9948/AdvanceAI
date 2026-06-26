"""
ultrasonic.py

Windows Development Version

Simulates HC-SR04 Ultrasonic Sensor.
Later replace with Raspberry Pi GPIO code.
"""

import random
import time


class UltrasonicSensor:

    def __init__(self):

        self.threshold = 20

        print("Ultrasonic Sensor Initialized")

    def get_distance(self):

        distance = random.randint(5, 100)

        print(f"Distance : {distance} cm")

        return distance

    def obstacle_detected(self):

        distance = self.get_distance()

        if distance <= self.threshold:

            print("Obstacle Detected")

            return True

        print("Path Clear")

        return False


if __name__ == "__main__":

    sensor = UltrasonicSensor()

    while True:

        sensor.obstacle_detected()

        time.sleep(2)