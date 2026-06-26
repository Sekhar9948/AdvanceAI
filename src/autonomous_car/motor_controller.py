"""
motor_controller.py

Windows Development Version
Simulates motor movement.

Later this file will control
L298N Motor Driver on Raspberry Pi.
"""

import time


class MotorController:

    def __init__(self):

        self.speed = 70
        self.status = "STOPPED"

        print("Motor Controller Initialized")

    def set_speed(self, speed):

        self.speed = speed

        print(f"Speed set to {speed}%")

    def move_forward(self):

        self.status = "FORWARD"

        print(f"Moving Forward | Speed : {self.speed}%")

    def move_backward(self):

        self.status = "BACKWARD"

        print(f"Moving Backward | Speed : {self.speed}%")

    def turn_left(self):

        self.status = "LEFT"

        print("Turning Left")

    def turn_right(self):

        self.status = "RIGHT"

        print("Turning Right")

    def stop(self):

        self.status = "STOPPED"

        print("Car Stopped")

    def emergency_stop(self):

        self.status = "EMERGENCY STOP"

        print("!!! EMERGENCY STOP ACTIVATED !!!")

    def get_status(self):

        return {
            "status": self.status,
            "speed": self.speed
        }


if __name__ == "__main__":

    motor = MotorController()

    motor.set_speed(60)

    time.sleep(1)

    motor.move_forward()

    time.sleep(2)

    motor.turn_left()

    time.sleep(2)

    motor.turn_right()

    time.sleep(2)

    motor.move_backward()

    time.sleep(2)

    motor.stop()

    print()

    print(motor.get_status())