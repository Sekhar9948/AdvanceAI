"""
command_handler.py

Handles all commands for the Autonomous Car.
"""

from .decision_engine import DecisionEngine


class CommandHandler:

    def __init__(self):

        self.car = DecisionEngine()

        print("Command System Ready")

    def execute(self, command):

        command = command.upper()

        if command == "START":

            print("\nStarting Autonomous Car...\n")

            self.car.autonomous_drive()

        elif command == "STOP":

            print("\nStopping Car...\n")

            self.car.motor.stop()

        elif command == "PHOTO":

            print("\nTaking Photo...\n")

            self.car.detector.detect_from_camera()

        elif command == "LEFT":

            self.car.motor.turn_left()

        elif command == "RIGHT":

            self.car.motor.turn_right()

        elif command == "FORWARD":

            self.car.motor.move_forward()

        elif command == "BACKWARD":

            self.car.motor.move_backward()

        elif command == "STATUS":

            print(self.car.motor.get_status())

        else:

            print("Unknown Command")


if __name__ == "__main__":

    commands = CommandHandler()

    while True:

        print("\n==============================")
        print("AI Autonomous Car Commands")
        print("==============================")

        print("START")
        print("STOP")
        print("FORWARD")
        print("BACKWARD")
        print("LEFT")
        print("RIGHT")
        print("PHOTO")
        print("STATUS")
        print("EXIT")

        cmd = input("\nEnter Command : ")

        if cmd.upper() == "EXIT":
            break

        commands.execute(cmd)
        