
import darkdetect
from PySide6.QtGui import QColor

class ThemeManager:
    def __init__(self):
        # Auto-detect system theme initially, default to dark if detection fails
        self.current_theme = darkdetect.theme().lower() if darkdetect.theme() else "dark"
        
        # Define theme colors
        self.themes = {
            "dark": {
                # CustomTkinter colors
                "bg_color": "#1E1E1E",
                "fg_color": "#FFFFFF",
                "primary_color": "#1E88E5",
                "secondary_color": "#0D47A1",
                "success_color": "#43A047",
                "warning_color": "#FB8C00",
                "danger_color": "#E53935",
                "card_bg": "#2D2D2D",
                "sidebar_bg": "#121212",
                "header_bg": "#252525",
                "hover_color": "#373737",
                "border_color": "#424242",
                "chart_colors": ["#1E88E5", "#43A047", "#FB8C00", "#E53935", "#8E24AA", "#00ACC1", "#FFB300"],
                
                # PySide6 colors
                "qt_window": QColor(33, 33, 33),
                "qt_window_text": QColor(255, 255, 255),
                "qt_base": QColor(25, 25, 25),
                "qt_text": QColor(255, 255, 255),
                "qt_button": QColor(53, 53, 53),
                "qt_button_text": QColor(255, 255, 255),
                "qt_highlight": QColor(42, 130, 218),
            },
            "light": {
                # CustomTkinter colors
                "bg_color": "#F5F5F5",
                "fg_color": "#212121",
                "primary_color": "#1976D2",
                "secondary_color": "#0D47A1", 
                "success_color": "#388E3C",
                "warning_color": "#F57C00",
                "danger_color": "#D32F2F",
                "card_bg": "#FFFFFF",
                "sidebar_bg": "#E0E0E0",
                "header_bg": "#EEEEEE",
                "hover_color": "#E0E0E0",
                "border_color": "#BDBDBD",
                "chart_colors": ["#1976D2", "#388E3C", "#F57C00", "#D32F2F", "#7B1FA2", "#0097A7", "#FFA000"],
                
                # PySide6 colors
                "qt_window": QColor(240, 240, 240),
                "qt_window_text": QColor(0, 0, 0),
                "qt_base": QColor(255, 255, 255),
                "qt_text": QColor(0, 0, 0),
                "qt_button": QColor(240, 240, 240),
                "qt_button_text": QColor(0, 0, 0),
                "qt_highlight": QColor(0, 120, 215),
            }
        }
        
        # Set the initial theme
        self.set_theme(self.current_theme)
    
    def set_theme(self, theme):
        """Set the current theme."""
        if theme in self.themes:
            self.current_theme = theme
            
    def get_color(self, color_name):
        """Get a color from the current theme."""
        if color_name in self.themes[self.current_theme]:
            return self.themes[self.current_theme][color_name]
        return None
        
    def get_qt_color(self, color_name):
        """Get a PySide6 color from the current theme."""
        qt_color_name = f"qt_{color_name}"
        if qt_color_name in self.themes[self.current_theme]:
            return self.themes[self.current_theme][qt_color_name]
        return None
    
    def get_ctk_button_colors(self):
        """Get CustomTkinter button colors for the current theme."""
        theme = self.themes[self.current_theme]
        return {
            "fg_color": theme["primary_color"],
            "hover_color": theme["secondary_color"],
            "text_color": "#FFFFFF" if self.current_theme == "dark" else "#FFFFFF",
            "border_color": theme["border_color"]
        }
    
    def get_ctk_frame_colors(self):
        """Get CustomTkinter frame colors for the current theme."""
        theme = self.themes[self.current_theme]
        return {
            "fg_color": theme["card_bg"],
            "border_color": theme["border_color"]
        }
    
    def get_ctk_text_colors(self):
        """Get CustomTkinter text colors for the current theme."""
        theme = self.themes[self.current_theme]
        return {
            "text_color": theme["fg_color"],
            "placeholder_text_color": "#9E9E9E"
        } 