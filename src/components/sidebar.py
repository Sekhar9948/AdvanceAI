
import customtkinter as ctk
from ..utils.responsive_utils import get_font_size

class DummyTranslator:
    def t(self, key):
        return key


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, app_width, app_height, show_screen_callback, toggle_theme_callback,translator=None):
        # Initialize with theme-specific colors
        
        super().__init__(
            parent, 
            corner_radius=0,
            fg_color="#121212",  # Will be updated with theme
            width=250,
            height=app_height
        )
        if translator is None:
            self.translator = DummyTranslator()
        else:
            self.translator = translator
        
        self.app_width = app_width
        self.app_height = app_height
        self.show_screen = show_screen_callback
        self.toggle_theme = toggle_theme_callback
        self.active_item = "dashboard"
        
        # Configure column and row
        self.grid_rowconfigure(20, weight=1)  # Flexible space before theme toggle
        self.grid_columnconfigure(0, weight=1)
        
        # Create widgets
        self.create_logo()
        
        # Create scrollable frame for nav items
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self, 
            corner_radius=0,
            fg_color="transparent",
            scrollbar_fg_color="transparent",
            scrollbar_button_color="#555555",
            scrollbar_button_hover_color="#777777"
        )
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=(10, 10))
        self.grid_rowconfigure(1, weight=1)  # Make scrollable frame expand
        
        # Create nav items within scrollable frame
        self.create_nav_items()
        
        # Create theme toggle at the bottom (outside scrollable frame)
        self.create_theme_toggle()
    
    def create_logo(self):
        """Create logo at the top of the sidebar."""
        # Logo container
        self.logo_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.logo_frame.grid(row=0, column=0, sticky="ew", pady=(20, 10))
        
        # Logo label
        self.logo_label = ctk.CTkLabel(
            self.logo_frame, 
            text=self.translator.t("app_name"),
            font=ctk.CTkFont(family="Roboto", size=get_font_size(24), weight="bold"),
            text_color="#FFFFFF"
        )
        self.logo_label.pack(pady=5)
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.logo_frame, 
            text=self.translator.t("app_subtitle"),
            font=ctk.CTkFont(family="Roboto", size=get_font_size(12)),
            text_color="#AAAAAA"
        )
        self.subtitle_label.pack()
    
    def create_nav_items(self):
        """Create navigation items."""
        # Navigation section title
        self.nav_title = ctk.CTkLabel(
            self.scrollable_frame, 
            text=self.translator.t("NAVIGATION"),
            font=ctk.CTkFont(family="Roboto", size=get_font_size(12), weight="bold"),
            text_color="#777777",
            anchor="w"
        )
        self.nav_title.pack(anchor="w", padx=10, pady=(5, 10))
        
        # Navigation buttons with their corresponding screens
        self.nav_items = [
            {"name": "dashboard", "text": self.translator.t("dashboard")},
            {"name": "section_title_1", "text": self.translator.t("model_categories"), "type": "section"},
            {"name": "vision_models", "text": self.translator.t("vision_models")},
            {"name": "speech_models", "text": self.translator.t("speech_models")},
            {"name": "text_models", "text": self.translator.t("text_models")},
            {"name": "section_title_2", "text": self.translator.t("utilities"), "type": "section"},
            {"name": "settings", "text": self.translator.t("settings")},
            {"name": "section_title_3", "text": self.translator.t("additional"), "type": "section"},
            {"name": "help", "text": self.translator.t("help")},
            {"name": "about", "text": self.translator.t("about")},
            {"name": "feedback", "text": self.translator.t("feedback")}
]
        
        # Create each navigation item
        for item in self.nav_items:
            if item.get("type") == "section":
                # Section header
                section_label = ctk.CTkLabel(
                    self.scrollable_frame, 
                    text=item["text"],
                    font=ctk.CTkFont(family="Roboto", size=get_font_size(12), weight="bold"),
                    text_color="#777777",
                    anchor="w"
                )
                section_label.pack(anchor="w", padx=20, pady=(15, 8), fill="x")
                item["section_label"] = section_label
            else:
                # Navigation button
                button_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
                button_frame.pack(fill="x", padx=10, pady=2)
                
                # Create indicator for active item
                indicator = ctk.CTkFrame(
                    button_frame, 
                    width=4, 
                    corner_radius=2,
                    fg_color="#1E88E5" if item["name"] == self.active_item else "transparent"
                )
                indicator.pack(side="left", fill="y", padx=(0, 5))
                
                # Button
                button = ctk.CTkButton(
                    button_frame,
                    text=item["text"],
                    font=ctk.CTkFont(family="Roboto", size=get_font_size(14)),
                    fg_color="transparent",
                    text_color="#FFFFFF",
                    hover_color="#1E88E5" if item["name"] == self.active_item else "#333333",
                    anchor="w",
                    height=10,
                    corner_radius=8,
                    command=lambda name=item["name"]: self.handle_nav_click(name)
                )
                
                # Highlight active item
                if item["name"] == self.active_item:
                    button.configure(fg_color="#2D2D2D")
                
                button.pack(fill="x", expand=True)
                
                # Store references for later updates
                item["button"] = button
                item["indicator"] = indicator
    
    def create_theme_toggle(self):
        """Create theme toggle button at the bottom of the sidebar."""
        self.theme_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        self.theme_frame.grid(row=21, column=0, sticky="ew", padx=10, pady=10)
        
        self.theme_button = ctk.CTkButton(
            self.theme_frame,
            text=self.translator.t("toggle_theme"),
            font=ctk.CTkFont(family="Roboto", size=get_font_size(14)),
            fg_color="#333333",
            text_color="#FFFFFF",
            hover_color="#444444",
            height=40,
            corner_radius=8,
            command=self.toggle_theme
        )
        self.theme_button.pack(fill="x", pady=10)
    
    def handle_nav_click(self, name):
        """Handle navigation item click."""
        # Skip if already active or if item is a section header
        if name == self.active_item or any(item.get("name") == name and item.get("type") == "section" for item in self.nav_items):
            return
        
        # Update active item
        self.set_active(name)
        
        # Show the corresponding screen
        self.show_screen(name)
    
    def set_active(self, name):
        """Set the active navigation item."""
        # Update active item
        self.active_item = name
        
        # Update button styles
        for item in self.nav_items:
            if "button" in item and "indicator" in item:
                if item["name"] == name:
                    item["button"].configure(
                        fg_color="#2D2D2D",
                        hover_color="#1E88E5"
                    )
                    item["indicator"].configure(fg_color="#1E88E5")
                else:
                    item["button"].configure(
                        fg_color="transparent",
                        hover_color="#333333"
                    )
                    item["indicator"].configure(fg_color="transparent")
    
    def update_theme(self, theme):
        """Update sidebar colors based on theme."""
        # Update sidebar background color
        bg_color = "#121212" if theme == "dark" else "#E0E0E0"
        self.configure(fg_color=bg_color)
        self.scrollable_frame.configure(fg_color="transparent")
        
        # Update scrollbar colors
        scrollbar_color = "#555555" if theme == "dark" else "#BBBBBB"
        scrollbar_hover = "#777777" if theme == "dark" else "#999999"
        self.scrollable_frame.configure(
            scrollbar_button_color=scrollbar_color,
            scrollbar_button_hover_color=scrollbar_hover
        )
        
        # Update text colors
        text_color = "#FFFFFF" if theme == "dark" else "#212121"
        faded_text_color = "#777777" if theme == "dark" else "#757575"
        subtitle_color = "#AAAAAA" if theme == "dark" else "#616161"
        active_color = "#1E88E5" if theme == "dark" else "#1976D2"
        
        # Update logo text
        self.logo_label.configure(text_color=text_color)
        self.subtitle_label.configure(text_color=subtitle_color)
        
        # Update section headers
        self.nav_title.configure(text_color=faded_text_color)
        for item in self.nav_items:
            if item.get("type") == "section" and "section_label" in item:
                item["section_label"].configure(text_color=faded_text_color)
            elif "button" in item and "indicator" in item:
                # Update button colors
                if item["name"] == self.active_item:
                    button_bg = "#DDDDDD" if theme == "light" else "#2D2D2D"
                    item["button"].configure(
                        fg_color=button_bg,
                        text_color=text_color,
                        hover_color=active_color
                    )
                    item["indicator"].configure(fg_color=active_color)
                else:
                    item["button"].configure(
                        text_color=text_color,
                        hover_color="#E0E0E0" if theme == "light" else "#333333"
                    )
        
        # Update theme toggle button
        self.theme_button.configure(
            fg_color="#BDBDBD" if theme == "light" else "#333333",
            text_color=text_color
        )