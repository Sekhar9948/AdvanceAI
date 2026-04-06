
import customtkinter as ctk
import cv2
import os
import time
import threading
from PIL import Image, ImageTk
import numpy as np
import tensorflow as tf

import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from language_manager import LanguageManager

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
model_path = os.path.join(project_root, 'trained_models/object_classification')
dataset_path = os.path.join(project_root, 'dataset/object_data')

# Set theme and color scheme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModernTrainingApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.translator = LanguageManager()
        self.translator.load_language("en")

        self.root.title(self.translator.get("object_trainer_title"))
        self.root.geometry("1280x800")

        
        
        # Define color scheme
        self.colors = {
            "primary": "#1f6aa5",
            "secondary": "#2d8fd5",
            "accent": "#ff6b6b",
            "success": "#6bff6b",
            "warning": "#ffcc00",
            "background": "#1a1a1a",
            "card": "#2a2a2a",
            "text": "#ffffff"
        }
        
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=3)
        self.root.grid_rowconfigure(0, weight=0)  # Header row doesn't need to expand
        self.root.grid_rowconfigure(1, weight=1)  # Main content row should expand
        
        # Variables
        self.class_labels = []
        self.num_objects = 0
        self.recording = False
        self.camera_active = False
        self.current_recording_class = None
        self.inference_mode = False
        self.model = None
        self.class_names = []
        
        # Create placeholder image for the camera feed - MOVED BEFORE create_right_panel
        self.create_placeholder_image()
        
        # Create main containers
        self.create_header()
        self.create_left_panel()
        self.create_right_panel()
        
        # Initialize camera
        self.cap = None
        self.camera_thread = None
        
    def create_placeholder_image(self):
        # Create a black image with "No Camera Feed" text
        placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add text to the center of the image
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = "No Camera Feed"
        textsize = cv2.getTextSize(text, font, 1, 2)[0]
        text_x = (placeholder.shape[1] - textsize[0]) // 2
        text_y = (placeholder.shape[0] + textsize[1]) // 2
        cv2.putText(placeholder, text, (text_x, text_y), font, 1, (200, 200, 200), 2)
        
        # Convert to PhotoImage
        self.placeholder_image = ImageTk.PhotoImage(image=Image.fromarray(placeholder))
        
    def create_header(self):
        # Create header frame
        self.header_frame = ctk.CTkFrame(self.root, fg_color=self.colors["primary"], corner_radius=0, height=60)
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.header_frame.grid_propagate(False)
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_rowconfigure(0, weight=1)
        
        # App title
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="Object Classification Trainer", 
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=self.colors["text"]
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # Status indicator
        self.status_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.status_frame.grid(row=0, column=1, padx=20, pady=10, sticky="e")
        
        self.status_indicator = ctk.CTkLabel(
            self.status_frame,
            text="●",
            font=ctk.CTkFont(size=24),
            text_color=self.colors["warning"]
        )
        self.status_indicator.pack(side="left", padx=(0, 5))
        
        self.status_text = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text"]
        )
        self.status_text.pack(side="left")
        
    def create_left_panel(self):
        # Main container for left panel
        self.left_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.left_container.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.left_container.grid_rowconfigure(0, weight=1)
        self.left_container.grid_columnconfigure(0, weight=1)
        
        # Left panel for controls with scrollable frame
        self.left_frame = ctk.CTkScrollableFrame(
            self.left_container,
            fg_color=self.colors["card"],
            corner_radius=10,
            border_width=0
        )
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        
        # Title for control panel
        self.control_title = ctk.CTkLabel(
            self.left_frame,
            text="Training Controls",
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color=self.colors["text"]
        )
        self.control_title.pack(pady=(10, 20))
        
        # Class management section
        self.create_class_management_section()
        
        # Training parameters section
        self.create_training_parameters_section()
        
        # Start training button
        self.start_btn = ctk.CTkButton(
            self.left_frame,
            text="Start Training",
            command=self.start_training,
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            fg_color=self.colors["accent"],
            hover_color="#ff8c8c",
            corner_radius=8,
            height=45
        )
        self.start_btn.pack(pady=20, padx=20, fill="x")
        
        # Progress section
        self.create_progress_section()
        
        # Inference section - NEW
        self.create_inference_section()
        
    def create_class_management_section(self):
        # Class management section
        class_section = ctk.CTkFrame(self.left_frame, fg_color=self.colors["card"])
        class_section.pack(fill="x", padx=10, pady=5)
        
        # Section header with icon
        class_header = ctk.CTkFrame(class_section, fg_color="transparent")
        class_header.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            class_header, 
            text="Class Management", 
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color=self.colors["text"]
        ).pack(side="left", pady=5)
        
        # Container for class fields
        self.class_container = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.class_container.pack(fill="x", padx=10, pady=5)
        
        # Add class button
        self.add_class_btn = ctk.CTkButton(
            class_section,
            text="+ Add New Class",
            command=self.add_class_field,
            font=ctk.CTkFont(family="Helvetica", size=14),
            fg_color=self.colors["secondary"],
            hover_color="#3da1e8",
            corner_radius=8
        )
        self.add_class_btn.pack(pady=10, padx=10, fill="x")
    
    def create_training_parameters_section(self):
        # Training parameters section
        params_section = ctk.CTkFrame(self.left_frame, fg_color=self.colors["card"])
        params_section.pack(fill="x", padx=10, pady=15)
        
        ctk.CTkLabel(
            params_section, 
            text="Training Parameters", 
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color=self.colors["text"]
        ).pack(pady=10)
        
        # Parameters grid
        params_grid = ctk.CTkFrame(params_section, fg_color="transparent")
        params_grid.pack(fill="x", padx=15, pady=5)
        
        # Frames per object
        frames_row = ctk.CTkFrame(params_grid, fg_color="transparent")
        frames_row.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            frames_row, 
            text="Frames per object:", 
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text"]
        ).pack(side="left")
        
        self.frames_entry = ctk.CTkEntry(
            frames_row,
            fg_color=self.colors["background"],
            border_color=self.colors["secondary"],
            text_color=self.colors["text"],
            corner_radius=6,
            width=100
        )
        self.frames_entry.pack(side="right", padx=5)
        self.frames_entry.insert(0, "100")
        
        # Epochs
        epochs_row = ctk.CTkFrame(params_grid, fg_color="transparent")
        epochs_row.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            epochs_row, 
            text="Epochs:", 
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text"]
        ).pack(side="left")
        
        self.epochs_entry = ctk.CTkEntry(
            epochs_row,
            fg_color=self.colors["background"],
            border_color=self.colors["secondary"],
            text_color=self.colors["text"],
            corner_radius=6,
            width=100
        )
        self.epochs_entry.pack(side="right", padx=5)
        self.epochs_entry.insert(0, "10")
        
        # Learning rate
        lr_row = ctk.CTkFrame(params_grid, fg_color="transparent")
        lr_row.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            lr_row, 
            text="Learning rate:", 
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text"]
        ).pack(side="left")
        
        self.lr_entry = ctk.CTkEntry(
            lr_row,
            fg_color=self.colors["background"],
            border_color=self.colors["secondary"],
            text_color=self.colors["text"],
            corner_radius=6,
            width=100
        )
        self.lr_entry.pack(side="right", padx=5)
        self.lr_entry.insert(0, "0.001")
    
    def create_progress_section(self):
        # Progress section
        progress_section = ctk.CTkFrame(self.left_frame, fg_color=self.colors["card"])
        progress_section.pack(fill="x", padx=10, pady=15)
        
        ctk.CTkLabel(
            progress_section, 
            text="Training Progress", 
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color=self.colors["text"]
        ).pack(pady=10)
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(
            progress_section,
            fg_color=self.colors["background"],
            progress_color=self.colors["accent"],
            height=15,
            corner_radius=5
        )
        self.progress.pack(fill="x", padx=15, pady=10)
        self.progress.set(0)
        
        # Time remaining label
        self.time_label = ctk.CTkLabel(
            progress_section, 
            text="Estimated time remaining: Calculating...",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text"]
        )
        self.time_label.pack(pady=10)
    
    def create_inference_section(self):
        # Inference section
        inference_section = ctk.CTkFrame(self.left_frame, fg_color=self.colors["card"])
        inference_section.pack(fill="x", padx=10, pady=15)
        
        ctk.CTkLabel(
            inference_section, 
            text="Inference Mode", 
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color=self.colors["text"]
        ).pack(pady=10)
        
        self.inference_btn = ctk.CTkButton(
            inference_section,
            text="Start Inference",
            command=self.toggle_inference_mode,
            font=ctk.CTkFont(family="Helvetica", size=14),
            fg_color=self.colors["secondary"],
            hover_color="#3da1e8",
            corner_radius=8
        )
        self.inference_btn.pack(pady=10, padx=10, fill="x")
        
        # Confidence threshold slider
        threshold_frame = ctk.CTkFrame(inference_section, fg_color="transparent")
        threshold_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            threshold_frame, 
            text="Confidence Threshold:", 
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text"]
        ).pack(side="left")
        
        self.threshold_value = ctk.CTkLabel(
            threshold_frame, 
            text="0.5", 
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text"]
        )
        self.threshold_value.pack(side="right")
        
        self.threshold_slider = ctk.CTkSlider(
            inference_section,
            from_=0.0,
            to=1.0,
            number_of_steps=20,
            command=self.update_threshold
        )
        self.threshold_slider.pack(fill="x", padx=10, pady=10)
        self.threshold_slider.set(0.5)
        
        # Last prediction label
        self.prediction_label = ctk.CTkLabel(
            inference_section, 
            text="No prediction yet", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text"]
        )
        self.prediction_label.pack(pady=10)
        
    def update_threshold(self, value):
        self.threshold_value.configure(text=f"{value:.2f}")
        
    def create_right_panel(self):
        # Right panel for camera and preview
        self.right_frame = ctk.CTkFrame(self.root, fg_color=self.colors["card"], corner_radius=10)
        self.right_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        # Configure grid for right panel
        self.right_frame.grid_rowconfigure(0, weight=0)  # Title
        self.right_frame.grid_rowconfigure(1, weight=1)  # Camera container
        self.right_frame.grid_rowconfigure(2, weight=0)  # Status
        self.right_frame.grid_rowconfigure(3, weight=0)  # Controls
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        # Camera section title
        self.camera_title = ctk.CTkLabel(
            self.right_frame,
            text="Camera Preview",
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color=self.colors["text"]
        )
        self.camera_title.grid(row=0, column=0, pady=(20, 10))
        
        # Camera view container - using grid instead of pack for better control
        self.camera_container = ctk.CTkFrame(
            self.right_frame, 
            fg_color=self.colors["background"], 
            corner_radius=8,
            height=480,  # Fixed height to match camera resolution
            width=640    # Fixed width to match camera resolution
        )
        self.camera_container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.camera_container.grid_propagate(False)  # Prevent resizing
        self.camera_container.grid_rowconfigure(0, weight=1)
        self.camera_container.grid_columnconfigure(0, weight=1)
        
        # Camera view
        self.camera_label = ctk.CTkLabel(
            self.camera_container, 
            text="",
            image=self.placeholder_image
        )
        self.camera_label.grid(row=0, column=0, sticky="nsew")
        
        # Recording status
        self.recording_status = ctk.CTkLabel(
            self.right_frame, 
            text="Camera Inactive", 
            font=ctk.CTkFont(family="Helvetica", size=16),
            text_color=self.colors["warning"]
        )
        self.recording_status.grid(row=2, column=0, pady=10)
        
        # Camera controls
        self.controls_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.controls_frame.grid(row=3, column=0, pady=20)
        
        self.camera_btn = ctk.CTkButton(
            self.controls_frame,
            text="Start Camera",
            command=self.toggle_camera,
            font=ctk.CTkFont(family="Helvetica", size=14),
            fg_color=self.colors["secondary"],
            hover_color="#3da1e8",
            corner_radius=8,
            width=150
        )
        self.camera_btn.pack(side="left", padx=10)
        
        self.stop_btn = ctk.CTkButton(
            self.controls_frame,
            text="Stop Camera",
            command=self.stop_camera,
            font=ctk.CTkFont(family="Helvetica", size=14),
            fg_color="#555555",
            hover_color="#777777",
            corner_radius=8,
            width=150,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=10)
        
    def toggle_camera(self):
        if not self.camera_active:
            self.start_camera()
            self.camera_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
        else:
            self.stop_camera()
            self.camera_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            
    def add_class_field(self):
        class_frame = ctk.CTkFrame(self.class_container, fg_color=self.colors["background"], corner_radius=8)
        class_frame.pack(fill="x", padx=10, pady=5)
        
        # Class name entry
        entry = ctk.CTkEntry(
            class_frame, 
            placeholder_text=f"Class Name {self.num_objects + 1}",
            fg_color=self.colors["card"],
            border_color=self.colors["secondary"],
            text_color=self.colors["text"],
            corner_radius=6
        )
        entry.pack(side="left", padx=5, pady=10, fill="x", expand=True)
        
        # Button container
        btn_container = ctk.CTkFrame(class_frame, fg_color="transparent")
        btn_container.pack(side="right", padx=5, pady=5)
        
        # Record button
        record_btn = ctk.CTkButton(
            btn_container,
            text="Record",
            command=lambda: self.toggle_recording(entry, record_btn),
            font=ctk.CTkFont(family="Helvetica", size=12),
            fg_color=self.colors["accent"],
            hover_color="#ff8c8c",
            corner_radius=6,
            width=80,
            height=30
        )
        record_btn.pack(side="left", padx=2)
        entry.record_btn = record_btn  # Store reference to record button
        
        # Remove button
        remove_btn = ctk.CTkButton(
            btn_container,
            text="✕",
            command=lambda: self.remove_class_field(class_frame, entry),
            font=ctk.CTkFont(family="Helvetica", size=12),
            fg_color="#555555",
            hover_color="#777777",
            corner_radius=6,
            width=30,
            height=30
        )
        remove_btn.pack(side="left", padx=2)
        
        self.class_labels.append(entry)
        self.num_objects += 1
        
    def remove_class_field(self, frame, entry):
        if self.current_recording_class == entry:
            self.recording = False
            self.current_recording_class = None
        frame.pack_forget()
        frame.destroy()
        self.class_labels.remove(entry)
        self.num_objects -= 1
        
    def toggle_recording(self, entry, record_btn):
        class_name = entry.get()
        if not class_name:
            return
            
        if not self.camera_active:
            self.start_camera()
            self.camera_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            
        if self.current_recording_class == entry:
            # Stop recording for this class
            self.recording = False
            self.current_recording_class = None
            record_btn.configure(
                text="Record",
                fg_color=self.colors["accent"]
            )
            self.recording_status.configure(
                text="Camera Active",
                text_color=self.colors["success"]
            )
            self.status_indicator.configure(text_color=self.colors["success"])
            self.status_text.configure(text="Camera Active")
        else:
            # Stop any ongoing recording
            if self.current_recording_class:
                self.current_recording_class.record_btn.configure(
                    text="Record",
                    fg_color=self.colors["accent"]
                )
            
            # Start recording for this class
            self.recording = True
            self.current_recording_class = entry
            record_btn.configure(
                text="Stop",
                fg_color="#ff3333"
            )
            self.recording_status.configure(
                text=f"Recording {class_name}...",
                text_color="#ff3333"
            )
            self.status_indicator.configure(text_color="#ff3333")
            self.status_text.configure(text=f"Recording {class_name}")
            
            # Start recording frames in a separate thread
            recording_thread = threading.Thread(
                target=self.record_frames,
                args=(entry, record_btn)
            )
            recording_thread.daemon = True
            recording_thread.start()
            
    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.camera_active = True
        self.camera_thread = threading.Thread(target=self.update_camera)
        self.camera_thread.daemon = True
        self.camera_thread.start()
        
        self.recording_status.configure(
            text="Camera Active",
            text_color=self.colors["success"]
        )
        self.status_indicator.configure(text_color=self.colors["success"])
        self.status_text.configure(text="Camera Active")
        
    def stop_camera(self):
        self.camera_active = False
        if self.cap is not None:
            self.cap.release()
        
        # Reset to placeholder image
        self.camera_label.configure(image=self.placeholder_image, text="")
        
        self.recording_status.configure(
            text="Camera Inactive",
            text_color=self.colors["warning"]
        )
        self.status_indicator.configure(text_color=self.colors["warning"])
        self.status_text.configure(text="Ready")
        
        self.camera_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        
        if self.inference_mode:
            self.inference_mode = False
            self.inference_btn.configure(
                text="Start Inference",
                fg_color=self.colors["secondary"]
            )
        
    def update_camera(self):
        while self.camera_active:
            ret, frame = self.cap.read()
            if ret:
                # Convert frame to RGB for display
                display_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                display_frame = cv2.resize(display_frame, (640, 480))
                
                if self.inference_mode and self.model is not None:
                    # Perform inference
                    class_index, confidence = self.predict_object(frame)
                    threshold = self.threshold_slider.get()
                    
                    if confidence >= threshold:
                        predicted_label = self.class_names[class_index]
                        # Update UI with prediction
                        self.prediction_label.configure(
                            text=f"Predicted: {predicted_label} ({confidence:.2f})",
                            text_color=self.colors["success"]
                        )
                        
                        # Display prediction on frame
                        cv2.putText(
                            display_frame, 
                            f"{predicted_label}: {confidence:.2f}", 
                            (20, 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            0.8, 
                            (0, 255, 0), 
                            2
                        )
                    else:
                        # Below threshold
                        self.prediction_label.configure(
                            text=f"Confidence too low ({confidence:.2f})",
                            text_color=self.colors["warning"]
                        )
                        
                        # Display on frame
                        cv2.putText(
                            display_frame, 
                            f"Confidence: {confidence:.2f}", 
                            (20, 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            0.8, 
                            (255, 165, 0), 
                            2
                        )
                
                # Add recording indicator if recording
                elif self.recording and self.current_recording_class:
                    # Add red circle in top-right corner
                    cv2.circle(display_frame, (620, 20), 10, (255, 0, 0), -1)
                    
                    # Add frame counter
                    class_name = self.current_recording_class.get()
                    save_dir = f'{dataset_path}/{class_name}'
                    print(save_dir)
                    if os.path.exists(save_dir):
                        frame_count = len(os.listdir(save_dir))
                        frames_total = int(self.frames_entry.get())
                        cv2.putText(
                            display_frame, 
                            f"Frames: {frame_count}/{frames_total}", 
                            (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            0.7, 
                            (255, 0, 0), 
                            2
                        )
                
                # Convert to PhotoImage and update display
                photo = ImageTk.PhotoImage(image=Image.fromarray(display_frame))
                self.camera_label.configure(image=photo)
                self.camera_label.image = photo
                
                # Update status based on mode
                if self.inference_mode:
                    self.recording_status.configure(
                        text="Inference Mode Active",
                        text_color=self.colors["secondary"]
                    )
                elif self.recording and self.current_recording_class:
                    class_name = self.current_recording_class.get()
                    self.recording_status.configure(
                        text=f"Recording {class_name}...",
                        text_color="#ff3333"
                    )
                else:
                    self.recording_status.configure(
                        text="Camera Active",
                        text_color=self.colors["success"]
                    )
            
            time.sleep(0.03)  # Limit frame rate to reduce CPU usage
                    
    def record_frames(self, entry, record_btn):
        class_name = entry.get()
        if not class_name:
            return
            
        frames = int(self.frames_entry.get())
        save_dir = f'{dataset_path}/{class_name}'
        
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        frames_captured = 0
        while frames_captured < frames and self.recording:
            ret, frame = self.cap.read()
            if ret:
                cv2.imwrite(os.path.join(save_dir, f"{frames_captured}.jpg"), frame)
                frames_captured += 1
                self.recording_status.configure(
                    text=f"Recording {class_name}... ({frames_captured}/{frames} frames)",
                    text_color="#ff3333"
                )
                time.sleep(0.05)  # Slight delay to avoid overwhelming the system
                
        self.recording = False
        self.current_recording_class = None
        record_btn.configure(
            text="Record",
            fg_color=self.colors["accent"]
        )
        self.recording_status.configure(
            text="Recording Complete",
            text_color=self.colors["success"]
        )
        self.status_indicator.configure(text_color=self.colors["success"])
        self.status_text.configure(text="Recording Complete")
        
    def start_training(self):
        print(self.class_labels)
        if len(self.class_labels) < 2:
            self.time_label.configure(text="Error: Add at least 2 classes for training!")
            return
            
        num_frames = int(self.frames_entry.get())
        epochs = int(self.epochs_entry.get())
        lr = float(self.lr_entry.get())
        object_names = [entry.get() for entry in self.class_labels if entry.get().strip()]
        
        # Check if we have class names
        if not object_names:
            self.time_label.configure(text="Error: No class names provided!")
            return
            
        # Save class names to file
        with open("class_names.txt", 'w') as f:
            for name in object_names:
                f.write(f"{name}\n")
                    
        self.progress.set(0)
        self.start_btn.configure(state="disabled", text="Training...")
        self.time_label.configure(text="Preparing training data...")
        
        # Start training in a separate thread
        training_thread = threading.Thread(target=self.train_model, args=(object_names, epochs, lr))
        training_thread.daemon = True
        training_thread.start()

    def train_model(self, class_names, epochs, learning_rate):
        try:
            # Update UI
            self.status_indicator.configure(text_color="#ffcc00")
            self.status_text.configure(text="Training Model")
            
            # Store class names for inference
            self.class_names = class_names
            
            # Set up dataset paths
            dataset_dir = dataset_path
            
            # Check if dataset exists for all classes
            for class_name in class_names:
                class_dir = os.path.join(dataset_dir, class_name)
                if not os.path.exists(class_dir) or len(os.listdir(class_dir)) == 0:
                    self.update_training_status(f"Error: No frames found for class '{class_name}'")
                    return
            
            # Create image data generator for augmentation
            self.update_training_status("Preprocessing images...")
            
            # Define image size
            img_height, img_width = 224, 224
            batch_size = 32
            
            # Create a data generator with augmentation for training
            datagen = tf.keras.preprocessing.image.ImageDataGenerator(
                rescale=1.0/255,
                validation_split=0.2,
                rotation_range=20,
                width_shift_range=0.2,
                height_shift_range=0.2,
                horizontal_flip=True,
                zoom_range=0.2
            )
            
            # Load training dataset
            train_generator = datagen.flow_from_directory(
                dataset_dir,
                target_size=(img_height, img_width),
                batch_size=batch_size,
                class_mode='categorical',
                subset='training',
                shuffle=True
            )
            
            # Load validation dataset
            validation_generator = datagen.flow_from_directory(
                dataset_dir,
                target_size=(img_height, img_width),
                batch_size=batch_size,
                class_mode='categorical',
                subset='validation',
                shuffle=False
            )
            
            num_classes = len(class_names)
            
            # Create a model based on MobileNetV2
            self.update_training_status("Creating model architecture...")
            
            # Use a pre-trained model
            base_model = tf.keras.applications.MobileNetV2(
                input_shape=(img_height, img_width, 3),
                include_top=False,
                weights='imagenet'
            )
            
            # Freeze the base model
            base_model.trainable = False
            
            # Create the model architecture
            model = tf.keras.Sequential([
                base_model,
                tf.keras.layers.GlobalAveragePooling2D(),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(128, activation='relu'),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(num_classes, activation='softmax')
            ])
            
            # Compile the model
            model.compile(
                optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            # Set up callbacks
            class ProgressCallback(tf.keras.callbacks.Callback):
                def __init__(self, app):
                    super().__init__()
                    self.app = app
                    self.start_time = time.time()
                    
                def on_epoch_begin(self, epoch, logs=None):
                    self.epoch_start_time = time.time()
                    
                def on_epoch_end(self, epoch, logs=None):
                    # Calculate progress
                    progress = (epoch + 1) / epochs
                    self.app.progress.set(progress)
                    
                    # Calculate time remaining
                    elapsed_time = time.time() - self.start_time
                    estimated_total = elapsed_time / progress
                    remaining = estimated_total - elapsed_time
                    
                    # Format time remaining
                    mins = int(remaining // 60)
                    secs = int(remaining % 60)
                    
                    # Update UI with training metrics
                    self.app.update_training_status(
                        f"Epoch {epoch+1}/{epochs} - "
                        f"Loss: {logs['loss']:.4f} - "
                        f"Accuracy: {logs['accuracy']:.4f} - "
                        f"Time remaining: {mins}m {secs}s"
                    )
            
            # Start training
            self.update_training_status("Training started...")
            model.fit(
                train_generator,
                epochs=epochs,
                validation_data=validation_generator,
                callbacks=[ProgressCallback(self)]
            )
            
            # Save the model
            model_dir = model_path
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)
                
            model_path = os.path.join(model_dir, "object_classifier.h5")
            model.save(model_path)
            
            # Save the class names with the model
            self.model = model
            
            # Training complete
            self.update_training_status("Training complete!")
            self.status_indicator.configure(text_color=self.colors["success"])
            self.status_text.configure(text="Training Complete")
            
            # Enable the inference button
            self.inference_btn.configure(state="normal")
            
        except Exception as e:
            self.update_training_status(f"Error during training: {str(e)}")
            
        finally:
            # Re-enable the start button
            self.start_btn.configure(state="normal", text="Start Training")

    def update_training_status(self, text):
        # Update UI from any thread
        self.root.after(0, lambda: self.time_label.configure(text=text))

    def toggle_inference_mode(self):
        if not self.model:
            self.time_label.configure(text="Error: No trained model available. Train the model first!")
            return
            
        # Toggle inference mode
        self.inference_mode = not self.inference_mode
        
        if self.inference_mode:
            # Start camera if not already active
            if not self.camera_active:
                self.start_camera()
                self.camera_btn.configure(state="disabled")
                self.stop_btn.configure(state="normal")
                
            # Load class names if needed
            if not self.class_names and os.path.exists("class_names.txt"):
                with open("class_names.txt", "r") as f:
                    self.class_names = [line.strip() for line in f.readlines()]
                    
            self.inference_btn.configure(
                text="Stop Inference",
                fg_color="#ff6b6b"
            )
            self.recording_status.configure(
                text="Inference Mode Active",
                text_color=self.colors["secondary"]
            )
            self.status_indicator.configure(text_color=self.colors["secondary"])
            self.status_text.configure(text="Inference Mode")
            
        else:
            self.inference_btn.configure(
                text="Start Inference",
                fg_color=self.colors["secondary"]
            )
            self.recording_status.configure(
                text="Camera Active",
                text_color=self.colors["success"]
            )
            self.status_indicator.configure(text_color=self.colors["success"])
            self.status_text.configure(text="Camera Active")
            self.prediction_label.configure(text="No prediction yet")

    def predict_object(self, frame):
        # Preprocess the frame for prediction
        img = cv2.resize(frame, (224, 224))
        img = img / 255.0  # Normalize
        img = np.expand_dims(img, axis=0)  # Add batch dimension
        
        # Make prediction
        predictions = self.model.predict(img)
        class_index = np.argmax(predictions[0])
        confidence = float(predictions[0][class_index])
        
        return class_index, confidence

    def run(self):
        # Check if dataset directory exists
        if not os.path.exists(dataset_path):
            os.makedirs(dataset_path)
            
        # Check if models directory exists
        if not os.path.exists("models"):
            os.makedirs("models")
        
        # Load existing model if available
        model_path1 = os.path.join(model_path, "object_classifier.h5")
        if os.path.exists(model_path1):
            try:
                self.model = tf.keras.models.load_model(model_path1)
                # Load class names
                if os.path.exists("class_names.txt"):
                    with open("class_names.txt", "r") as f:
                        self.class_names = [line.strip() for line in f.readlines()]
                self.time_label.configure(text="Loaded existing model")
            except Exception as e:
                self.time_label.configure(text=f"Could not load model: {str(e)}")
        
        # Start the application
        self.root.mainloop()

    # Main entry point
if __name__ == "__main__":
    app = ModernTrainingApp()
    app.run()