"""
ultrasonic.py

Cross Platform Ultrasonic Sensor

Windows:
    Simulated Distance

Raspberry Pi:
    HC-SR04
"""

import platform
import random
import time

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
# Raspberry Pi GPIO
# -------------------------------------------------

if IS_RASPBERRY_PI:
    from gpiozero import DistanceSensor


# -------------------------------------------------
# Ultrasonic Sensor
# -------------------------------------------------

class UltrasonicSensor:

    def __init__(self):
        """
        Initialize the ultrasonic sensor.
        """

        # Default obstacle threshold (cm)
        self.threshold = 20

        if IS_RASPBERRY_PI:

            # HC-SR04 Connections
            # Trigger -> GPIO5
            # Echo    -> GPIO6

            self.sensor = DistanceSensor(
                echo=6,
                trigger=5,
                max_distance=4
            )

            print()
            print("==============================")
            print(" Raspberry Pi HC-SR04 Ready")
            print("==============================")

        else:

            print()
            print("==============================")
            print(" Windows Simulation Mode")
            print("==============================")

        print("Ultrasonic Sensor Initialized")

    # -------------------------------------------------

    def set_threshold(self, threshold):
        """
        Set obstacle detection threshold (cm).
        """

        self.threshold = max(1, float(threshold))

        print(f"Threshold set to {self.threshold:.1f} cm")

    # -------------------------------------------------

    def get_distance(self):
        """
        Return distance in centimeters.
        """

        if IS_RASPBERRY_PI:

            try:
                distance = self.sensor.distance * 100

            except Exception:
                distance = 400.0

        else:

            # Windows Simulation
            distance = random.randint(5, 100)

        print(f"Distance : {distance:.1f} cm")

        return distance

    # -------------------------------------------------

    def obstacle_detected(self):
        """
        Returns True if obstacle is within threshold.
        """

        distance = self.get_distance()

        if distance <= self.threshold:
            print("Obstacle Detected")
            return True

        print("Path Clear")
        return False

    # -------------------------------------------------

    def cleanup(self):
        """
        Release ultrasonic resources.
        """

        if IS_RASPBERRY_PI:

            try:
                self.sensor.close()

            except Exception:
                pass

        print("Ultrasonic Sensor Closed")

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

    sensor = UltrasonicSensor()

    try:

        while True:

            sensor.obstacle_detected()

            time.sleep(1)

    except KeyboardInterrupt:

        print("\nStopping Ultrasonic Test...")

    finally:

        sensor.cleanup()