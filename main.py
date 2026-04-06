
#!/usr/bin/env python3
import os
import sys
import platform
import customtkinter as ctk
from PIL import Image, ImageTk
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPalette, QIcon, QFont

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import app modules
from src.themes.theme_manager import ThemeManager
from src.components.sidebar import Sidebar
from src.components.header import Header
from src.screens.dashboard import Dashboard
from src.screens.vision_models import VisionModelsScreen
from src.screens.speech_models import SpeechModelsScreen
from src.screens.text_models import TextModelsScreen
from src.utils.responsive_utils import get_screen_metrics
from src.translator import Translator

class EdvanceApp:
    def __init__(self):
        self.translator = Translator("en")
        # Set appearance mode and theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create PySide6 App
        self.qt_app = QApplication(sys.argv)
        self.qt_app.setStyle("Fusion")
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        self.apply_theme("dark")
        
        # Create main CustomTkinter window
        self.root = ctk.CTk()
        self.root.title("AdvanceAI - AI Education Tool")
        
        # Set window dimensions based on screen size
        screen_width, screen_height = get_screen_metrics()
        self.width = min(1280, int(screen_width * 0.85))
        self.height = min(800, int(screen_height * 0.85))
        self.root.geometry(f"{self.width}x{self.height}")
        
        # Set minimum window size
        self.root.minsize(800, 600)
        
        # Create icon directory if it doesn't exist
        icon_dir = os.path.join(os.path.dirname(__file__), 'assets', 'icons')
        os.makedirs(icon_dir, exist_ok=True)
        
        # Configure main layout
        self.setup_layout()
        
        # Initialize screens
        self.initialize_screens()
        
        # Show dashboard initially
        self.show_screen("dashboard")
        
    def setup_layout(self):
    # Main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True)

    # Sidebar
        self.sidebar = Sidebar(
            self.main_frame,
            self.width,
            self.height,
            self.show_screen,
            self.toggle_theme,
            self.translator
        )
        self.sidebar.pack(side="left", fill="y")

    # ✅ CREATE FIRST
        self.content_area = ctk.CTkFrame(self.main_frame, corner_radius=0)

    # ✅ THEN PACK
        self.content_area.pack(side="right", fill="both", expand=True)

    # Header
        self.header = Header(
            self.content_area,
            self.width,
            self.toggle_theme,
            current_theme=self.theme_manager.current_theme,
            translator=self.translator,
            change_language_callback=self.change_language
        )
        self.header.pack(side="top", fill="x")

    # Content frame
        self.content_frame = ctk.CTkFrame(self.content_area, corner_radius=0)
        self.content_frame.pack(side="bottom", fill="both", expand=True, padx=20, pady=20)
        
    def initialize_screens(self):
        self.screens = {}
        
        # Create dashboard
        self.screens["dashboard"] = Dashboard(
            self.content_frame, 
            self.theme_manager,
            self.translator
        )
        
        # Create model category screens
        self.screens["vision_models"] = VisionModelsScreen(
            self.content_frame, 
            self.theme_manager,
            self.translator
        )
        
        self.screens["speech_models"] = SpeechModelsScreen(
            self.content_frame, 
            self.theme_manager,
            self.translator
        )
        
        self.screens["text_models"] = TextModelsScreen(
            self.content_frame, 
            self.theme_manager,
            self.translator
        )

        
        # Hide all screens initially
        for screen in self.screens.values():
            screen.pack_forget()
    
    def show_screen(self, screen_name):
        # Hide all screens
        for screen in self.screens.values():
            screen.pack_forget()
            
        # Show the selected screen
        if screen_name in self.screens:
            self.screens[screen_name].pack(fill="both", expand=True)
            self.sidebar.set_active(screen_name)
            
    def toggle_theme(self):
        # Toggle between light and dark theme
        new_theme = "light" if self.theme_manager.current_theme == "dark" else "dark"
        self.apply_theme(new_theme)
        
        # Update UI elements
        self.header.update_theme(new_theme)
        self.sidebar.update_theme(new_theme)
        
        # Update all screens
        for screen in self.screens.values():
            screen.update_theme(new_theme)
    
    def apply_theme(self, theme):
        # Set theme
        self.theme_manager.set_theme(theme)
        
        # Apply to CustomTkinter
        ctk.set_appearance_mode(theme)
        
        # Apply to PySide6
        palette = QPalette()
        if theme == "dark":
            palette.setColor(QPalette.ColorRole.Window, QColor(33, 33, 33))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        else:
            palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(233, 233, 233))
            palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.Link, QColor(0, 102, 204))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        self.qt_app.setPalette(palette)
    
    def run(self):
        self.root.mainloop()

    

    def change_language(self, lang):
        self.translator.load_language(lang)

    # 🔥 FULL RESET (BEST FIX)
        for widget in self.root.winfo_children():
            widget.destroy()

        self.setup_layout()
        self.initialize_screens()
        self.show_screen("dashboard")
if __name__ == "__main__":
    app = EdvanceApp()
    app.run() 