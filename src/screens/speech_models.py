
import customtkinter as ctk
from .base_model_screen import BaseModelScreen
import os
from panda3d.core import loadPrcFileData
import sys
import subprocess
from src.translator import Translator

# Configure Panda3D window before initialization
loadPrcFileData("", "window-title Panda3D Model")
loadPrcFileData("", "win-size 800 600")
loadPrcFileData("", "win-origin 50 50")
loadPrcFileData("", "threading-model None")  # Use single-threaded model for Panda3D

class SpeechModelsScreen(BaseModelScreen):
    def __init__(self, parent, theme_manager=None, translator=None):
        self.translator = translator if translator else Translator("en")
        title = self.translator.t("speech_models")
        description = self.translator.t("speech_main_description")
        
        # Initialize base screen
        super().__init__(
            parent,
            theme_manager=theme_manager,
            title=title,
            description=description
        )
        
        # Add speech models
        self.add_speech_models()
        
        # Add 3D Voice Command as default preview
        self.show_model_preview(self.translator.t("voice_command_3d"))
    
    def add_speech_models(self):
        """Add speech models to the list."""
        # Speaker Identification
        self.add_model(
            title=self.translator.t("speaker_identification"),
            description=self.translator.t("speaker_identification_desc"),
            icon_path=None
)
        
        # 3D Voice Command
        self.add_model(
            title=self.translator.t("voice_command_3d"),
            description=self.translator.t("voice_command_desc"),
            icon_path=None
)
        

    def show_model_preview(self, model_title):
        """Override the base method to show custom preview content."""
        # Clear existing preview content
        self.clear_preview()
        
        # Set preview title
        self.set_preview_title(model_title)
        
        # Add model-specific content
        if model_title == self.translator.t("voice_command_3d"):
            self.load_3d_voice_command_preview()
        elif model_title == self.translator.t("speaker_identification"):
            self.load_speaker_identification_preview()
        elif model_title == self.translator.t("speech_recognition"):
            self.load_speech_recognition_preview()
        elif model_title == self.translator.t("emotion_detection"):
            self.load_emotion_detection_preview()
        elif model_title == self.translator.t("language_identification"):
            self.load_language_identification_preview()
        else:
            # Fall back to the default preview
            super().show_model_preview(model_title)
    
    def load_3d_voice_command_preview(self):
        """Load 3D voice command model preview with full UI integration"""
        # Add description
        self.add_preview_description(
            self.translator.t("voice_command_full_desc")
        )
        
        # Create main container
        main_container = ctk.CTkFrame(
            self.preview_scroll,
            fg_color=self.theme_manager.get_color("card_bg") if self.theme_manager else "#2D2D2D",
            corner_radius=15
        )
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Add feature highlights
        features_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        features_frame.pack(fill="x", padx=20, pady=10)
        
        features = [
            self.translator.t("voice_feature_1"),
            self.translator.t("voice_feature_2"),
            self.translator.t("voice_feature_3"),
            self.translator.t("voice_feature_4"),
            self.translator.t("voice_feature_5"),
]
        
        for feature in features:
            feature_label = ctk.CTkLabel(
                features_frame,
                text=feature,
                font=ctk.CTkFont(family="Roboto", size=14),
                text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#FFFFFF"
            )
            feature_label.pack(anchor="w", pady=2)
        
        # Add preview image or placeholder
        preview_frame = ctk.CTkFrame(
            main_container,
            fg_color=self.theme_manager.get_color("card_bg") if self.theme_manager else "#2D2D2D",
            corner_radius=8,
            height=200
        )
        preview_frame.pack(fill="x", padx=20, pady=10)
        
        preview_label = ctk.CTkLabel(
            preview_frame,
            text=self.translator.t("launch_voice_command"),
            font=ctk.CTkFont(family="Roboto", size=16, weight="bold"),
            text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#FFFFFF"
        )
        preview_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Add launch button
        button_colors = self.theme_manager.get_ctk_button_colors() if self.theme_manager else {
            "fg_color": "#1976D2", 
            "hover_color": "#0D47A1",
            "text_color": "#FFFFFF"
        }
        
        launch_button = ctk.CTkButton(
            main_container,
            text=self.translator.t("launch_voice_command"),
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            fg_color=button_colors["fg_color"],
            hover_color=button_colors["hover_color"],
            text_color=button_colors["text_color"],
            height=40,
            command=self.launch_3d_interface
        )
        launch_button.pack(pady=20)
        
        # Add requirements info
        requirements_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        requirements_frame.pack(fill="x", padx=20, pady=10)
        
        requirements_label = ctk.CTkLabel(
            requirements_frame,
            text=self.translator.t("dependencies"),
            font=ctk.CTkFont(family="Roboto", size=14, weight="bold"),
            text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#FFFFFF"
        )
        requirements_label.pack(anchor="w")
        
        dependencies = [
            self.translator.t("dep_panda3d"),
            self.translator.t("dep_sounddevice"),
            self.translator.t("dep_librosa"),
            self.translator.t("dep_tensorflow"),
            self.translator.t("dep_numpy"),
        ]
        
        for dep in dependencies:
            dep_label = ctk.CTkLabel(
                requirements_frame,
                text=dep,
                font=ctk.CTkFont(family="Roboto", size=12),
                text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#EEEEEE"
            )
            dep_label.pack(anchor="w", pady=1)
    
    def launch_3d_interface(self):
        """Launch the full 3D Voice Command interface"""
        try:
            # Get the path to the 3d_model_control.py file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up two levels to reach the EdvanceAI root directory
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            model_control_path = os.path.join(root_dir, "tool_gui/3d_speech_to_text/3d_model_control.py")
            
            if not os.path.exists(model_control_path):
                # Try alternative path (directly in workspace root)
                model_control_path = os.path.join(os.getcwd(), "tool_gui/3d_speech_to_text/3d_model_control.py")
                
                if not os.path.exists(model_control_path):
                    raise FileNotFoundError(
                        "3D model control interface file not found. "
                        "Please ensure 3d_model_control.py is in the workspace root directory."
                    )
            
            # Launch the interface in a new process
            subprocess.Popen([sys.executable, model_control_path])
            
            # Show success message
            self.show_message(self.translator.t("launching_voice_command"))
            
        except Exception as e:
            self.show_error(self.translator.t("error_launch"))
            # Add more detailed error logging
            print(f"Error details: {str(e)}")
            print(f"Current directory: {os.getcwd()}")
            print(f"Attempted path: {model_control_path}")
    
    def show_message(self, message):
        """Show a temporary message in the preview area"""
        message_label = ctk.CTkLabel(
            self.preview_scroll,
            text=message,
            font=ctk.CTkFont(family="Roboto", size=14),
            text_color="#4CAF50"
        )
        message_label.pack(pady=10)
        
        # Remove message after 3 seconds
        self.after(3000, message_label.destroy)
    
    def show_error(self, message):
        """Show an error message in the preview area"""
        error_label = ctk.CTkLabel(
            self.preview_scroll,
            text=message,
            font=ctk.CTkFont(family="Roboto", size=14),
            text_color="#FF3B30"
        )
        error_label.pack(pady=10)
        
        # Remove error message after 5 seconds
        self.after(5000, error_label.destroy)
    
    # Placeholder methods for other model previews
    def load_speaker_identification_preview(self):
        """Create preview content for Speaker Identification."""
        # Description
        description = self.translator.t("speaker_full_desc")
        
        desc_label = ctk.CTkLabel(
            self.preview_scroll,
            text=description,
            wraplength=600,
            justify="left",
            font=ctk.CTkFont(size=14)
        )
        desc_label.pack(pady=20)
        
        # Feature highlights
        features_frame = ctk.CTkFrame(self.preview_scroll, fg_color="transparent")
        features_frame.pack(fill="x", padx=20, pady=10)
        
        features = [
            self.translator.t("speaker_feature_1"),
            self.translator.t("speaker_feature_2"),
            self.translator.t("speaker_feature_3"),
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
            self.preview_scroll,
            text=self.translator.t("launch_speaker"),
            command=self.launch_speaker_identification_interface,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        launch_button.pack(pady=20)

    def launch_speaker_identification_interface(self):
        """Launch the Speaker Identification interface."""
        try:
            # Get the path to the speaker_main_gui.py file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up two levels to reach the EdvanceAI root directory
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            model_path = os.path.join(root_dir, "tool_gui/speaker_identification/speaker_main_gui.py")
            
            if not os.path.exists(model_path):
                # Try alternative path (directly in workspace root)
                model_path = os.path.join(os.getcwd(), "tool_gui/speaker_identification/speaker_main_gui.py")
                
                if not os.path.exists(model_path):
                    raise FileNotFoundError(
                        "Speaker identification interface file not found. "
                        "Please ensure speaker_main_gui.py is in the workspace root directory."
                    )
            
            # Launch the interface in a new process
            subprocess.Popen([sys.executable, model_path])
            
            # Show success message
            self.show_message(self.translator.t("launching_speaker"))
            
        except Exception as e:
            self.show_error(self.translator.t("error_launch"))
            # Add more detailed error logging
            print(f"Error details: {str(e)}")
            print(f"Current directory: {os.getcwd()}")
            print(f"Attempted path: {model_path}")
        
    def load_speech_recognition_preview(self):
        self.add_preview_description(
            self.translator.t("speech_recognition_desc")
        )
        
    def load_emotion_detection_preview(self):
        self.add_preview_description(
            self.translator.t("emotion_detection_desc")
        )
        
    def load_language_identification_preview(self):
        self.add_preview_description(
            self.translator.t("language_identification_desc")
        ) 