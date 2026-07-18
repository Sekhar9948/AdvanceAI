"""
motor_controller.py

Cross Platform Motor Controller

Supports:
1. Windows Laptop (Simulation)
2. Raspberry Pi 4 + L298N (gpiozero)

Author : AdvanceAI
"""

import platform
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
# Raspberry Pi Libraries
# -------------------------------------------------

if IS_RASPBERRY_PI:
    from gpiozero import Motor


# -------------------------------------------------
# Motor Controller
# -------------------------------------------------

class MotorController:

    def __init__(self):

        self.speed = 70
        self.status = "STOPPED"

        if IS_RASPBERRY_PI:

            # Left Motor
            self.left_motor = Motor(
                forward=23,
                backward=24,
                enable=18,
                pwm=True
            )

            # Right Motor
            self.right_motor = Motor(
                forward=17,
                backward=27,
                enable=19,
                pwm=True
            )

            print("\n===================================")
            print(" Raspberry Pi Motor Ready")
            print("===================================")

        else:

            print("\n===================================")
            print(" Windows Simulation Mode")
            print("===================================")

        print("Motor Controller Initialized")

    # -------------------------------------------------

    def set_speed(self, speed):

        self.speed = max(0, min(100, int(speed)))

        print(f"Speed set to {self.speed}%")

    # -------------------------------------------------

    def move_forward(self):

        self.status = "FORWARD"

        if IS_RASPBERRY_PI:

            speed = self.speed / 100

            self.left_motor.forward(speed)
            self.right_motor.forward(speed)

        print(f"Moving Forward | Speed : {self.speed}%")

    # -------------------------------------------------

    def move_backward(self):

        self.status = "BACKWARD"

        if IS_RASPBERRY_PI:

            speed = self.speed / 100

            self.left_motor.backward(speed)
            self.right_motor.backward(speed)

        print(f"Moving Backward | Speed : {self.speed}%")

    # -------------------------------------------------

    def turn_left(self):

        self.status = "LEFT"

        if IS_RASPBERRY_PI:

            speed = self.speed / 100

            self.left_motor.backward(speed)
            self.right_motor.forward(speed)

        print(f"Turning Left | Speed : {self.speed}%")

    # -------------------------------------------------

    def turn_right(self):

        self.status = "RIGHT"

        if IS_RASPBERRY_PI:

            speed = self.speed / 100

            self.left_motor.forward(speed)
            self.right_motor.backward(speed)

        print(f"Turning Right | Speed : {self.speed}%")

    # -------------------------------------------------

    def stop(self):

        self.status = "STOPPED"

        if IS_RASPBERRY_PI:

            self.left_motor.stop()
            self.right_motor.stop()

        print("Car Stopped")

    # -------------------------------------------------

    def emergency_stop(self):

        self.stop()

        self.status = "EMERGENCY STOP"

        print("!!! EMERGENCY STOP ACTIVATED !!!")

    # -------------------------------------------------

    def get_status(self):

        return {
            "status": self.status,
            "speed": self.speed
        }

    # -------------------------------------------------

    def cleanup(self):
        """
        Safely stop motors and release resources.
        """

        self.stop()

        if IS_RASPBERRY_PI:

            try:
                self.left_motor.close()
                self.right_motor.close()
            except Exception:
                pass

        print("Motor Controller Closed")

    # -------------------------------------------------

    def __del__(self):
        """
        Automatically cleanup when object is destroyed.
        """

        try:
            self.cleanup()
        except Exception:
            pass


# =====================================================
# Testing
# =====================================================

if __name__ == "__main__":

    motor = MotorController()

    try:

        print("\n========== MOTOR TEST ==========\n")

        motor.set_speed(40)

        motor.move_forward()
        time.sleep(3)

        motor.turn_left()
        time.sleep(2)

        motor.turn_right()
        time.sleep(2)

        motor.move_backward()
        time.sleep(3)

        motor.stop()

        print("\nStatus:", motor.get_status())

    except KeyboardInterrupt:

        print("\nKeyboard Interrupt")

    finally:

        motor.cleanup()