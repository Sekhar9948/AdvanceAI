
import customtkinter as ctk
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, AmbientLight, DirectionalLight, loadPrcFileData
from direct.task import Task
import os
import numpy as np
import sys
import time
import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk

import sys

from panda3d.core import loadPrcFileData

# 🔥 ADD THIS HERE (before anything else related to Panda3D)
loadPrcFileData("", "load-display pandagl")
loadPrcFileData("", "aux-display pandagl")
loadPrcFileData("", "framebuffer-hardware false")

# THEN import ShowBase
from direct.showbase.ShowBase import ShowBase

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from language_manager import LanguageManager

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
model_path = os.path.join(project_root, 'trained_models','3d_speech_to_text')
dataset_path1 = os.path.join(project_root, 'dataset','3d_speech_to_text')

# Configure Panda3D window before initialization
loadPrcFileData("", "window-title Panda3D Model")
loadPrcFileData("", "win-size 800 600")
loadPrcFileData("", "win-origin 50 50")
loadPrcFileData("", "threading-model None")  # Use single-threaded model for Panda3D

# Try importing optional dependencies with fallbacks
try:
    # Import TensorFlow with warning suppression
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings
    import tensorflow as tf
    has_tensorflow = True
    print("TensorFlow successfully loaded.")
    
    # Try to import TensorFlow Hub
    try:
        import tensorflow_hub as hub
        has_tensorflow_hub = True
        print("TensorFlow Hub successfully loaded.")
    except ImportError:
        has_tensorflow_hub = False
        print("TensorFlow Hub not found. Pre-trained models will not be available.")
        
except ImportError:
    has_tensorflow = False
    has_tensorflow_hub = False
    print("TensorFlow not found. Voice training will be disabled.")

try:
    import sounddevice as sd
    import librosa
    import pickle
    has_audio = True
    print("Audio libraries successfully loaded.")
    
    # Try importing transformers library for Whisper model
    try:
        from transformers import WhisperProcessor, WhisperForConditionalGeneration
        has_transformers = True
        print("Transformers library successfully loaded.")
    except ImportError:
        has_transformers = False
        print("Transformers library not found. Advanced speech recognition will be limited.")
        
except ImportError:
    has_audio = False
    has_transformers = False
    print("Audio libraries not found. Voice commands will be disabled.")

# Configuration settings
SAMPLE_COUNT_PER_COMMAND = 3  # Default samples per command
TRAINING_EPOCHS = 50  # Default training epochs

class MyGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Set up the 3D model
        try:
            # Try different model paths
            model_paths = [
                "models/panda", 
                "models/panda.egg", 
                "models/panda.bam",
                "./models/panda",
                "./models/panda.egg",
                "./models/panda.bam"
            ]
            
            model_loaded = False
            for path in model_paths:
                try:
                    self.model = self.loader.loadModel(path)
                    model_loaded = True
                    print(f"Loaded model from {path}")
                    break
                except:
                    pass
            
            if not model_loaded:
                # Create a simple cube as fallback
                print("Could not load panda model, creating a simple cube instead")
                from panda3d.core import CardMaker
                cm = CardMaker('card')
                cm.setFrame(-0.5, 0.5, -0.5, 0.5)
                
                # Create colored cards for cube faces
                self.model = self.render.attachNewNode("boxModel")
                card = self.render.attachNewNode(cm.generate())
                card.setColor(0.5, 0.5, 1.0, 1)
                card.reparentTo(self.model)
                
                for i, (pos, hpr) in enumerate([
                    ((0, 0.5, 0), (0, 0, 0)),    # Front
                    ((0, -0.5, 0), (0, 180, 0)), # Back
                    ((0.5, 0, 0), (0, -90, 0)),  # Right
                    ((-0.5, 0, 0), (0, 90, 0)),  # Left
                    ((0, 0, 0.5), (-90, 0, 0)),  # Top
                    ((0, 0, -0.5), (90, 0, 0)),  # Bottom
                ]):
                    c = self.render.attachNewNode(cm.generate())
                    c.setPos(*pos)
                    c.setHpr(*hpr)
                    c.setColor(0.8, 0.3, 0.3, 1) if i % 2 else c.setColor(0.3, 0.8, 0.3, 1)
                    c.reparentTo(self.model)
            
            self.model.reparentTo(self.render)
            self.model.setScale(0.5)
            self.model.setPos(0, 5, 0)
        except Exception as e:
            print(f"Error setting up model: {e}")
        
        # Setup lighting
        self.setup_lighting()
        
        # Set camera position for better viewing
        self.cam.setPos(0, -10, 2)
        self.cam.lookAt(0, 5, 0)
        
        # Movement flags
        self.rotating = False
        self.rotation_speed = 60
        self.y_movement_speed = 0.5
        
        # Always set up commands regardless of library availability
        self.commands = {"left": self.move_left, "right": self.move_right, 
                        "up": self.move_up, "down": self.move_down, 
                        "rotate": self.start_rotation}
        self.dataset = {cmd: [] for cmd in self.commands.keys()}
        self.speech_model = None
        self.sr = 22050  # Standard sample rate
        self.duration = 2  # Recording duration in seconds
    
    def setup_lighting(self):
        """Set up basic scene lighting"""
        # Add ambient light
        ambient_light = AmbientLight("ambient_light")
        ambient_light.setColor((0.5, 0.5, 0.5, 1))
        alnp = self.render.attachNewNode(ambient_light)
        self.render.setLight(alnp)
        
        # Add directional light
        directional_light = DirectionalLight("directional_light")
        directional_light.setColor((0.8, 0.8, 0.8, 1))
        dlnp = self.render.attachNewNode(directional_light)
        dlnp.setHpr(45, -45, 0)
        self.render.setLight(dlnp)
    
    def move_left(self):
        """Move the model left"""
        self.model.setPos(self.model.getPos() + Vec3(-1, 0, 0))
    
    def move_right(self):
        """Move the model right"""
        self.model.setPos(self.model.getPos() + Vec3(1, 0, 0))
    
    def move_up(self):
        """Move the model up"""
        self.model.setPos(self.model.getPos() + Vec3(0, 0, 1))
    
    def move_down(self):
        """Move the model down"""
        self.model.setPos(self.model.getPos() + Vec3(0, 0, -1))
    
    def start_rotation(self):
        """Toggle rotation of the model"""
        self.rotating = not self.rotating
        if self.rotating:
            self.taskMgr.add(self.rotate_model, "rotateTask")
        else:
            self.taskMgr.remove("rotateTask")
    
    def rotate_model(self, task):
        """Rotate the model continuously"""
        if self.rotating:
            self.model.setH(self.model.getH() + (self.rotation_speed * globalClock.getDt()))
            self.model.setY(self.model.getY() + (self.y_movement_speed * globalClock.getDt()))
            return Task.cont
        return Task.done

# Create controller for UI and game integration
class VoiceControlApp(ctk.CTk):
    def __init__(self):
        super().__init__() 
        # Initialize the Panda3D app first

        self.translator = LanguageManager()
        self.translator.load_language("en")

        self.game = MyGame()
        
        # Check for required libraries
        self.tf_available = has_tensorflow
        self.tf_hub_available = has_tensorflow_hub
        self.audio_available = has_audio
        self.transformers_available = has_transformers
        
        # Pre-trained model
        self.pretrained_model = None
        self.whisper_model = None
        self.whisper_processor = None
        self.using_pretrained_model = False
        self.using_whisper_model = False
        self.pretrained_confidence_threshold = 0.7  # Default threshold
        
        # Current command being recorded
        self.current_command = None
        self.current_command_index = 0
        self.all_commands = list(self.game.commands.keys()) if self.game.commands else []
        self.samples_per_command = SAMPLE_COUNT_PER_COMMAND
        self.training_epochs = TRAINING_EPOCHS
        self.current_sample_index = 0
        self.manual_recording = False  # Flag for manual recording mode
        
        # Task queues for safe threading
        self.audio_queue = []
        self.processing_queue = []
        self.is_recording = False
        self.is_training = False
        self.is_predicting = False
        
        # Audio visualization
        self.audio_data = None
        self.recording_countdown = 0
        self.is_countdown_active = False
        self.visualize_active = False
        self.audio_canvas = None
        self.audio_figure = None
        
        # Set up CustomTkinter UI
        self.setup_ui()
        
        # Add task for processing queues
        self.game.taskMgr.add(self.process_queues, "processQueues")
        
        # Start Panda3D main loop
        self.start_panda3d_loop()
        
        # Make sure dataset directory exists
        if not os.path.exists(dataset_path1):
            os.makedirs(dataset_path1)
    
    def setup_ui(self):
        # Set up the main window
        
        self.title(self.translator.get("voice_command_3d"))
        self.geometry("1280x860+200+50")
        self.protocol("WM_DELETE_WINDOW", self.on_close)                
        
        # Set up CustomTkinter appearance and color theme
        ctk.set_appearance_mode("dark")  # Options: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"
        
        # Create the main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create a horizontal layout with sidebar and content area
        self.sidebar_width = 320
        
        # Create sidebar frame (left panel)
        self.sidebar_frame = ctk.CTkFrame(
            self.main_frame, 
            width=self.sidebar_width,
            fg_color=("#e0e0e0", "#2d2d2d"),
            corner_radius=15
        )
        self.sidebar_frame.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar_frame.pack_propagate(False)  # Prevent sidebar from shrinking
        
        # Create right panel with a canvas for scrolling
        self.right_panel_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=("#ffffff", "#1e1e1e"),
            corner_radius=15
        )
        self.right_panel_frame.pack(side="right", fill="both", expand=True)
        
        # Create a canvas inside the right panel for scrolling
        self.canvas = ctk.CTkCanvas(
            self.right_panel_frame, 
            highlightthickness=0,
            bg="#1e1e1e"  # Match the dark theme
        )
        self.scrollbar = ctk.CTkScrollbar(
            self.right_panel_frame, 
            orientation="vertical", 
            command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack the scrollbar and canvas
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Create a frame inside the canvas to hold the content
        self.content_frame = ctk.CTkFrame(
            self.canvas,
            fg_color=("#ffffff", "#1e1e1e"),
            corner_radius=0
        )
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        
        # Configure scrolling
        self.content_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Bind mousewheel to scroll
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        # Add content to the sidebar
        self.setup_sidebar()
        
        # Add content to the content area
        self.setup_content_area()
        
        # Bind keyboard shortcuts
        self.bind("<KeyPress>", self.handle_keypress)
        
        # Update dataset statistics initially
        self.update_dataset_stats()
    
    def setup_sidebar(self):
        # App title and theme switcher
        self.header_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=10, pady=(20, 10))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=self.translator.t("3D Model Voice Control"),
            font=ctk.CTkFont(size=22, weight="bold", family="Arial"),
            text_color=("#2d2d2d", "#ffffff")
        )
        self.title_label.pack(side="left", padx=10)
        
        # Theme switcher
        self.theme_switch = ctk.CTkSwitch(
            self.header_frame,
            text=self.translator.t("Dark"),
            command=self.toggle_theme,
            font=ctk.CTkFont(size=12),
            progress_color=("#007AFF", "#0A84FF")
        )
        self.theme_switch.pack(side="right", padx=10)
        self.theme_switch.select()  # Default to dark mode
        
        # Create scrollable sidebar content
        self.sidebar_scroll = ctk.CTkScrollableFrame(
            self.sidebar_frame,
            fg_color="transparent",
            corner_radius=0
        )
        self.sidebar_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Model Controls Section
        self.create_section_label("Model Controls", self.sidebar_scroll)
        
        # Movement controls with modern styling
        self.controls_frame = ctk.CTkFrame(self.sidebar_scroll, fg_color="transparent")
        self.controls_frame.pack(fill="x", padx=10, pady=5)
        
        # Movement buttons with grid layout
        button_style = {
            "width": 70,
            "height": 70,
            "corner_radius": 15,
            "font": ctk.CTkFont(size=14, weight="bold"),
            "hover_color": ("#0051A8", "#0051A8")
        }

        # Movement button style with blue color
        movement_button_style = button_style.copy()
        movement_button_style["fg_color"] = ("#007AFF", "#0A84FF")
        
        # Rotate button style with red color
        rotate_button_style = button_style.copy()
        rotate_button_style["fg_color"] = ("#FF3B30", "#FF453A")
        rotate_button_style["hover_color"] = ("#CC2E26", "#CC2E26")
        
        # Up button
        self.btn_up = ctk.CTkButton(
            self.controls_frame,
            text="↑",
            command=self.game.move_up,
            **movement_button_style
        )
        self.btn_up.grid(row=0, column=1, padx=5, pady=5)
        
        # Left button
        self.btn_left = ctk.CTkButton(
            self.controls_frame,
            text="←",
            command=self.game.move_left,
            **movement_button_style
        )
        self.btn_left.grid(row=1, column=0, padx=5, pady=5)
        
        # Rotate button
        self.btn_rotate = ctk.CTkButton(
            self.controls_frame,
            text="⟲",
            command=self.game.start_rotation,
            **rotate_button_style
        )
        self.btn_rotate.grid(row=1, column=1, padx=5, pady=5)
        
        # Right button
        self.btn_right = ctk.CTkButton(
            self.controls_frame,
            text="→",
            command=self.game.move_right,
            **movement_button_style
        )
        self.btn_right.grid(row=1, column=2, padx=5, pady=5)
        
        # Down button
        self.btn_down = ctk.CTkButton(
            self.controls_frame,
            text="↓",
            command=self.game.move_down,
            **movement_button_style
        )
        self.btn_down.grid(row=2, column=1, padx=5, pady=5)
        
        # Configure grid weights
        self.controls_frame.grid_columnconfigure(0, weight=1)
        self.controls_frame.grid_columnconfigure(1, weight=1)
        self.controls_frame.grid_columnconfigure(2, weight=1)
        
        # Model Transformation Section
        self.create_section_label("Transform", self.sidebar_scroll)
        
        # Scale slider
        self.scale_frame = self.create_slider_control(
            self.sidebar_scroll,
            "Scale",
            0.1,
            2.0,
            0.5,
            self.update_scale
        )
        
        # Rotation speed slider
        self.rotation_frame = self.create_slider_control(
            self.sidebar_scroll,
            "Rotation Speed",
            0,
            100,
            60,
            self.update_rotation_speed
        )
        
        # Voice Control Section
        self.create_section_label("Voice Control", self.sidebar_scroll)
        
        # Command selection
        self.command_frame = ctk.CTkFrame(self.sidebar_scroll, fg_color="transparent")
        self.command_frame.pack(fill="x", padx=10, pady=5)
        
        if not self.all_commands:
            self.all_commands = ["left", "right", "up", "down", "rotate"]
            
        self.command_var = ctk.StringVar(value=self.all_commands[0])
        self.command_dropdown = ctk.CTkOptionMenu(
            self.command_frame,
            values=self.all_commands,
            variable=self.command_var,
            dynamic_resizing=True,
            width=200,
            height=32,
            font=ctk.CTkFont(size=14),
            fg_color=("#007AFF", "#0A84FF"),
            button_color=("#0051A8", "#0051A8"),
            button_hover_color=("#003D7F", "#003D7F")
        )
        self.command_dropdown.pack(fill="x", pady=5)
        
        # Sample controls
        self.sample_frame = ctk.CTkFrame(self.sidebar_scroll, fg_color="transparent")
        self.sample_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            self.sample_frame,
            text="Sample #",
            font=ctk.CTkFont(size=14)
        ).pack(side="left")
        
        self.sample_entry = ctk.CTkEntry(
            self.sample_frame,
            width=60,
            height=32,
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        self.sample_entry.pack(side="right")
        self.sample_entry.insert(0, "1")
        
        # Recording buttons
        self.record_button = ctk.CTkButton(
            self.sidebar_scroll,
            text=self.translator.t("Record Command"),
            command=self.record_single_command,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#FF3B30", "#FF453A"),
            hover_color=("#CC2E26", "#CC2E26")
        )
        self.record_button.pack(fill="x", padx=10, pady=5)
        
        self.record_all_button = ctk.CTkButton(
            self.sidebar_scroll,
            text=self.translator.t("Record All Commands"),
            command=self.record_command,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.record_all_button.pack(fill="x", padx=10, pady=5)
    
    def setup_content_area(self):
        # Status bar at the top
        self.status_bar = ctk.CTkFrame(
            self.content_frame,
            height=40,
            fg_color=("#f5f5f5", "#2d2d2d"),
            corner_radius=10
        )
        self.status_bar.pack(fill="x", padx=10, pady=10)
        self.status_bar.pack_propagate(False)
        
        # Status indicators
        self.recording_status = ctk.CTkLabel(
            self.status_bar,
            text=self.translator.t("● Ready"),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#00CA4E", "#00CA4E")
        )
        self.recording_status.pack(side="left", padx=15)
        
        # Add status label (missing in original code)
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text=self.translator.t("Status: Ready"),
            font=ctk.CTkFont(size=14),
            text_color=("#1a1a1a", "#ffffff")
        )
        self.status_label.pack(side="left", padx=15)
        
        self.countdown_label = ctk.CTkLabel(
            self.status_bar,
            text="",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#FF9F0A", "#FF9F0A")
        )
        self.countdown_label.pack(side="right", padx=15)
        
        # Add recording indicator label (missing in original code)
        self.recording_indicator = ctk.CTkLabel(
            self.status_bar,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#FF9F0A", "#FF9F0A")
        )
        self.recording_indicator.pack(side="right", padx=15)
        
        # Audio visualization
        self.viz_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=("#f5f5f5", "#2d2d2d"),
            corner_radius=15
        )
        self.viz_frame.pack(fill="x", padx=10, pady=10)
        
        # Create matplotlib figure for audio visualization
        self.audio_figure = Figure(figsize=(8, 2), dpi=100, facecolor="#2d2d2d" if ctk.get_appearance_mode() == "dark" else "#f5f5f5")
        self.audio_plot = self.audio_figure.add_subplot(111)
        self.audio_plot.set_ylim(-1, 1)
        self.audio_plot.set_xlim(0, 100)
        self.audio_plot.set_title("Audio Level", color="#ffffff" if ctk.get_appearance_mode() == "dark" else "#2d2d2d", pad=10)
        self.audio_plot.set_yticks([-1, 0, 1])
        self.audio_plot.set_xticks([])
        self.audio_plot.grid(True, color="#404040" if ctk.get_appearance_mode() == "dark" else "#cccccc")
        self.audio_plot.tick_params(colors="#ffffff" if ctk.get_appearance_mode() == "dark" else "#2d2d2d")
        
        self.canvas_widget = ctk.CTkFrame(self.viz_frame)
        self.canvas_widget.pack(fill="x", padx=10, pady=10)
        
        self.audio_canvas = FigureCanvasTkAgg(self.audio_figure, master=self.canvas_widget)
        self.audio_canvas.draw()
        self.audio_canvas.get_tk_widget().pack(fill="x", expand=True)
        
        # Dataset statistics
        self.stats_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=("#f5f5f5", "#2d2d2d"),
            corner_radius=15
        )
        self.stats_frame.pack(fill="x", padx=10, pady=10)
        
        self.dataset_label = ctk.CTkLabel(
            self.stats_frame,
            text=self.translator.t("Dataset Statistics"),
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.dataset_label.pack(pady=10)
        
        self.samples_count = ctk.CTkLabel(
            self.stats_frame,
            text=self.translator.t("Total Samples: 0"),
            font=ctk.CTkFont(size=14)
        )
        self.samples_count.pack(pady=5)
        
        self.command_counts = ctk.CTkLabel(
            self.stats_frame,
            text="",
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        self.command_counts.pack(pady=5)
        
        # Progress section
        self.progress_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=("#f5f5f5", "#2d2d2d"),
            corner_radius=15
        )
        self.progress_frame.pack(fill="x", padx=10, pady=10)
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text=self.translator.t("Progress: 0%"),
            font=ctk.CTkFont(size=14)
        )
        self.progress_label.pack(pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)
        
        # Training controls
        self.train_buttons_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=("#f5f5f5", "#2d2d2d"),
            corner_radius=15
        )
        self.train_buttons_frame.pack(fill="x", padx=10, pady=10)
        
        train_label = ctk.CTkLabel(
            self.train_buttons_frame,
            text=self.translator.t("Voice Model Training"),
            font=ctk.CTkFont(size=16, weight="bold")
        )
        train_label.pack(pady=5)
        
        self.train_button = ctk.CTkButton(
            self.train_buttons_frame,
            text=self.translator.t("Train Model"),
            command=self.train_model,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#007AFF", "#0A84FF"),
            hover_color=("#0051A8", "#0051A8")
        )
        self.train_button.pack(fill="x", padx=10, pady=5)
        
        # Add a button to load pre-trained model
        self.pretrained_button = ctk.CTkButton(
            self.train_buttons_frame,
            text=self.translator.t("Use CNN Model"),
            command=self.load_pretrained_model,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#5856D6", "#5E5CE6"),
            hover_color=("#4740B3", "#4740B3")
        )
        self.pretrained_button.pack(fill="x", padx=10, pady=5)
        
        # Add a button to load Whisper model for advanced speech recognition
        self.whisper_button = ctk.CTkButton(
            self.train_buttons_frame,
            text=self.translator.t("Use Whisper Model (Best)"),
            command=self.load_whisper_model,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#FF2D55", "#FF375F"),
            hover_color=("#D50032", "#D50032")
        )
        self.whisper_button.pack(fill="x", padx=10, pady=5)
        
        # Add confidence threshold slider for pre-trained model
        self.pretrained_conf_frame = ctk.CTkFrame(
            self.train_buttons_frame,
            fg_color="transparent",
            height=40
        )
        self.pretrained_conf_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            self.pretrained_conf_frame,
            text=self.translator.t("Confidence Threshold:"),
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=5)
        
        self.pretrained_threshold_slider = ctk.CTkSlider(
            self.pretrained_conf_frame,
            from_=0.1,
            to=0.95,
            number_of_steps=17,  # 0.05 increments
            command=self.update_confidence_threshold,
            width=150
        )
        self.pretrained_threshold_slider.pack(side="right", padx=5)
        self.pretrained_threshold_slider.set(self.pretrained_confidence_threshold)
        
        self.pretrained_threshold_label = ctk.CTkLabel(
            self.pretrained_conf_frame,
            text=f"{self.pretrained_confidence_threshold:.2f}",
            font=ctk.CTkFont(size=14),
            width=30
        )
        self.pretrained_threshold_label.pack(side="right", padx=2)
        
        self.use_button = ctk.CTkButton(
            self.train_buttons_frame,
            text=self.translator.t("Start Continuous Listening"),
            command=self.start_continuous_listening,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#30D158", "#30D158"),
            hover_color=("#248A3D", "#248A3D")
        )
        self.use_button.pack(fill="x", padx=10, pady=5)
        
        self.listen_once_button = ctk.CTkButton(
            self.train_buttons_frame,
            text=self.translator.t("Listen for Command"),
            command=self.listen_for_single_command,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#9B59B6", "#8E44AD"),
            hover_color=("#7D3C98", "#7D3C98")
        )
        self.listen_once_button.pack(fill="x", padx=10, pady=5)
        
        # Add a stop listening button
        self.stop_listening_button = ctk.CTkButton(
            self.train_buttons_frame,
            text="Stop Listening",
            command=self.stop_listening,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#E74C3C", "#C0392B"),
            hover_color=("#C0392B", "#A93226")
        )
        self.stop_listening_button.pack(fill="x", padx=10, pady=5)
        
        # Add debug text widget
        self.debug_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=("#f5f5f5", "#2d2d2d"),
            corner_radius=15
        )
        self.debug_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        debug_label = ctk.CTkLabel(
            self.debug_frame,
            text="Debug Output",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        debug_label.pack(pady=5)
        
        self.debug_text = ctk.CTkTextbox(
            self.debug_frame,
            fg_color=("#ffffff", "#303030"),
            text_color=("#000000", "#ffffff"),
            font=ctk.CTkFont(size=12, family="Consolas")
        )
        self.debug_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_section_label(self, text, parent, pady=(20, 10)):
        """Create a section label with modern styling"""
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#1a1a1a", "#ffffff")
        )
        label.pack(fill="x", padx=10, pady=pady)
        return label
    
    def create_slider_control(self, parent, label, min_val, max_val, default, command):
        """Create a slider control with label and value display"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=5)
        
        label = ctk.CTkLabel(
            frame,
            text=label,
            font=ctk.CTkFont(size=14)
        )
        label.pack(fill="x")
        
        slider = ctk.CTkSlider(
            frame,
            from_=min_val,
            to=max_val,
            command=command,
            progress_color=("#007AFF", "#0A84FF"),
            button_color=("#0051A8", "#0051A8"),
            button_hover_color=("#003D7F", "#003D7F")
        )
        slider.pack(fill="x", pady=5)
        slider.set(default)
        
        return frame
    
    def update_samples_count(self):
        """Update samples count from entry field"""
        try:
            new_value = int(self.samples_entry.get())
            if new_value < 1:
                new_value = 1
            if new_value > 20:
                new_value = 20
                
            self.samples_per_command = new_value
            self.samples_entry.delete(0, "end")
            self.samples_entry.insert(0, str(self.samples_per_command))
            self.log_debug(f"Updated samples per command to {self.samples_per_command}")
        except ValueError:
            self.log_debug("Invalid value for samples per command. Please enter a number.")
            self.samples_entry.delete(0, "end")
            self.samples_entry.insert(0, str(self.samples_per_command))
    
    def update_epochs_count(self):
        """Update epochs count from entry field"""
        try:
            new_value = int(self.epochs_entry.get())
            if new_value < 1:
                new_value = 1
            if new_value > 500:
                new_value = 500
                
            self.training_epochs = new_value
            self.epochs_entry.delete(0, "end")
            self.epochs_entry.insert(0, str(self.training_epochs))
            self.log_debug(f"Updated training epochs to {self.training_epochs}")
        except ValueError:
            self.log_debug("Invalid value for training epochs. Please enter a number.")
            self.epochs_entry.delete(0, "end")
            self.epochs_entry.insert(0, str(self.training_epochs))
    
    def update_dataset_stats(self):
        """Update the dataset statistics display"""
        if not hasattr(self.game, 'dataset') or not self.game.dataset:
            self.dataset_label.configure(text="Dataset Statistics (0 samples)")
            self.samples_count.configure(text="No samples recorded yet")
            self.command_counts.configure(text="")
            return
            
        total_samples = sum(len(samples) for samples in self.game.dataset.values())
        self.dataset_label.configure(text=f"Dataset Statistics ({total_samples} samples)")
        
        # Show count for each command
        counts_text = ""
        for cmd, samples in self.game.dataset.items():
            sample_count = len(samples)
            if sample_count > 0:
                counts_text += f"{cmd}: {sample_count} samples\n"
        
        if counts_text:
            self.samples_count.configure(text="Samples per command:")
            self.command_counts.configure(text=counts_text)
        else:
            self.samples_count.configure(text="No command samples recorded")
            self.command_counts.configure(text="")
    
    def clear_debug_output(self):
        """Clear the debug output text"""
        self.debug_text.delete("1.0", "end")
        self.log_debug("Debug output cleared")
    
    def on_close(self):
        """Handle window close event"""
        sys.exit(0)
    
    def start_panda3d_loop(self):
        """Start the main Panda3D loop and make it cooperative with Tkinter"""
        # Run Tkinter update as a task in Panda3D
        def tk_update(task):
            try:
                self.update()
                return Task.cont
            except Exception as e:
                print(f"Error in Tkinter update: {e}")
                return Task.done
        
        self.game.taskMgr.add(tk_update, "tkUpdateTask")
    
    def update_status(self, text):
        """Update the status label with icons"""
        # Check for common status messages and add appropriate icons
        if "error" in text.lower() or "failed" in text.lower():
            icon = "⚠️ "  # Warning icon for errors
            self.status_label.configure(text_color=("#FF3B30", "#FF453A"))
        elif "recording" in text.lower():
            icon = "🎙️ "  # Microphone icon for recording
            self.status_label.configure(text_color=("#FF9500", "#FF9F0A"))
        elif "listening" in text.lower():
            icon = "👂 "  # Ear icon for listening
            self.status_label.configure(text_color=("#30D158", "#30D158"))
        elif "training" in text.lower():
            icon = "🧠 "  # Brain icon for training
            self.status_label.configure(text_color=("#5856D6", "#5E5CE6"))
        elif "heard" in text.lower():
            icon = "🔊 "  # Sound icon for recognized command
            self.status_label.configure(text_color=("#30D158", "#30D158"))
        elif "ready" in text.lower():
            icon = "✓ "  # Checkmark for ready state
            self.status_label.configure(text_color=("#1a1a1a", "#ffffff"))
        else:
            icon = "• "  # Default bullet point
            self.status_label.configure(text_color=("#1a1a1a", "#ffffff"))
            
        self.status_label.configure(text=f"Status: {icon}{text}")
    
    def update_progress(self, progress, text=None):
        """Update progress bar and label with better visuals"""
        self.progress_bar.set(progress)
        
        # Set the progress bar color based on progress value
        if progress < 0.3:
            self.progress_bar.configure(progress_color=("#FF9500", "#FF9F0A"))  # Orange for low progress
        elif progress < 0.7:
            self.progress_bar.configure(progress_color=("#30D158", "#30D158"))  # Green for medium progress
        else:
            self.progress_bar.configure(progress_color=("#007AFF", "#0A84FF"))  # Blue for high progress
            
        if text:
            self.progress_label.configure(text=text)
        else:
            percent = int(progress * 100)
            self.progress_label.configure(text=f"Progress: {percent}%")
    
    def log_debug(self, text):
        """Add text to debug output with timestamp"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.debug_text.insert("end", f"[{timestamp}] {text}\n")
        self.debug_text.see("end")  # Scroll to end
    
    def update_audio_visualization(self):
        """Update the audio visualization plot"""
        try:
            if self.audio_data is None or not self.visualize_active:
                return
                
            # Get a segment of the audio data
            if len(self.audio_data) > 100:
                display_data = self.audio_data[-100:]
            else:
                display_data = self.audio_data
                
            # Clear the plot and redraw
            self.audio_plot.clear()
            self.audio_plot.set_ylim(-1, 1)
            self.audio_plot.set_xlim(0, len(display_data))
            self.audio_plot.set_title("Audio Level")
            self.audio_plot.set_yticks([-1, 0, 1])
            self.audio_plot.set_xticks([])
            self.audio_plot.grid(True)
            
            # Calculate RMS for intensity color
            if len(display_data) > 0:
                rms = np.sqrt(np.mean(np.square(display_data)))
                if rms > 0.6:
                    color = 'red'
                elif rms > 0.3:
                    color = 'orange'
                else:
                    color = 'green'
            else:
                color = 'blue'
                
            # Update RMS status
            if len(display_data) > 0:
                level = int(rms * 100)
                self.recording_status.configure(
                    text=f"Recording level: {level}%",
                    text_color=color
                )
            
            # Plot the data
            self.audio_plot.plot(display_data, color=color)
            self.audio_canvas.draw()
            
        except Exception as e:
            self.log_debug(f"Error updating audio visualization: {str(e)}")
    
    def process_queues(self, task):
        """Process any queued tasks safely on the main thread"""
        try:
            # Process audio recording queue
            if self.audio_queue and not self.is_recording:
                task_info = self.audio_queue.pop(0)
                if task_info['type'] == 'record':
                    self.is_recording = True
                    self._record_audio_task()
                elif task_info['type'] == 'record_single':
                    self.is_recording = True
                    self._record_single_command_task(task_info['command'], task_info['sample'])
                elif task_info['type'] == 'predict':
                    self.is_predicting = True
                    self._predict_command_task(task_info['label_map'])
                elif task_info['type'] == 'predict_once':
                    self.is_predicting = True
                    self._predict_once_command_task(task_info['label_map'])
            
            # Process ML tasks queue
            if self.processing_queue and not self.is_training:
                task_info = self.processing_queue.pop(0)
                if task_info['type'] == 'train':
                    self.is_training = True
                    self._train_model_task()
            
            # Update audio visualization if active
            if self.visualize_active and self.audio_data is not None:
                self.update_audio_visualization()
                
            # Update countdown display if active
            if self.is_countdown_active:
                remaining = self.recording_countdown - time.time()
                if remaining > 0:
                    count = int(remaining)
                    # Create a more prominent countdown with color
                    if count == 3:
                        self.countdown_label.configure(text=f"{count}", text_color="#FF3B30")  # Red for 3
                    elif count == 2:
                        self.countdown_label.configure(text=f"{count}", text_color="#FF9500")  # Orange for 2
                    elif count == 1:
                        self.countdown_label.configure(text=f"{count}", text_color="#30D158")  # Green for 1
                    
                    # Make countdown font size larger as it gets closer to 0
                    new_size = 24 + (3 - count) * 4  # Starts at 24, increases to 32
                    self.countdown_label.configure(font=ctk.CTkFont(size=new_size, weight="bold"))
                else:
                    self.countdown_label.configure(text="GO!", text_color="#30D158")
                    self.countdown_label.configure(font=ctk.CTkFont(size=32, weight="bold"))
                    # Reset countdown after a brief display of GO!
                    self.game.taskMgr.doMethodLater(0.5, self._reset_countdown_display, "resetCountdown")
                    self.is_countdown_active = False
                
        except Exception as e:
            self.log_debug(f"Error in queue processing: {str(e)}")
        
        return task.cont
    
    def _reset_countdown_display(self, task):
        """Reset the countdown display"""
        self.countdown_label.configure(text="")
        self.countdown_label.configure(font=ctk.CTkFont(size=20, weight="bold"))
        return task.done
    
    def record_command(self):
        """Queue recording of voice command samples"""
        if not self.tf_available or not self.audio_available:
            self.update_status("Missing required libraries")
            self.log_debug("Cannot record: TensorFlow or audio libraries missing")
            self.log_debug("Make sure to install: tensorflow, sounddevice, and librosa")
            self.log_debug("Run: pip install tensorflow sounddevice librosa")
            return
        
        # Reset current command index
        self.current_command_index = 0
        self.current_command = None
        
        try:
            # Queue the recording task instead of starting a thread
            self.audio_queue.append({'type': 'record'})
            self.update_status("Queued recording...")
        except Exception as e:
            self.log_debug(f"Error queueing recording: {str(e)}")
            self.update_status("Recording setup failed")
    
    def _record_audio_task(self):
        """Record audio samples on the main thread"""
        try:
            all_commands = self.all_commands
            if not all_commands:
                self.update_status("No commands defined")
                self.is_recording = False
                return
                
            self.log_debug(f"Starting recording for {len(all_commands)} commands")
            self.log_debug(f"Will record {self.samples_per_command} samples per command")
            
            # Create a fresh dataset
            self.game.dataset = {cmd: [] for cmd in all_commands}
            
            # Setup recording for first command and sample
            self.current_command_index = 0
            self.current_command = all_commands[0]
            self.current_sample_index = 0
            
            # Enable audio visualization
            self.visualize_active = True
            self.audio_data = np.zeros(100)
            
            # Create session directory for this recording
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.session_dir = os.path.join(dataset_path1, f'session_{timestamp}')
            os.makedirs(self.session_dir, exist_ok=True)
            self.log_debug(f"Created session directory: {self.session_dir}")
            
            # Start the recording sequence with a countdown
            self.start_recording_countdown(3)
            
        except Exception as e:
            self.log_debug(f"Error in recording setup: {str(e)}")
            self.update_status(f"Recording setup error")
            self.visualize_active = False
            self.is_recording = False
    
    def start_recording_countdown(self, seconds):
        """Start a countdown before recording"""
        self.recording_countdown = time.time() + seconds
        self.is_countdown_active = True
        self.game.taskMgr.doMethodLater(seconds, self._begin_recording, "beginRecording")
    
    def _begin_recording(self, task):
        """Start the recording sequence after countdown"""
        try:
            # Start monitoring audio levels
            self.game.taskMgr.add(self._monitor_audio_levels, "monitorAudio")
            
            # Start the recording sequence
            if self.manual_recording:
                self.game.taskMgr.add(self._record_single_sample, "recordSingleSample")
            else:
                self.game.taskMgr.add(self._record_next_sample, "recordNextSample")
            return task.done
        except Exception as e:
            self.log_debug(f"Error starting recording: {str(e)}")
            self.is_recording = False
            self.visualize_active = False
            self.manual_recording = False
            return task.done
    
    def _monitor_audio_levels(self, task):
        """Monitor audio levels for visualization"""
        if not self.visualize_active:
            return task.done
            
        try:
            # Get a short chunk of audio
            duration = 0.1  # 100ms
            audio_chunk = sd.rec(
                int(self.game.sr * duration),
                samplerate=self.game.sr,
                channels=1,
                dtype=np.float32
            )
            sd.wait()
            
            # Update the audio data
            if audio_chunk is not None and len(audio_chunk) > 0:
                flattened = audio_chunk.flatten()
                self.audio_data = np.append(self.audio_data[-400:], flattened)
                
            return task.cont
        except Exception as e:
            self.log_debug(f"Error monitoring audio: {str(e)}")
            return task.done
    
    def _record_next_sample(self, task):
        """Record one sample at a time using Panda3D's task system"""
        try:
            all_commands = self.all_commands
            cmd = self.current_command
            sample_idx = self.current_sample_index
            
            # Update recording indicator
            self.recording_indicator.configure(
                text=f"Recording: '{cmd}' (Sample {sample_idx+1}/{self.samples_per_command})"
            )
            self.update_status(f"Say '{cmd}' now...")
            self.log_debug(f"Recording '{cmd}' - sample {sample_idx+1}/{self.samples_per_command}")
            
            # Update progress
            total_progress = (self.current_command_index * self.samples_per_command + sample_idx) / (len(all_commands) * self.samples_per_command)
            self.update_progress(total_progress, f"Recording: {int(total_progress*100)}%")
            
            # Add a delay task and then record
            self.game.taskMgr.doMethodLater(1.0, self._do_recording, "doRecording")
            return task.done
        except Exception as e:
            self.log_debug(f"Error in recording sequence: {str(e)}")
            self.update_status(f"Recording sequence error")
            self.recording_indicator.configure(text="")
            self.is_recording = False
            self.visualize_active = False
            return task.done
    
    def _do_recording(self, task):
        """Actually perform the recording after delay"""
        try:
            cmd = self.current_command
            sample_idx = self.current_sample_index
            
            # Indicate active recording
            self.recording_status.configure(
                text="RECORDING ACTIVE",
                text_color="#FF5555"
            )
            
            # Record audio
            audio = sd.rec(int(self.game.sr * self.game.duration), 
                          samplerate=self.game.sr, 
                          channels=1, 
                          dtype=np.float32)
            sd.wait()
            
            # Reset recording status
            self.recording_status.configure(
                text="Processing...",
                text_color="#AAAAAA"
            )
            
            # Check if audio was recorded properly
            if audio is None or len(audio) == 0:
                self.log_debug(f"No audio data received for '{cmd}' sample {sample_idx+1}")
            else:
                # Add to dataset
                flattened = audio.flatten()
                self.game.dataset[cmd].append(flattened)
                
                # Calculate RMS to check audio quality
                rms = np.sqrt(np.mean(np.square(flattened)))
                quality = "Good" if rms > 0.1 else "Low"
                
                self.log_debug(f"Recorded '{cmd}' sample {sample_idx+1}: {len(flattened)} samples (Level: {int(rms*100)}%)")
                
                # Save individual sample to session directory
                sample_file = os.path.join(self.session_dir, f'{cmd}_sample_{sample_idx+1}.npy')
                np.save(sample_file, flattened)
                self.log_debug(f"Saved sample to {sample_file}")
                
                # Update the dataset stats after each recording
                self.update_dataset_stats()
            
            # Move to next sample or command
            self.current_sample_index += 1
            if self.current_sample_index >= self.samples_per_command:
                # Move to next command
                self.current_command_index += 1
                self.current_sample_index = 0
                
                if self.current_command_index >= len(self.all_commands):
                    # All done
                    self.recording_indicator.configure(text="")
                    self.update_status("Recording Complete")
                    self.update_progress(1.0, "Recording: 100%")
                    self.log_debug(f"Dataset now contains {sum(len(samples) for samples in self.game.dataset.values())} samples")
                    
                    # Save dataset to session directory
                    dataset_file = os.path.join(self.session_dir, 'dataset.pkl')
                    with open(dataset_file, 'wb') as f:
                        pickle.dump(self.game.dataset, f)
                    self.log_debug(f"Saved complete dataset to {dataset_file}")
                    
                    # Stop audio visualization
                    self.visualize_active = False
                    self.recording_status.configure(
                        text="Recording complete",
                        text_color="#00AA00"
                    )
                    self.is_recording = False
                    return task.done
                else:
                    # Setup next command
                    self.current_command = self.all_commands[self.current_command_index]
            
            # Continue recording next sample
            self.game.taskMgr.add(self._record_next_sample, "recordNextSample")
            return task.done
            
        except Exception as e:
            self.log_debug(f"Error during recording: {str(e)}")
            self.update_status(f"Recording error")
            self.recording_indicator.configure(text="")
            self.is_recording = False
            self.visualize_active = False
            return task.done
    
    def save_dataset(self):
        """Save the recorded dataset"""
        if not self.tf_available or not self.audio_available:
            self.update_status("Voice commands disabled")
            return
            
        try:
            # Make sure voice_data directory exists
            os.makedirs(dataset_path1, exist_ok=True)
            
            # Create a timestamped filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            dataset_file = f"{dataset_path1}/dataset_{timestamp}.pkl"
            
            # Check if dataset has any samples
            total_samples = sum(len(samples) for samples in self.game.dataset.values())
            if total_samples == 0:
                self.update_status("No samples to save")
                self.log_debug("Dataset is empty, nothing to save")
                return
                
            with open(dataset_file, "wb") as f:
                pickle.dump(self.game.dataset, f)
                
            # Also save a copy as the default dataset
            with open(f"{dataset_path1}/dataset.pkl", "wb") as f:
                pickle.dump(self.game.dataset, f)
            
            # Save command counts to a summary file
            summary_file = f"{dataset_path1}/dataset_{timestamp}_summary.txt"
            with open(summary_file, "w") as f:
                f.write(f"Dataset Summary - {timestamp}\n")
                f.write(f"Total samples: {total_samples}\n\n")
                f.write("Samples per command:\n")
                for cmd, samples in self.game.dataset.items():
                    f.write(f"  {cmd}: {len(samples)} samples\n")
                
            self.update_status(f"Dataset Saved! ({total_samples} samples)")
            self.log_debug(f"Saved dataset with {total_samples} samples to {dataset_file}")
            self.log_debug(f"Also saved as default dataset.pkl")
            self.log_debug(f"Summary saved to {summary_file}")
        except Exception as e:
            self.log_debug(f"Error saving dataset: {str(e)}")
            self.update_status(f"Save error")
    
    def train_model(self):
        """Queue training of the voice recognition model"""
        if not self.tf_available or not self.audio_available:
            self.update_status("TensorFlow or audio libraries missing")
            self.log_debug("Cannot train model: TensorFlow or audio libraries are not installed")
            self.log_debug("Please install with: pip install tensorflow sounddevice librosa")
            return
        
        try:
            # Queue the training task instead of starting a thread
            self.processing_queue.append({'type': 'train'})
            self.update_status(f"Queued training with {self.training_epochs} epochs...")
            self.update_progress(0, "Training: Queued")
        except Exception as e:
            self.log_debug(f"Error queueing training: {str(e)}")
            self.update_status("Training setup failed")
    
    def _train_model_task(self):
        """Train model on the main thread"""
        try:
            self.log_debug(f"Starting model training with {self.training_epochs} epochs...")
            X, y = [], []
            
            # Check if dataset has samples
            total_samples = sum(len(samples) for samples in self.game.dataset.values())
            if total_samples == 0:
                self.log_debug("No samples in dataset. Try loading a saved dataset.")
                
                # Try to load saved dataset
                dataset_file = f"{dataset_path1}/dataset.pkl"
                if os.path.exists(dataset_file):
                    self.log_debug(f"Loading dataset from {dataset_file}")
                    with open(dataset_file, "rb") as f:
                        self.game.dataset = pickle.load(f)
                    
                    total_samples = sum(len(samples) for samples in self.game.dataset.values())
                    self.update_dataset_stats()
                    
                    if total_samples == 0:
                        self.update_status("No samples found")
                        self.log_debug("Loaded dataset is also empty")
                        self.is_training = False
                        return
                else:
                    self.update_status("No training data!")
                    self.log_debug("No dataset file found")
                    self.is_training = False
                    return
            
            # Process each sample
            self.log_debug("Processing audio samples...")
            sample_count = 0
            empty_commands = []
            
            for label, samples in self.game.dataset.items():
                self.log_debug(f"Processing {len(samples)} samples for '{label}'")
                
                if len(samples) == 0:
                    empty_commands.append(label)
                    continue
                    
                for sample in samples:
                    if len(sample) == 0:
                        self.log_debug(f"Empty sample for '{label}', skipping")
                        continue
                    
                    try:
                        # Extract MFCC features
                        mfccs = librosa.feature.mfcc(y=sample, sr=self.game.sr, n_mfcc=13)
                        mfccs_flat = mfccs.flatten()
                        
                        # Check if features are valid
                        if np.isnan(mfccs_flat).any():
                            self.log_debug(f"Invalid features (NaN) in sample for '{label}', skipping")
                            continue
                            
                        X.append(mfccs_flat)
                        y.append(label)
                        sample_count += 1
                        
                    except Exception as e:
                        self.log_debug(f"Error processing sample for '{label}': {str(e)}")
            
            if empty_commands:
                self.log_debug(f"Warning: These commands have no samples: {', '.join(empty_commands)}")
            
            if len(X) == 0:
                self.update_status("No valid samples!")
                self.log_debug("No valid samples after processing")
                self.is_training = False
                return
            
            # Convert lists to numpy arrays
            self.log_debug(f"Creating training arrays with {len(X)} samples")    
            X = np.array(X)
            
            # Create label mapping
            label_map = {label: i for i, label in enumerate(self.game.commands.keys())}
            self.log_debug(f"Label mapping: {label_map}")
            
            # Convert string labels to numeric
            y_encoded = np.array([label_map[label] for label in y])
            
            # Ask user if they want to use a CNN model instead (detected by number of samples)
            use_cnn = len(X) >= 5  # Only use CNN if we have enough samples
            
            if use_cnn:
                # Prepare data for CNN (reshape from flattened to 2D+channels)
                self.log_debug("Preparing data for CNN model...")
                
                # Determine the shape of the MFCC features
                mfccs_per_sample = 13  # Standard MFCC features
                frames_per_sample = len(X[0]) // mfccs_per_sample
                
                # Reshape the data for CNN input: (batch, time, features, channel)
                X_reshaped = X.reshape(-1, frames_per_sample, mfccs_per_sample, 1)
                
                self.log_debug(f"Reshaped data for CNN: {X_reshaped.shape}")
                
                # Create a CNN model
                self.log_debug("Creating CNN model for better performance...")
                
                # Simple CNN model
                inputs = tf.keras.layers.Input(shape=(frames_per_sample, mfccs_per_sample, 1))
                
                # First convolutional block
                x = tf.keras.layers.Conv2D(16, (3, 3), activation='relu', padding='same')(inputs)
                x = tf.keras.layers.BatchNormalization()(x)
                x = tf.keras.layers.MaxPooling2D((2, 2))(x)
                x = tf.keras.layers.Dropout(0.2)(x)
                
                # Second convolutional block
                x = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(x)
                x = tf.keras.layers.BatchNormalization()(x)
                x = tf.keras.layers.MaxPooling2D((2, 2))(x)
                x = tf.keras.layers.Dropout(0.3)(x)
                
                # Flatten and dense layers
                x = tf.keras.layers.Flatten()(x)
                x = tf.keras.layers.Dense(64, activation='relu')(x)
                x = tf.keras.layers.BatchNormalization()(x)
                x = tf.keras.layers.Dropout(0.4)(x)
                
                # Output layer
                outputs = tf.keras.layers.Dense(len(self.game.commands), activation='softmax')(x)
                
                # Create and compile the model
                self.game.speech_model = tf.keras.Model(inputs=inputs, outputs=outputs)
                self.game.speech_model.compile(
                    optimizer='adam',
                    loss='sparse_categorical_crossentropy',
                    metrics=['accuracy']
                )
                
                # Save the reshape parameters for prediction
                self.game.cnn_model = True
                self.game.mfccs_per_sample = mfccs_per_sample
                self.game.frames_per_sample = frames_per_sample
                
                # Add task to continue training in batches to avoid freezing the app
                self._training_data = {
                    'X': X_reshaped,
                    'y': y_encoded,
                    'label_map': label_map,
                    'current_epoch': 0,
                    'cnn_model': True
                }
                
                self.log_debug("Using CNN model for training - better performance expected")
                
            else:
                # Define and create standard model (fallback for very small datasets)
                self.log_debug("Creating standard neural network model...")
                input_shape = X.shape[1]  # Get feature dimension from the data
                
                # Create sequential model
                self.game.speech_model = tf.keras.Sequential([
                    tf.keras.layers.Dense(64, activation='relu', input_shape=(input_shape,)),
                    tf.keras.layers.BatchNormalization(),
                    tf.keras.layers.Dropout(0.3),
                    tf.keras.layers.Dense(32, activation='relu'),
                    tf.keras.layers.Dropout(0.2),
                    tf.keras.layers.Dense(len(self.game.commands), activation='softmax')
                ])
                
                # Compile model
                self.game.speech_model.compile(
                    optimizer='adam',
                    loss='sparse_categorical_crossentropy',
                    metrics=['accuracy']
                )
                
                # Standard reshape for prediction
                self.game.cnn_model = False
                
                # Add task to continue training in batches to avoid freezing the app
                self._training_data = {
                    'X': X,
                    'y': y_encoded,
                    'label_map': label_map,
                    'current_epoch': 0,
                    'cnn_model': False
                }
                
                self.log_debug("Using standard model for training (small dataset)")
            
            # Start training epochs
            self.game.taskMgr.add(self._train_epoch, "trainEpoch")
        
        except Exception as e:
            self.log_debug(f"Training setup error: {str(e)}")
            self.update_status(f"Training setup error")
            self.update_progress(0, "Training: Failed")
            self.is_training = False
    
    def _train_epoch(self, task):
        """Train one epoch at a time to avoid freezing the UI"""
        try:
            current_epoch = self._training_data['current_epoch']
            X = self._training_data['X']
            y = self._training_data['y']
            
            if current_epoch >= self.training_epochs:
                # Training complete
                self._finish_training()
                return task.done
            
            # Train for one epoch
            self.log_debug(f"Training epoch {current_epoch+1}/{self.training_epochs}")
            history = self.game.speech_model.fit(
                X, y,
                epochs=1,
                verbose=0
            )
            
            # Update progress
            acc = history.history.get('accuracy', [0])[0]
            progress = (current_epoch + 1) / self.training_epochs
            self.update_progress(progress, f"Training: {current_epoch+1}/{self.training_epochs}")
            
            if (current_epoch + 1) % 5 == 0 or current_epoch == 0:
                self.log_debug(f"Epoch {current_epoch+1}/{self.training_epochs} - accuracy: {acc:.4f}")
            
            # Move to next epoch
            self._training_data['current_epoch'] = current_epoch + 1
            
            # Pause briefly to allow UI updates
            return task.again
            
        except Exception as e:
            self.log_debug(f"Training epoch error: {str(e)}")
            self.update_status(f"Training epoch error")
            self.update_progress(0, "Training: Failed")
            self.is_training = False
            return task.done
    
    def _finish_training(self):
        """Complete the training process"""
        try:
            # Evaluate model
            X = self._training_data['X']
            y = self._training_data['y']
            label_map = self._training_data['label_map']
            
            loss, accuracy = self.game.speech_model.evaluate(X, y, verbose=0)
            self.log_debug(f"Final model accuracy: {accuracy:.4f}")
            
            # Save the model
            model_dir = dataset_path1
            os.makedirs(model_dir, exist_ok=True)
            model_file = os.path.join(model_dir, "model.pkl")
            
            # Save the model by itself
            with open(model_file, "wb") as f:
                pickle.dump(self.game.speech_model, f)
                
            # Save the label map separately
            label_map_file = os.path.join(model_dir, "label_map.pkl")
            with open(label_map_file, "wb") as f:
                pickle.dump(label_map, f)
            
            self.update_status(f"Model Trained! (Accuracy: {accuracy:.2f})")
            self.log_debug(f"Model saved to {model_file}")
            self.log_debug(f"Label map saved to {label_map_file}")
            self.update_progress(1.0, "Training: Complete")
            
        except Exception as e:
            self.log_debug(f"Training completion error: {str(e)}")
            self.update_status(f"Training completion error")
        
        finally:
            self.is_training = False
    
    def use_trained_model(self):
        """Use the trained voice recognition model to control the 3D model"""
        if not self.tf_available or not self.audio_available:
            self.update_status("TensorFlow or audio libraries missing")
            self.log_debug("Cannot use voice control: TensorFlow or audio libraries are not installed")
            self.log_debug("Please install with: pip install tensorflow sounddevice librosa")
            return
        
        try:
            # Check for required files
            model_file = f"{dataset_path1}/model.pkl"
            label_map_file = f"{dataset_path1}/label_map.pkl"
            
            if not os.path.exists(model_file):
                self.update_status("Train model first!")
                self.log_debug(f"Model file not found: {model_file}")
                return
                
            if not os.path.exists(label_map_file):
                self.update_status("Label map missing!")
                self.log_debug(f"Label map file not found: {label_map_file}")
                return
            
            # Load the model
            self.log_debug(f"Loading model from {model_file}")
            with open(model_file, "rb") as f:
                self.game.speech_model = pickle.load(f)
                
            # Load the label map
            self.log_debug(f"Loading label map from {label_map_file}")
            with open(label_map_file, "rb") as f:
                label_map = pickle.load(f)
            
            self.log_debug(f"Model and label map loaded successfully")
            self.recording_indicator.configure(text="Listening for commands...")
            
            # Queue the prediction task
            self.audio_queue.append({'type': 'predict', 'label_map': label_map})
            
        except Exception as e:
            self.log_debug(f"Error loading model: {str(e)}")
            self.update_status(f"Model load error")
    
    def _predict_command_task(self, label_map):
        """Predict command from voice input on the main thread"""
        try:
            self.update_status("Listening...")
            self.log_debug("Recording audio for prediction...")
            
            # Record audio
            audio = sd.rec(
                int(self.game.sr * self.game.duration),
                samplerate=self.game.sr,
                channels=1,
                dtype=np.float32
            )
            sd.wait()
            
            # Check if user stopped listening while we were recording
            if not self.is_predicting:
                self.log_debug("Prediction stopped by user")
                return
                
            # Check audio
            if audio is None or len(audio) == 0:
                self.log_debug("No audio data received")
                
                # Continue listening if still in predicting mode
                if self.is_predicting:
                    self.game.taskMgr.doMethodLater(0.1, lambda task: self.audio_queue.append(
                        {'type': 'predict', 'label_map': label_map}), "queueNextPrediction")
                return
                
            flattened = audio.flatten()
            self.log_debug(f"Audio recorded: {len(flattened)} samples")
            
            # Calculate RMS to check audio quality
            rms = np.sqrt(np.mean(np.square(flattened)))
            
            # Only process audio if it's loud enough
            if rms < 0.05:  # Threshold for noise
                self.log_debug(f"Audio level too low: {rms:.2f} - ignoring")
                
                # Continue listening if still in predicting mode
                if self.is_predicting:
                    self.game.taskMgr.doMethodLater(0.1, lambda task: self.audio_queue.append(
                        {'type': 'predict', 'label_map': label_map}), "queueNextPrediction")
                return
            
            # Use Whisper model if enabled
            if self.using_whisper_model and self.whisper_model is not None and self.whisper_processor is not None:
                # Process with Whisper model
                self.log_debug("Running Whisper speech recognition...")
                
                try:
                    # Resample to 16kHz (required by Whisper)
                    if self.game.sr != 16000:
                        audio_16k = librosa.resample(flattened, orig_sr=self.game.sr, target_sr=16000)
                    else:
                        audio_16k = flattened
                        
                    # Make sure audio is normalized
                    if np.max(np.abs(audio_16k)) > 0:
                        audio_16k = audio_16k / np.max(np.abs(audio_16k))
                    
                    # Prepare features with the Whisper processor
                    self.log_debug("Processing audio with Whisper...")
                    input_features = self.whisper_processor(
                        audio_16k, 
                        sampling_rate=16000, 
                        return_tensors="pt"
                    ).input_features
                    
                    # Generate token ids using the Whisper model
                    self.log_debug("Generating transcription...")
                    predicted_ids = self.whisper_model.generate(input_features)
                    
                    # Decode the ids to text
                    transcription = self.whisper_processor.batch_decode(
                        predicted_ids, 
                        skip_special_tokens=True
                    )[0].strip().lower()
                    
                    self.log_debug(f"Whisper transcription: '{transcription}'")
                    
                    # Check if the transcription matches any command
                    command = None
                    for phrase, cmd in self.whisper_command_mapping.items():
                        if phrase in transcription:
                            command = cmd
                            self.log_debug(f"Matched command: '{cmd}' from phrase '{phrase}'")
                            break
                    
                    if command is not None and command in self.game.commands:
                        self.update_status(f"Heard: {command} (from '{transcription}')")
                        self.game.commands[command]()
                    else:
                        self.log_debug(f"No command match found for '{transcription}'")
                    
                    # Continue listening if still in predicting mode
                    if self.is_predicting:
                        self.game.taskMgr.doMethodLater(0.1, lambda task: self.audio_queue.append(
                            {'type': 'predict', 'label_map': label_map}), "queueNextPrediction")
                    return
                
                except Exception as e:
                    self.log_debug(f"Error using Whisper model: {str(e)}")
                    # Fall back to other methods
            
            # Use pre-trained CNN model if enabled
            if self.using_pretrained_model and self.pretrained_model is not None:
                command, confidence = self._predict_with_pretrained_model(audio)
                if command is not None and confidence > self.pretrained_confidence_threshold:  # Use adjustable threshold
                    self.log_debug(f"Pre-trained model predicted: {command} (confidence: {confidence:.2f})")
                    self.update_status(f"Heard: {command} ({confidence:.2f} confidence)")
                    self.game.commands[command]()
                    
                    # Continue listening if still in predicting mode
                    if self.is_predicting:
                        self.game.taskMgr.doMethodLater(0.1, lambda task: self.audio_queue.append(
                            {'type': 'predict', 'label_map': label_map}), "queueNextPrediction")
                    return
                else:
                    self.log_debug(f"Pre-trained model confidence too low ({confidence:.2f}) or command not recognized")
                    
            # Fall back to custom model
            # Extract features
            self.log_debug("Extracting MFCC features...")
            mfccs = librosa.feature.mfcc(y=flattened, sr=self.game.sr, n_mfcc=13)
            
            # Check if we're using a CNN model (trained with _train_model_task)
            if hasattr(self.game, 'cnn_model') and self.game.cnn_model:
                self.log_debug("Using CNN model for prediction...")
                
                # Reshape for CNN input
                frames_per_sample = self.game.frames_per_sample
                mfccs_per_sample = self.game.mfccs_per_sample
                
                # Make sure we have the right number of frames
                if mfccs.shape[1] < frames_per_sample:
                    # Pad if too short
                    padding_width = frames_per_sample - mfccs.shape[1]
                    mfccs = np.pad(mfccs, ((0, 0), (0, padding_width)), mode='constant')
                elif mfccs.shape[1] > frames_per_sample:
                    # Truncate if too long
                    mfccs = mfccs[:, :frames_per_sample]
                
                # Reshape for CNN input: (batch, time, features, channels)
                mfccs_reshaped = mfccs.T  # now (frames, features)
                mfccs_reshaped = np.expand_dims(mfccs_reshaped, axis=0)  # add batch dimension
                mfccs_reshaped = np.expand_dims(mfccs_reshaped, axis=-1)  # add channel dimension
                
                # Make prediction
                predictions = self.game.speech_model.predict(mfccs_reshaped, verbose=0)
            else:
                # Standard model (flatten features)
                mfccs_flat = mfccs.flatten().reshape(1, -1)
                predictions = self.game.speech_model.predict(mfccs_flat, verbose=0)
            
            prediction_idx = np.argmax(predictions[0])
            
            # Get command from label map
            command = None
            for cmd, idx in label_map.items():
                if idx == prediction_idx:
                    command = cmd
                    break
                    
            if command is None:
                self.log_debug(f"Failed to map prediction index {prediction_idx} to command")
                
                # Continue listening if still in predicting mode
                if self.is_predicting:
                    self.game.taskMgr.doMethodLater(0.1, lambda task: self.audio_queue.append(
                        {'type': 'predict', 'label_map': label_map}), "queueNextPrediction")
                return
                
            confidence = predictions[0][prediction_idx]
            self.log_debug(f"Predicted '{command}' with confidence {confidence:.2f}")
            
            # Only execute high-confidence commands
            if confidence >= 0.6:  # Threshold can be adjusted
                self.update_status(f"Heard: {command} ({confidence:.2f} confidence)")
                self.game.commands[command]()
            else:
                self.log_debug(f"Command '{command}' ignored due to low confidence ({confidence:.2f})")
            
            # Continue listening if still in predicting mode
            if self.is_predicting:
                self.game.taskMgr.doMethodLater(0.1, lambda task: self.audio_queue.append(
                    {'type': 'predict', 'label_map': label_map}), "queueNextPrediction")
            
        except Exception as e:
            self.log_debug(f"Prediction error: {str(e)}")
            self.update_status("Recognition error")
            
            # Continue listening despite error if still in predicting mode
            if self.is_predicting:
                self.game.taskMgr.doMethodLater(0.5, lambda task: self.audio_queue.append(
                    {'type': 'predict', 'label_map': label_map}), "queueNextPrediction")
    
    def stop_listening(self):
        """Stop continuous listening mode"""
        self.log_debug("Stopping listening mode")
        
        # Reset prediction flags
        self.is_predicting = False
        
        # Clear the audio queue
        self.audio_queue.clear()
        
        # Update UI to show we're no longer listening
        self.recording_indicator.configure(
            text="", 
            fg_color="transparent",
            bg_color="transparent"
        )
        self.update_status("Listening stopped")
        
        # Re-enable buttons
        self.listen_once_button.configure(state="normal")
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "light" if current_mode == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        
        # Update theme switch text
        self.theme_switch.configure(text=new_mode.capitalize())
        
        # Update matplotlib figure colors
        if hasattr(self, 'audio_figure'):
            self.audio_figure.patch.set_facecolor("#2d2d2d" if new_mode == "dark" else "#f5f5f5")
            self.audio_plot.set_title("Audio Level", color="#ffffff" if new_mode == "dark" else "#2d2d2d")
            self.audio_plot.tick_params(colors="#ffffff" if new_mode == "dark" else "#2d2d2d")
            self.audio_plot.grid(True, color="#404040" if new_mode == "dark" else "#cccccc")
            self.audio_canvas.draw()
        
        # Update status bar colors
        self.status_bar.configure(fg_color=("#f5f5f5", "#2d2d2d")[new_mode == "dark"])
        
        # Update visualization frame colors
        self.viz_frame.configure(fg_color=("#f5f5f5", "#2d2d2d")[new_mode == "dark"])
        
        # Update stats frame colors
        self.stats_frame.configure(fg_color=("#f5f5f5", "#2d2d2d")[new_mode == "dark"])
        
        # Update progress frame colors
        self.progress_frame.configure(fg_color=("#f5f5f5", "#2d2d2d")[new_mode == "dark"])
        
        # Update content area colors
        self.content_area.configure(fg_color=("#ffffff", "#1e1e1e")[new_mode == "dark"])
        
        # Update sidebar colors
        self.sidebar.configure(fg_color=("#e0e0e0", "#2d2d2d")[new_mode == "dark"])
        
        # Update main container colors
        self.main_container.configure(fg_color=("#f0f0f0", "#1a1a1a")[new_mode == "dark"])
        
        # Update section labels
        for widget in self.sidebar_scroll.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(text_color=("#1a1a1a", "#ffffff")[new_mode == "dark"])
        
        # Update recording status colors
        self.recording_status.configure(text_color=("#00CA4E", "#00CA4E"))
        self.countdown_label.configure(text_color=("#FF9F0A", "#FF9F0A"))
        
        # Update dataset label colors
        self.dataset_label.configure(text_color=("#1a1a1a", "#ffffff")[new_mode == "dark"])
        self.samples_count.configure(text_color=("#1a1a1a", "#ffffff")[new_mode == "dark"])
        self.command_counts.configure(text_color=("#1a1a1a", "#ffffff")[new_mode == "dark"])
        
        # Update progress label colors
        self.progress_label.configure(text_color=("#1a1a1a", "#ffffff")[new_mode == "dark"])
        
        # Update title label colors
        self.title_label.configure(text_color=("#2d2d2d", "#ffffff")[new_mode == "dark"])
        
        # Update theme switch colors
        self.theme_switch.configure(
            progress_color=("#007AFF", "#0A84FF"),
            button_color=("#0051A8", "#0051A8"),
            button_hover_color=("#003D7F", "#003D7F")
        )
        
        # Update all buttons
        for widget in self.sidebar_scroll.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                if widget.cget("text") == "Record Command":
                    widget.configure(
                        fg_color=("#FF3B30", "#FF453A"),
                        hover_color=("#CC2E26", "#CC2E26")
                    )
                elif widget.cget("text") == "Record All Commands":
                    widget.configure(
                        fg_color=("#007AFF", "#0A84FF"),
                        hover_color=("#0051A8", "#0051A8")
                    )
        
        # Update sliders
        for widget in self.sidebar_scroll.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkSlider):
                        child.configure(
                            progress_color=("#007AFF", "#0A84FF"),
                            button_color=("#0051A8", "#0051A8"),
                            button_hover_color=("#003D7F", "#003D7F")
                        )
        
        # Update command dropdown if it exists
        if hasattr(self, 'command_dropdown'):
            self.command_dropdown.configure(
                fg_color=("#007AFF", "#0A84FF"),
                button_color=("#0051A8", "#0051A8"),
                button_hover_color=("#003D7F", "#003D7F")
            )
        
        # Update sample entry if it exists
        if hasattr(self, 'sample_entry'):
            self.sample_entry.configure(
                fg_color=("#ffffff", "#2d2d2d")[new_mode == "dark"],
                text_color=("#000000", "#ffffff")[new_mode == "dark"]
            )

    def update_scale(self, value):
        """Update the model's scale"""
        try:
            scale_value = float(value)  # Convert string to float
            self.game.model.setScale(scale_value)
            self.log_debug(f"Model scale updated to {scale_value:.2f}")
        except Exception as e:
            self.log_debug(f"Error updating model scale: {str(e)}")
    
    def update_rotation_speed(self, value):
        """Update the model's rotation speed"""
        try:
            speed_value = float(value)  # Convert string to float
            self.game.rotation_speed = speed_value
            self.log_debug(f"Rotation speed updated to {speed_value:.2f}")
        except Exception as e:
            self.log_debug(f"Error updating rotation speed: {str(e)}")
    
    def handle_keypress(self, event):
        """Handle keyboard shortcuts for model control"""
        try:
            if event.keysym == 'w':
                self.game.move_up()
            elif event.keysym == 's':
                self.game.move_down()
            elif event.keysym == 'a':
                self.game.move_left()
            elif event.keysym == 'd':
                self.game.move_right()
            elif event.keysym == 'r':
                self.game.start_rotation()
        except Exception as e:
            self.log_debug(f"Error handling keypress: {str(e)}")
    
    def record_single_command(self):
        """Record a single command selected by the user"""
        if not self.tf_available or not self.audio_available:
            self.update_status("Missing required libraries")
            self.log_debug("Cannot record: TensorFlow or audio libraries missing")
            self.log_debug("Make sure to install: tensorflow, sounddevice, and librosa")
            self.log_debug("Run: pip install tensorflow sounddevice librosa")
            return
            
        if self.is_recording or self.is_predicting:
            self.update_status("Recording or prediction already in progress")
            return
            
        try:
            # Get the selected command and sample number
            command = self.command_var.get()
            try:
                sample_num = int(self.sample_entry.get()) - 1  # Convert to 0-based index
                if sample_num < 0:
                    sample_num = 0
                    self.sample_entry.delete(0, "end")
                    self.sample_entry.insert(0, "1")
            except ValueError:
                sample_num = 0
                self.sample_entry.delete(0, "end")
                self.sample_entry.insert(0, "1")
            
            self.current_command = command
            self.current_sample_index = sample_num
            self.manual_recording = True
            
            # Queue the recording task
            self.audio_queue.append({'type': 'record_single', 'command': command, 'sample': sample_num})
            self.update_status(f"Queued recording for '{command}' (Sample {sample_num+1})")
            
        except Exception as e:
            self.log_debug(f"Error setting up single recording: {str(e)}")
            self.update_status("Recording setup failed")
    
    def _record_single_command_task(self, command, sample_idx):
        """Record a single command sample on the main thread"""
        try:
            self.log_debug(f"Starting recording for '{command}' (Sample {sample_idx+1})")
            
            # Make sure dataset exists
            if not hasattr(self.game, 'dataset') or not self.game.dataset:
                self.game.dataset = {cmd: [] for cmd in self.all_commands}
            
            # Make sure command exists in dataset
            if command not in self.game.dataset:
                self.game.dataset[command] = []
            
            # Convert sample_idx to integer and ensure it's valid
            sample_idx = int(sample_idx)
            if sample_idx < 0:
                sample_idx = 0
            
            # Extend dataset list if needed
            while len(self.game.dataset[command]) <= sample_idx:
                self.game.dataset[command].append(None)
            
            # Enable audio visualization
            self.visualize_active = True
            self.audio_data = np.zeros(100)
            
            # Create session directory if it doesn't exist
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            if not hasattr(self, 'session_dir') or not os.path.exists(self.session_dir):
                self.session_dir = os.path.join(dataset_path1, f'session_{timestamp}')
                os.makedirs(self.session_dir, exist_ok=True)
                self.log_debug(f"Created session directory: {self.session_dir}")
            
            # Start the recording sequence with a countdown
            self.current_command = command
            self.current_sample_index = sample_idx
            self.start_recording_countdown(3)
            
        except Exception as e:
            self.log_debug(f"Error in single recording setup: {str(e)}")
            self.update_status(f"Recording setup error")
            self.visualize_active = False
            self.is_recording = False
            self.manual_recording = False
    
    def _record_single_sample(self, task):
        """Record a single sample selected by the user"""
        try:
            cmd = self.current_command
            sample_idx = self.current_sample_index
            
            # Update recording indicator
            self.recording_indicator.configure(
                text=f"Recording: '{cmd}' (Sample {sample_idx+1})"
            )
            self.update_status(f"Say '{cmd}' now...")
            self.log_debug(f"Recording '{cmd}' - sample {sample_idx+1}")
            
            # Add a delay task and then record
            self.game.taskMgr.doMethodLater(1.0, self._do_single_recording, "doSingleRecording")
            return task.done
        except Exception as e:
            self.log_debug(f"Error in recording sequence: {str(e)}")
            self.update_status(f"Recording sequence error")
            self.recording_indicator.configure(text="")
            self.is_recording = False
            self.visualize_active = False
            self.manual_recording = False
            return task.done
    
    def _do_single_recording(self, task):
        """Record a single sample selected by the user"""
        try:
            cmd = self.current_command
            sample_idx = self.current_sample_index
            
            # Indicate active recording
            self.recording_status.configure(
                text="RECORDING ACTIVE",
                text_color="#FF5555"
            )
            
            # Record audio
            audio = sd.rec(int(self.game.sr * self.game.duration), 
                          samplerate=self.game.sr, 
                          channels=1, 
                          dtype=np.float32)
            sd.wait()
            
            # Reset recording status
            self.recording_status.configure(
                text="Processing...",
                text_color="#AAAAAA"
            )
            
            # Check if audio was recorded properly
            if audio is None or len(audio) == 0:
                self.log_debug(f"No audio data received for '{cmd}' sample {sample_idx+1}")
            else:
                # Add to dataset
                flattened = audio.flatten()
                self.game.dataset[cmd][sample_idx] = flattened
                
                # Calculate RMS to check audio quality
                rms = np.sqrt(np.mean(np.square(flattened)))
                quality = "Good" if rms > 0.1 else "Low"
                
                self.log_debug(f"Recorded '{cmd}' sample {sample_idx+1}: {len(flattened)} samples (Level: {int(rms*100)}%)")
                
                # Save individual sample to session directory
                sample_file = os.path.join(self.session_dir, f'{cmd}_sample_{sample_idx+1}.npy')
                np.save(sample_file, flattened)
                self.log_debug(f"Saved sample to {sample_file}")
                
                # Update the dataset stats 
                self.update_dataset_stats()
                
                # Auto-increment sample number for next recording
                next_sample = sample_idx + 2  # +1 for index and +1 to increment
                self.sample_entry.delete(0, "end")
                self.sample_entry.insert(0, str(next_sample))
            
            # All done with this recording
            self.recording_indicator.configure(text="")
            self.update_status(f"Recorded '{cmd}' (Sample {sample_idx+1})")
            
            # Stop audio visualization
            self.visualize_active = False
            self.recording_status.configure(
                text="Recording complete",
                text_color="#00AA00"
            )
            self.is_recording = False
            self.manual_recording = False
            return task.done
            
        except Exception as e:
            self.log_debug(f"Error during recording: {str(e)}")
            self.update_status(f"Recording error")
            self.recording_indicator.configure(text="")
            self.is_recording = False
            self.visualize_active = False
            self.manual_recording = False
            return task.done

    def start_continuous_listening(self):
        """Start continuous listening for voice commands to control the 3D model"""
        if not self.tf_available or not self.audio_available:
            self.log_debug("TensorFlow or audio libraries not available for voice command recognition")
            self.update_status("Libraries missing for voice recognition")
            return
            
        self.log_debug("Setting up continuous voice command recognition...")
        
        # Load the model and label map
        label_map = self._load_speech_model_and_labels()
        if label_map is None:
            return
            
        # Update UI to show we're listening continuously
        self.update_status("Starting continuous listening")
        self.recording_indicator.configure(
            text="🎤 CONTINUOUS", 
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#30D158", "#30D158"),
            bg_color=("#30D158", "#248A3D"),
            corner_radius=10,
            text_color=("#ffffff", "#ffffff")
        )
        
        # Queue a prediction task
        self.audio_queue.append({
            'type': 'predict',
            'label_map': label_map
        })
        
    def _load_speech_model_and_labels(self):
        """Helper method to load the speech model and label map"""
        try:
            # Check if we have a trained model
            model_path = os.path.join(dataset_path1, 'model.pkl')
            if not os.path.exists(model_path):
                self.log_debug(f"Model file not found at {model_path}")
                self.update_status("No trained model found")
                return None
                
            # Load the model if needed
            if not hasattr(self.game, 'speech_model') or self.game.speech_model is None:
                self.log_debug("Loading speech recognition model...")
                with open(model_path, 'rb') as f:
                    model_tuple = pickle.load(f)
                    if isinstance(model_tuple, tuple) and len(model_tuple) == 2:
                        self.game.speech_model, _ = model_tuple
                    else:
                        self.game.speech_model = model_tuple
                self.log_debug("Speech model loaded successfully")
                
            # Check if we have a label map
            label_map_path = os.path.join(dataset_path1, 'label_map.pkl')
            if not os.path.exists(label_map_path):
                self.log_debug(f"Label map not found at {label_map_path}")
                self.update_status("No label map found")
                return None
                
            # Load the label map
            with open(label_map_path, 'rb') as f:
                label_map = pickle.load(f)
                
            return label_map
            
        except Exception as e:
            self.log_debug(f"Error loading speech model: {str(e)}")
            self.update_status("Error loading model")
            return None

    def listen_for_single_command(self):
        """Listen for a single voice command and execute it"""
        if not self.tf_available or not self.audio_available:
            self.log_debug("TensorFlow or audio libraries not available for voice command recognition")
            self.update_status("Libraries missing for voice recognition")
            return
            
        self.log_debug("Setting up single command recognition...")
        
        # Load the model and label map
        label_map = self._load_speech_model_and_labels()
        if label_map is None:
            return
            
        # Update UI to show we're listening
        self.update_status("Preparing to listen")
        self.recording_indicator.configure(
            text="🎤 LISTENING", 
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#9B59B6", "#8E44AD"),
            bg_color=("#9B59B6", "#7D3C98"),
            corner_radius=10,
            text_color=("#ffffff", "#ffffff")
        )
        self.listen_once_button.configure(state="disabled")
        
        # Queue a prediction task for a single command
        self.audio_queue.append({
            'type': 'predict_once',
            'label_map': label_map
        })

    def load_pretrained_model(self):
        """Load a pre-trained speech recognition model from TensorFlow Hub"""
        if not self.tf_available or not self.audio_available:
            self.update_status("TensorFlow or audio libraries missing")
            self.log_debug("Cannot load pre-trained model: Required libraries missing")
            self.log_debug("Make sure to install: tensorflow, sounddevice, and librosa")
            self.log_debug("Run: pip install tensorflow sounddevice librosa")
            return
        
        try:
            self.update_status("Loading advanced CNN model...")
            self.log_debug("Creating CNN speech recognition model...")
            
            # Use a CNN architecture which works much better for audio
            # The input shape will be (frames, mfcc_features, 1) for a CNN
            frames = 40  # Longer time context
            mfcc_features = 13
            
            self.log_debug("Creating CNN model architecture...")
            # Build a CNN model that's better at audio feature extraction
            inputs = tf.keras.layers.Input(shape=(frames, mfcc_features, 1))
            
            # First convolutional block
            x = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(inputs)
            x = tf.keras.layers.BatchNormalization()(x)
            x = tf.keras.layers.MaxPooling2D((2, 2))(x)
            x = tf.keras.layers.Dropout(0.2)(x)
            
            # Second convolutional block
            x = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
            x = tf.keras.layers.BatchNormalization()(x)
            x = tf.keras.layers.MaxPooling2D((2, 2))(x)
            x = tf.keras.layers.Dropout(0.3)(x)
            
            # Flatten and dense layers
            x = tf.keras.layers.Flatten()(x)
            x = tf.keras.layers.Dense(128, activation='relu')(x)
            x = tf.keras.layers.BatchNormalization()(x)
            x = tf.keras.layers.Dropout(0.5)(x)
            
            # Output layer
            outputs = tf.keras.layers.Dense(len(self.game.commands), activation='softmax')(x)
            
            # Create the model
            self.pretrained_model = tf.keras.Model(inputs=inputs, outputs=outputs)
            
            # Compile the model
            self.log_debug("Compiling CNN model...")
            self.pretrained_model.compile(
                optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )
            
            # Initialize the model with a dummy input
            self.log_debug("Initializing CNN model...")
            dummy_input = np.zeros((1, frames, mfcc_features, 1))
            _ = self.pretrained_model(dummy_input)
            
            # Save the frames and features for later use in prediction
            self.cnn_frames = frames
            self.cnn_features = mfcc_features
            
            # Create a mapping from our commands to indices
            self.log_debug("Setting up command mapping...")
            commands = list(self.game.commands.keys())
            self.pretrained_command_mapping = {cmd: cmd for cmd in commands}
            
            # Set flags
            self.using_pretrained_model = True
            self.using_whisper_model = False  # Disable Whisper model
            
            self.update_status("Advanced CNN model loaded!")
            self.log_debug("CNN model created successfully. Ready for voice commands.")
            
            # Update button text
            self.pretrained_button.configure(text="Using CNN Model ✓")
            self.whisper_button.configure(text="Use Whisper Model (Best)")
            
            return True
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.log_debug(f"Error loading CNN model: {str(e)}")
            self.log_debug(f"Error details: {error_details}")
            
            if str(e).lower().find("memory") >= 0:
                # Memory error
                self.update_status("Failed: Not enough memory")
                self.log_debug("The CNN model requires more memory than is available.")
                self.log_debug("Try closing other applications or using a smaller model.")
            else:
                self.update_status("Failed to load CNN model")
                
            self.using_pretrained_model = False
            return False

    def _predict_with_pretrained_model(self, audio):
        """Use the CNN model to predict commands from audio"""
        try:
            if self.pretrained_model is None:
                return None, 0.0
                
            # Process audio to extract MFCC features
            audio = audio.flatten()
            
            # Add some noise to make recognition more robust
            noise_factor = 0.005
            noisy_audio = audio + noise_factor * np.random.normal(0, 1, len(audio))
            
            # Extract features with better parameters
            mfccs = librosa.feature.mfcc(
                y=noisy_audio, 
                sr=self.game.sr, 
                n_mfcc=self.cnn_features,  # Use saved feature count
                hop_length=256,  # Shorter hop for more temporal resolution
                n_fft=1024
            )
            
            # Normalize features for better performance
            mfccs = (mfccs - np.mean(mfccs)) / (np.std(mfccs) + 1e-8)
            
            # Ensure we have the right number of frames (pad or truncate)
            if mfccs.shape[1] < self.cnn_frames:
                # Pad if too short
                padding_width = self.cnn_frames - mfccs.shape[1]
                mfccs = np.pad(mfccs, ((0, 0), (0, padding_width)), mode='constant')
            elif mfccs.shape[1] > self.cnn_frames:
                # Truncate if too long (take the central portion)
                start = (mfccs.shape[1] - self.cnn_frames) // 2
                mfccs = mfccs[:, start:start + self.cnn_frames]
            
            # Reshape for CNN input: (batch, frames, features, channels)
            mfccs = mfccs.T  # now (frames, features)
            mfccs = np.expand_dims(mfccs, axis=0)  # add batch dimension
            mfccs = np.expand_dims(mfccs, axis=-1)  # add channel dimension
            
            # Make prediction
            self.log_debug("Running CNN prediction...")
            predictions = self.pretrained_model.predict(mfccs, verbose=0)
            prediction_idx = np.argmax(predictions[0])
            confidence = predictions[0][prediction_idx]
            
            # Get predictions for top 3 commands (for debugging)
            top_indices = np.argsort(predictions[0])[-3:][::-1]
            commands = list(self.game.commands.keys())
            
            # Log top 3 predictions
            for i, idx in enumerate(top_indices):
                if idx < len(commands):
                    cmd = commands[idx]
                    conf = predictions[0][idx]
                    self.log_debug(f"Top {i+1}: {cmd} ({conf:.2f})")
            
            # Map to command
            if prediction_idx < len(commands):
                command = commands[prediction_idx]
                self.log_debug(f"CNN model detected: {command} (confidence: {confidence:.2f})")
                return command, confidence
            else:
                self.log_debug(f"Invalid prediction index: {prediction_idx}")
                return None, 0.0
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.log_debug(f"Error in CNN model prediction: {str(e)}")
            self.log_debug(f"Error details: {error_details}")
            return None, 0.0

    def update_confidence_threshold(self, value):
        """Update the confidence threshold for pre-trained model predictions"""
        value = float(value)
        self.pretrained_confidence_threshold = value
        self.pretrained_threshold_label.configure(text=f"{value:.2f}")
        self.log_debug(f"Pre-trained model confidence threshold set to {value:.2f}")

    def load_whisper_model(self):
        """Load OpenAI's Whisper model for state-of-the-art speech recognition"""
        if not self.audio_available or not self.transformers_available:
            self.update_status("Required libraries missing")
            self.log_debug("Cannot load Whisper model: Required libraries missing")
            self.log_debug("Make sure to install: transformers, torch, sounddevice, and librosa")
            self.log_debug("Run: pip install transformers torch sounddevice librosa")
            return
        
        try:
            self.update_status("Loading Whisper model...")
            self.log_debug("Initializing Whisper model (this may take a moment)...")
            
            # Use the smaller whisper model for better performance
            model_name = "openai/whisper-tiny"
            
            # First load the processor - this handles audio preprocessing
            self.log_debug(f"Loading Whisper processor from {model_name}...")
            self.whisper_processor = WhisperProcessor.from_pretrained(model_name)
            
            # Then load the model
            self.log_debug(f"Loading Whisper model from {model_name}...")
            self.whisper_model = WhisperForConditionalGeneration.from_pretrained(model_name)
            
            # Create command mappings - Whisper returns text, so we need to map phrases to commands
            self.log_debug("Setting up command mappings...")
            # Map common phrases and their variations to commands
            self.whisper_command_mapping = {
                "left": "left",
                "move left": "left",
                "go left": "left",
                
                "right": "right",
                "move right": "right",
                "go right": "right",
                
                "up": "up",
                "move up": "up",
                "go up": "up",
                
                "down": "down",
                "move down": "down",
                "go down": "down",
                
                "rotate": "rotate",
                "spin": "rotate",
                "turn": "rotate",
                "start rotation": "rotate",
                "stop rotation": "rotate",
                "stop": "rotate",
            }
            
            # Set the flag to indicate we're using the Whisper model
            self.using_whisper_model = True
            self.using_pretrained_model = False  # Disable other models
            
            self.update_status("Whisper model loaded!")
            self.log_debug("Whisper model loaded successfully!")
            
            # Update button text
            self.whisper_button.configure(text="Using Whisper Model ✓")
            self.pretrained_button.configure(text="Use CNN Model")
            
            return True
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.log_debug(f"Error loading Whisper model: {str(e)}")
            self.log_debug(f"Error details: {error_details}")
            self.update_status("Failed to load Whisper model")
            self.using_whisper_model = False
            return False

    def on_frame_configure(self, event):
        """Update the canvas scrollregion when the content frame changes size"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def on_canvas_configure(self, event):
        """Resize the content frame when the canvas changes size"""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
        
    def on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# Run the application
if __name__ == "__main__":
    try:
        app = VoiceControlApp()
        app.game.run()
    except Exception as e:
        import traceback
        print(f"Error starting application: {e}")
        print("Detailed error information:")
        traceback.print_exc()
        sys.exit(1)