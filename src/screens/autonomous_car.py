import customtkinter as ctk

from ..utils.responsive_utils import get_font_size
from src.autonomous_car.ssh_client import SSHClient
from src.autonomous_car.status import SystemStatus
from src.autonomous_car.car_commands import CarCommands
from src.autonomous_car.camera import Camera


class AutonomousCarScreen(ctk.CTkFrame):

    def __init__(self, parent, theme_manager=None, translator=None):

        self.theme_manager = theme_manager
        self.translator = translator

        bg = "#1E1E1E"

        if theme_manager:
            bg = theme_manager.get_color("bg_color")

        super().__init__(
            parent,
            fg_color=bg,
            corner_radius=0
        )

        self.create_ui()

    ###########################################################

    def create_ui(self):

        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )

        self.scroll.pack(fill="both", expand=True)

        #######################################################

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
            pady=(20, 10)
        )

        #######################################################

        self.subtitle = ctk.CTkLabel(
            self.scroll,
            text="Control and monitor your AI Autonomous Vehicle",
            font=ctk.CTkFont(size=get_font_size(14))
        )

        self.subtitle.pack(
            anchor="w",
            padx=20,
            pady=(0, 20)
        )

        #######################################################

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

        #######################################################

        self.camera_status = self.create_status_card(
            self.status_frame,
            "📷 Camera",
            "Ready",
            0
        )

        self.motor_status = self.create_status_card(
            self.status_frame,
            "🚙 Motor",
            "Stopped",
            1
        )

        self.ai_status = self.create_status_card(
            self.status_frame,
            "🤖 YOLO",
            "Offline",
            2
        )

        self.ssh_status = self.create_status_card(
            self.status_frame,
            "📡 SSH",
            "Disconnected",
            3
        )

        #######################################################

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

        #######################################################

        self.connect_btn = ctk.CTkButton(
            self.control_frame,
            text="Connect Raspberry Pi",
            command=self.connect_pi
        )

        self.connect_btn.grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="ew"
        )

        #######################################################

        self.start_btn = ctk.CTkButton(
            self.control_frame,
            text="▶ Start Car",
            command=self.start_car
        )

        self.start_btn.grid(
            row=0,
            column=1,
            padx=10,
            pady=10,
            sticky="ew"
        )

        #######################################################

        self.stop_btn = ctk.CTkButton(
            self.control_frame,
            text="⏹ Stop Car",
            command=self.stop_car
        )

        self.stop_btn.grid(
            row=0,
            column=2,
            padx=10,
            pady=10,
            sticky="ew"
        )

        #######################################################

        self.photo_btn = ctk.CTkButton(
            self.control_frame,
            text="📷 Take Photo",
            command=self.take_photo
        )

        self.photo_btn.grid(
            row=1,
            column=0,
            padx=10,
            pady=10,
            sticky="ew"
        )

        #######################################################

        self.detect_btn = ctk.CTkButton(
            self.control_frame,
            text="🤖 Detect Objects",
            command=self.detect_objects
        )

        self.detect_btn.grid(
            row=1,
            column=1,
            padx=10,
            pady=10,
            sticky="ew"
        )

        #######################################################

        self.status_btn = ctk.CTkButton(
            self.control_frame,
            text="📊 System Status",
            command=self.system_status
        )

        self.status_btn.grid(
            row=1,
            column=2,
            padx=10,
            pady=10,
            sticky="ew"
        )

        #######################################################

        self.log_title = ctk.CTkLabel(
            self.scroll,
            text="Console Log",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        )

        self.log_title.pack(
            anchor="w",
            padx=20,
            pady=(10,5)
        )

        #######################################################

        self.console = ctk.CTkTextbox(
            self.scroll,
            height=220
        )

        self.console.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0,20)
        )

        self.log("AdvanceAI Autonomous Car Module Loaded")

    ###########################################################

    def create_status_card(self,parent,title,value,column):

        frame=ctk.CTkFrame(parent,corner_radius=10)

        frame.grid(
            row=0,
            column=column,
            padx=8,
            pady=10,
            sticky="nsew"
        )

        ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=(15,5))

        value_label=ctk.CTkLabel(
            frame,
            text=value
        )

        value_label.pack(pady=(0,15))

        return value_label

    ###########################################################

    def log(self,message):

        self.console.insert("end",message+"\n")

        self.console.see("end")

    ###########################################################

    def connect_pi(self):

        self.log("Connecting Raspberry Pi...")

    def start_car(self):

        self.log("Starting Autonomous Car...")

    def stop_car(self):

        self.log("Stopping Car...")

    def take_photo(self):

        self.log("Capturing Image...")

    def detect_objects(self):

        self.log("Running YOLO Detection...")

    def system_sta
    \7888888888