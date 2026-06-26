"""
status.py

System Status Monitor
"""

import platform
import psutil
import datetime


class SystemStatus:

    def __init__(self):

        self.camera_status = "READY"
        self.motor_status = "STOPPED"
        self.sensor_status = "READY"
        self.ai_status = "READY"
        self.ssh_status = "DISCONNECTED"

    def get_system_info(self):

        return {

            "Operating System": platform.system(),

            "OS Version": platform.version(),

            "Processor": platform.processor(),

            "CPU Usage": f"{psutil.cpu_percent()} %",

            "RAM Usage": f"{psutil.virtual_memory().percent} %",

            "Current Time": datetime.datetime.now().strftime("%H:%M:%S")

        }

    def get_car_status(self):

        return {

            "Camera": self.camera_status,

            "Motor": self.motor_status,

            "Ultrasonic": self.sensor_status,

            "AI Model": self.ai_status,

            "SSH": self.ssh_status

        }

    def display(self):

        print("\n==============================")
        print("SYSTEM INFORMATION")
        print("==============================")

        system = self.get_system_info()

        for key, value in system.items():

            print(f"{key} : {value}")

        print("\n==============================")
        print("CAR STATUS")
        print("==============================")

        car = self.get_car_status()

        for key, value in car.items():

            print(f"{key} : {value}")


if __name__ == "__main__":

    status = SystemStatus()

    status.display()
    