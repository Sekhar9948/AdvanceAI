import customtkinter as ctk
import threading
import time

from ..utils.responsive_utils import get_font_size

from ..autonomous_car.camera import Camera
from ..autonomous_car.motor_controller import MotorController
from ..autonomous_car.status import SystemStatus
from ..autonomous_car.command_handler import CommandHandler
from ..autonomous_car.ssh_client import SSHClient


class AutonomousCarScreen(ctk.CTkFrame):

    def __init__(self, parent, theme_manager=None, translator=None):

        self.parent = parent
        self.theme_manager = theme_manager
        self.translator = translator

        bg = "#1E1E1E"

        if self.theme_manager:
            bg = self.theme_manager.get_color("bg_color")

        super().__init__(
            parent,
            fg_color=bg,
            corner_radius=0
        )

        ###################################################
        # Backend Modules
        ###################################################

        self.camera = Camera()
        self.motor = MotorController()
        self.status = SystemStatus()
        self.commands = CommandHandler()
        self.ssh = SSHClient()

        self.connected = False
        self.running = False

        self.create_ui()

        self.after(1000, self.update_status)

    ##############################################################

    def create_ui(self):

        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )

        self.scroll.pack(
            fill="both",
            expand=True
        )

        ##############################################################

        self.title = ctk.CTkLabel(
            self.scroll,
            text="🚗 Autonomous AI Car",
            font=ctk.CTkFont(
                size=get_font_size(28),
                weight="bold"
            )
        )

        self.title.pack(
            anchor="w",
            padx=20,
            pady=(20,10)
        )

        ##############################################################

        self.subtitle = ctk.CTkLabel(
            self.scroll,
            text="Raspberry Pi Autonomous Vehicle Control Center",
            font=ctk.CTkFont(
                size=get_font_size(14)
            )
        )

        self.subtitle.pack(
            anchor="w",
            padx=20,
            pady=(0,20)
        )

        ##############################################################

        self.status_frame = ctk.CTkFrame(
            self.scroll,
            corner_radius=12
        )

        self.status_frame.pack(
            fill="x",
            padx=20,
            pady=10
        )

        self.status_frame.grid_columnconfigure((0,1,2,3),weight=1)

        ##############################################################

        self.camera_status = self.create_status_card(
            self.status_frame,
            "📷 Camera",
            "READY",
            0
        )

        self.motor_status = self.create_status_card(
            self.status_frame,
            "🚙 Motors",
            "STOPPED",
            1
        )

        self.ai_status = self.create_status_card(
            self.status_frame,
            "🤖 YOLO",
            "READY",
            2
        )

        self.ssh_status = self.create_status_card(
            self.status_frame,
            "📡 SSH",
            "OFFLINE",
            3
        )

        ##############################################################

        self.control_frame = ctk.CTkFrame(
            self.scroll,
            corner_radius=12
        )

        self.control_frame.pack(
            fill="x",
            padx=20,
            pady=20
        )

        self.control_frame.grid_columnconfigure((0,1,2),weight=1)

        ##############################################################

        self.connect_button = ctk.CTkButton(
            self.control_frame,
            text="Connect Raspberry Pi",
            height=45,
            command=self.connect_pi
        )

        self.connect_button.grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="ew"
        )

        ##############################################################

        self.start_button = ctk.CTkButton(
            self.control_frame,
            text="▶ Start",
            height=45,
            command=self.start_car
        )

        self.start_button.grid(
            row=0,
            column=1,
            padx=10,
            pady=10,
            sticky="ew"
        )

        ##############################################################

        self.stop_button = ctk.CTkButton(
            self.control_frame,
            text="⏹ Stop",
            height=45,
            command=self.stop_car
        )

        self.stop_button.grid(
            row=0,
            column=2,
            padx=10,
            pady=10,
            sticky="ew"
        )

        ##############################################################

        self.photo_button = ctk.CTkButton(
            self.control_frame,
            text="📸 Take Photo",
            height=45,
            command=self.take_photo
        )

        self.photo_button.grid(
            row=1,
            column=0,
            padx=10,
            pady=10,
            sticky="ew"
        )

        ##############################################################

        self.detect_button = ctk.CTkButton(
            self.control_frame,
            text="🤖 Detect Objects",
            height=45,
            command=self.detect_objects
        )

        self.detect_button.grid(
            row=1,
            column=1,
            padx=10,
            pady=10,
            sticky="ew"
        )

        ##############################################################

        self.status_button = ctk.CTkButton(
            self.control_frame,
            text="📊 System Status",
            height=45,
            command=self.show_status
        )

        self.status_button.grid(
            row=1,
            column=2,
            padx=10,
            pady=10,
            sticky="ew"
        )

        ##############################################################

        self.log_title = ctk.CTkLabel(
            self.scroll,
            text="System Console",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        )

        self.log_title.pack(
            anchor="w",
            padx=20,
            pady=(20,5)
        )

        ##############################################################

        self.console = ctk.CTkTextbox(
            self.scroll,
            height=250
        )

        self.console.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0,20)
        )

        self.log("===================================")
        self.log(" AdvanceAI Autonomous Car ")
        self.log("===================================")
        self.log("System Initialized")

            ##############################################################

    def create_status_card(self, parent, title, value, column):

        frame = ctk.CTkFrame(
            parent,
            corner_radius=10
        )

        frame.grid(
            row=0,
            column=column,
            padx=10,
            pady=10,
            sticky="nsew"
        )

        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(
                size=get_font_size(14),
                weight="bold"
            )
        )

        title_label.pack(
            pady=(15,5)
        )

        value_label = ctk.CTkLabel(
            frame,
            text=value,
            font=ctk.CTkFont(
                size=get_font_size(18),
                weight="bold"
            )
        )

        value_label.pack(
            pady=(0,15)
        )

        return value_label

    ##############################################################

    def log(self, message):

        current_time = time.strftime("%H:%M:%S")

        self.console.insert(
            "end",
            f"[{current_time}] {message}\n"
        )

        self.console.see("end")

    ##############################################################

    def connect_pi(self):

        self.log("Connecting to Raspberry Pi...")

        try:

            host = "192.168.1.10"

            username = "pi"

            password = "raspberry"

            connected = self.ssh.connect(
                host,
                username,
                password
            )

            if connected:

                self.connected = True

                self.ssh_status.configure(
                    text="ONLINE"
                )

                self.log("SSH Connected Successfully")

            else:

                self.log("Connection Failed")

        except Exception as e:

            self.log(str(e))

    ##############################################################

    def start_car(self):

        self.log("Starting Autonomous Car")

        self.running = True

        self.motor.move_forward()

        self.motor_status.configure(
            text="MOVING"
        )

        threading.Thread(
            target=self.commands.execute,
            args=("START",),
            daemon=True
        ).start()

    ##############################################################

    def stop_car(self):

        self.log("Stopping Vehicle")

        self.running = False

        self.motor.stop()

        self.motor_status.configure(
            text="STOPPED"
        )

        threading.Thread(
            target=self.commands.execute,
            args=("STOP",),
            daemon=True
        ).start()

    ##############################################################

    def take_photo(self):

        self.log("Opening Camera")

        try:

            image = self.camera.capture()

            self.log(f"Saved : {image}")

        except Exception as e:

            self.log(str(e))

    ##############################################################

    def detect_objects(self):

        self.log("Launching YOLO Detector")

        self.ai_status.configure(
            text="RUNNING"
        )

        threading.Thread(

            target=self.commands.execute,

            args=("PHOTO",),

            daemon=True

        ).start()

    ##############################################################

    def show_status(self):

        info = self.status.get_system_info()

        self.log("--------------------------------")

        self.log("SYSTEM STATUS")

        self.log("--------------------------------")

        for key, value in info.items():

            self.log(f"{key} : {value}")

        self.log("--------------------------------")

    ##############################################################

    def update_status(self):

        try:

            car = self.status.get_car_status()

            self.camera_status.configure(
                text=car["Camera"]
            )

            self.motor_status.configure(
                text=car["Motor"]
            )

            self.ai_status.configure(
                text=car["AI Model"]
            )

            self.ssh_status.configure(
                text=car["SSH"]
            )

        except:

            pass

        self.after(
            1000,
            self.update_status
        )

            ##############################################################
    # Disconnect Raspberry Pi
    ##############################################################

    def disconnect_pi(self):

        self.log("Disconnecting Raspberry Pi...")

        try:

            self.ssh.disconnect()

            self.connected = False

            self.ssh_status.configure(
                text="OFFLINE"
            )

            self.log("Disconnected Successfully")

        except Exception as e:

            self.log(str(e))

    ##############################################################
    # Emergency Stop
    ##############################################################

    def emergency_stop(self):

        self.log("!!! EMERGENCY STOP !!!")

        try:

            self.running = False

            self.motor.emergency_stop()

            self.motor_status.configure(
                text="EMERGENCY"
            )

            self.commands.execute("STOP")

        except Exception as e:

            self.log(str(e))

    ##############################################################
    # Live Camera Preview
    ##############################################################

    def open_live_camera(self):

        self.log("Opening Live Camera")

        try:

            threading.Thread(

                target=self.camera.show_live,

                daemon=True

            ).start()

        except Exception as e:

            self.log(str(e))

    ##############################################################
    # Run Object Detection
    ##############################################################

    def run_ai_detection(self):

        self.log("Running Object Detection")

        try:

            threading.Thread(

                target=self.detect_objects,

                daemon=True

            ).start()

        except Exception as e:

            self.log(str(e))

    ##############################################################
    # Clear Console
    ##############################################################

    def clear_console(self):

        self.console.delete(
            "1.0",
            "end"
        )

    ##############################################################
    # Write Banner
    ##############################################################

    def write_banner(self):

        self.console.delete(
            "1.0",
            "end"
        )

        self.log("======================================")
        self.log(" AdvanceAI Autonomous Car Dashboard ")
        self.log("======================================")
        self.log("Ready...")
        self.log("")

    ##############################################################
    # Enable Buttons
    ##############################################################

    def enable_controls(self):

        self.start_button.configure(state="normal")
        self.stop_button.configure(state="normal")
        self.photo_button.configure(state="normal")
        self.detect_button.configure(state="normal")
        self.status_button.configure(state="normal")

    ##############################################################
    # Disable Buttons
    ##############################################################

    def disable_controls(self):

        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="disabled")
        self.photo_button.configure(state="disabled")
        self.detect_button.configure(state="disabled")
        self.status_button.configure(state="disabled")

    ##############################################################
    # Update Theme
    ##############################################################

    def update_theme(self, theme):

        if self.theme_manager is None:
            return

        self.configure(
            fg_color=self.theme_manager.get_color("bg_color")
        )

        self.scroll.configure(
            fg_color="transparent"
        )

    ##############################################################
    # Screen Open
    ##############################################################

    def on_show(self):

        self.log("Autonomous Car Screen Opened")

    ##############################################################
    # Screen Close
    ##############################################################

    def on_hide(self):

        self.log("Autonomous Car Screen Closed")

        if self.running:

            self.stop_car()

        if self.connected:

            self.disconnect_pi()

    ##############################################################
    # Destructor
    ##############################################################

    def destroy(self):

        try:

            if self.connected:

                self.ssh.disconnect()

        except:

            pass

        super().destroy()