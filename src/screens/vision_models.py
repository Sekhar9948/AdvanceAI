
import customtkinter as ctk
from .base_model_screen import BaseModelScreen
import os
import sys
import subprocess

# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../tool_gui'))
class VisionModelsScreen(BaseModelScreen):
    def __init__(self, parent, theme_manager=None, translator=None):
        self.translator = translator
        title = self.translator.t("vision_models")
        description = self.translator.t("vision_main_description")
        
        # Initialize base screen
        super().__init__(
            parent,
            theme_manager=theme_manager,
            title=title,
            description=description
        )
        
        # Add vision models
        self.add_vision_models()
    
    def add_vision_models(self):
        """Add vision models to the list."""
        # Hand Gesture Detection
        self.add_model(
            title=self.translator.t("hand_gesture"),
            description=self.translator.t("hand_gesture_desc"),
            icon_path=None
        )
        
        # Object Classification
        self.add_model(
            self.translator.t("object_classification"),
            self.translator.t("object_classification_desc"),
            icon_path=None
        )
        
        # Facial Emotion Detection
        self.add_model(
            self.translator.t("facial_emotion"),
            self.translator.t("facial_emotion_desc"),

            icon_path=None
        )
        
        self.add_model(
           self.translator.t("digit_classification"),
            self.translator.t("digit_classification_desc"),
            icon_path=None
        )
    
    def show_model_preview(self, model_title):
        """Show preview content for the selected model."""
        # Clear existing preview content
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        
        if model_title == self.translator.t("facial_emotion"):
            self.load_facial_emotion_preview()
        elif model_title == self.translator.t("digit_classification"):
            self.load_digit_classification_preview()
        elif model_title == self.translator.t("hand_gesture"):
            self.load_hand_gesture_preview()
        elif model_title == self.translator.t("object_classification"):
            self.load_object_classification_preview()
    
    def load_facial_emotion_preview(self):
        """Create preview content for Facial Emotion Detection."""
        # Description
        description = self.translator.t("facial_emotion_full_desc")
        
        desc_label = ctk.CTkLabel(
            self.preview_frame,
            text=description,
            wraplength=600,
            justify="left",
            font=ctk.CTkFont(size=14)
        )
        desc_label.pack(pady=20)
        
        # Feature highlights
        features_frame = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        features_frame.pack(fill="x", padx=20, pady=10)
        
        features =  [
            self.translator.t("feature_emotion_1"),
            self.translator.t("feature_emotion_2"),
        ]
        
        for feature in features:
            feature_label = ctk.CTkLabel(
                features_frame,
                text=f"• {feature}",
                justify="left",
                font=ctk.CTkFont(size=14)
            )
            feature_label.pack(anchor="w", pady=5)
        
        # Launch button
        launch_button = ctk.CTkButton(
            self.preview_frame,
            text=self.translator.t("launch_facial_emotion"),
            command=self.launch_facial_emotion_interface,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        launch_button.pack(pady=20)
        
        # Required dependencies
        deps_frame = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        deps_frame.pack(fill="x", padx=20, pady=10)
        
        deps_label = ctk.CTkLabel(
            deps_frame,
            text=self.translator.t("dependencies"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        deps_label.pack(anchor="w")
        
        deps = [
            self.translator.t("opencv"),
            self.translator.t("tensorflow"),
            self.translator.t("numpy"),
            self.translator.t("pandas")
        ]
        
        for dep in deps:
            dep_label = ctk.CTkLabel(
                deps_frame,
                text=f"• {dep}",
                justify="left",
                font=ctk.CTkFont(size=14)
            )
            dep_label.pack(anchor="w", pady=2)
    
    def launch_facial_emotion_interface(self):
        """Launch the Facial Emotion Detection interface."""
        try:
            # Get the path to the facial_emotion_detection.py file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up two levels to reach the EdvanceAI root directory
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            model_path = os.path.join(root_dir, "tool_gui/emotion_detection/facial_emotion_detection.py")
            
            if not os.path.exists(model_path):
                # Try alternative path (directly in workspace root)
                model_path = os.path.join(os.getcwd(), "tool_gui/emotion_detection/facial_emotion_detection.py")
                
                if not os.path.exists(model_path):
                    raise FileNotFoundError(
                        "Facial emotion detection interface file not found. "
                        "Please ensure facial_emotion_detection.py is in the workspace root directory."
                    )
            
            # Launch the interface in a new process
            subprocess.Popen([sys.executable, model_path])
            
            # Show success message
            self.show_message(self.translator.t("launching_emotion"))
            
        except Exception as e:
            self.show_error(self.translator.t("error_launch"))
            # Add more detailed error logging
            print(f"Error details: {str(e)}")
            print(f"Current directory: {os.getcwd()}")
            print(f"Attempted path: {model_path}")
    
    def load_digit_classification_preview(self):
        """Create preview content for Digit Classification."""
        # Description
        description = self.translator.t("digit_full_desc")
        
        desc_label = ctk.CTkLabel(
            self.preview_frame,
            text=description,
            wraplength=600,
            justify="left",
            font=ctk.CTkFont(size=14)
        )
        desc_label.pack(pady=20)
        
        # Feature highlights
        features_frame = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        features_frame.pack(fill="x", padx=20, pady=10)
        
        features = [
            self.translator.t("digit_feature_1"),
            self.translator.t("digit_feature_2"),
            self.translator.t("digit_feature_3"),
            self.translator.t("digit_feature_4"),
        ]
        
        for feature in features:
            feature_label = ctk.CTkLabel(
                features_frame,
                text=f"• {feature}",
                justify="left",
                font=ctk.CTkFont(size=14)
            )
            feature_label.pack(anchor="w", pady=5)
        
        # Launch button
        launch_button = ctk.CTkButton(
            self.preview_frame,
            text=self.translator.t("launch_digit"),
            command=self.launch_digit_classification_interface,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        launch_button.pack(pady=20)

    def launch_digit_classification_interface(self):
        """Launch the Digit Classification interface."""
        try:
            # Get the path to the digit_main_gui.py file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up two levels to reach the EdvanceAI root directory
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            model_path = os.path.join(root_dir, "tool_gui/digit_detection/digit_main_gui.py")
            
            if not os.path.exists(model_path):
                # Try alternative path (directly in workspace root)
                model_path = os.path.join(os.getcwd(), "tool_gui/digit_detection/digit_main_gui.py")
                
                if not os.path.exists(model_path):
                    raise FileNotFoundError(
                        "Digit classification interface file not found. "
                        "Please ensure digit_main_gui.py is in the workspace root directory."
                    )
            
            # Launch the interface in a new process
            subprocess.Popen([sys.executable, model_path])
            
            # Show success message
            self.show_message(self.translator.t("launching_digit"))
            
        except Exception as e:
            self.show_error(self.translator.t("error_launch"))
            # Add more detailed error logging
            print(f"Error details: {str(e)}")
            print(f"Current directory: {os.getcwd()}")
            print(f"Attempted path: {model_path}")
    
    def load_hand_gesture_preview(self):
        """Create preview content for Hand Gesture Detection."""
        # Description
        description = self.translator.t("hand_gesture_full_desc")
        
        desc_label = ctk.CTkLabel(
            self.preview_frame,
            text=description,
            wraplength=600,
            justify="left",
            font=ctk.CTkFont(size=14)
        )
        desc_label.pack(pady=20)
        
        # Feature highlights
        features_frame = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        features_frame.pack(fill="x", padx=20, pady=10)
        
        features = [
            self.translator.t("hand_gesture_feature_1"),
            self.translator.t("hand_gesture_feature_2"),
            self.translator.t("hand_gesture_feature_3"),
            self.translator.t("hand_gesture_feature_4"),
        ]
        
        for feature in features:
            feature_label = ctk.CTkLabel(
                features_frame,
                text=f"• {feature}",
                justify="left",
                font=ctk.CTkFont(size=14)
            )
            feature_label.pack(anchor="w", pady=5)
        
        # Launch button
        launch_button = ctk.CTkButton(
            self.preview_frame,
            text=self.translator.t("launch_hand_gesture"),
            command=self.launch_hand_gesture_interface,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        launch_button.pack(pady=20)

    def launch_hand_gesture_interface(self):
        """Launch the Hand Gesture Detection interface."""
        try:
            # Get the path to the gesture_main_gui.py file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up two levels to reach the EdvanceAI root directory
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            model_path = os.path.join(root_dir, "tool_gui/hand_gesture/gesture_main_gui.py")
            
            if not os.path.exists(model_path):
                # Try alternative path (directly in workspace root)
                model_path = os.path.join(os.getcwd(), "tool_gui/hand_gesture/gesture_main_gui.py")
                
                if not os.path.exists(model_path):
                    raise FileNotFoundError(
                        "Hand gesture detection interface file not found. "
                        "Please ensure gesture_main_gui.py is in the workspace root directory."
                    )
            
            # Launch the interface in a new process
            subprocess.Popen([sys.executable, model_path])
            
            # Show success message
            self.show_message(self.translator.t("launching_hand_gesture"))
            
        except Exception as e:
            self.show_error(self.translator.t("error_launch"))
            # Add more detailed error logging
            print(f"Error details: {str(e)}")
            print(f"Current directory: {os.getcwd()}")
            print(f"Attempted path: {model_path}")
    
    def load_object_classification_preview(self):
        """Create preview content for Object Classification."""
        # Description
        description = self.translator.t("hand_gesture_full_desc")
        
        desc_label = ctk.CTkLabel(
            self.preview_frame,
            text=description,
            wraplength=600,
            justify="left",
            font=ctk.CTkFont(size=14)
        )
        desc_label.pack(pady=20)
        
        # Feature highlights
        features_frame = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        features_frame.pack(fill="x", padx=20, pady=10)
        
        features = [
            self.translator.t("object_feature_1"),
            self.translator.t("object_feature_2"),
            self.translator.t("object_feature_3"),
            self.translator.t("object_feature_4"),
        ]
        
        for feature in features:
            feature_label = ctk.CTkLabel(
                features_frame,
                text=f"• {feature}",
                justify="left",
                font=ctk.CTkFont(size=14)
            )
            feature_label.pack(anchor="w", pady=5)
        
        # Launch button
        launch_button = ctk.CTkButton(
            self.preview_frame,
            text=self.translator.t("launch_object"),
            command=self.launch_object_classification_interface,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        launch_button.pack(pady=20)

    def launch_object_classification_interface(self):
        """Launch the Object Classification interface."""
        try:
            # Get the path to the object_main_gui.py file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up two levels to reach the EdvanceAI root directory
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            model_path = os.path.join(root_dir, "tool_gui/object_detection/object_main_gui.py")
            
            if not os.path.exists(model_path):
                # Try alternative path (directly in workspace root)
                model_path = os.path.join(os.getcwd(), "tool_gui/object_detection/object_main_gui.py")
                
                if not os.path.exists(model_path):
                    raise FileNotFoundError(
                        "Object classification interface file not found. "
                        "Please ensure object_main_gui.py is in the workspace root directory."
                    )
            
            # Launch the interface in a new process
            subprocess.Popen([sys.executable, model_path])
            
            # Show success message
            self.show_message(self.translator.t("launching_object"))
            
        except Exception as e:
            self.show_error(self.translator.t("error_launch"))
            # Add more detailed error logging
            print(f"Error details: {str(e)}")
            print(f"Current directory: {os.getcwd()}")
            print(f"Attempted path: {model_path}")
    
    def show_message(self, message):
        """Show a message in the preview area."""
        message_label = ctk.CTkLabel(
            self.preview_frame,
            text=message,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        message_label.pack(pady=10)
    
    def show_error(self, message):
        """Show an error message in the preview area."""
        error_label = ctk.CTkLabel(
            self.preview_frame,
            text=message,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#FF3B30"  # Red color for errors
        )
        error_label.pack(pady=10) 