
import customtkinter as ctk
from ..utils.responsive_utils import get_font_size

class Header(ctk.CTkFrame):
    def __init__(self, parent, app_width, toggle_theme_callback, current_theme="dark",translator=None, change_language_callback=None):
        # Initialize with theme-specific colors
        self.change_language_callback = change_language_callback
        from src.translator import Translator

        

    # ✅ Safe translator
        if translator is None:
            self.translator = Translator("en")
        else:
            self.translator = translator

        

        super().__init__(
            parent, 
            corner_radius=0,
            fg_color="#252525",  # Will be updated with theme
            height=70
        )
        
        self.app_width = app_width
        self.toggle_theme = toggle_theme_callback
        self.current_theme = current_theme
        
        # Configure layout
        self.grid_columnconfigure(0, weight=1)  # Title
        self.grid_columnconfigure(1, weight=0)  # Search
        self.grid_columnconfigure(2, weight=0)  # Theme toggle
        self.grid_columnconfigure(3, weight=0)  # User info
        self.grid_columnconfigure(4, weight=0)
        
        # Create header elements
        self.create_title()
        self.create_search_bar()
        self.create_theme_switch()
        self.create_user_info()

        self.lang_menu = ctk.CTkOptionMenu(
            self,
            values=["English", "Hindi", "Telugu", "Kannada"],
            command=self.change_language_ui,
            width=140
        )
        self.lang_menu.grid(row=0, column=4, padx=10)

        current_lang = self.translator.lang

        reverse_map = {
            "en": "English",
            "hi": "Hindi",
            "te": "Telugu",
            "kn": "Kannada"
        }

        self.lang_menu.set(reverse_map.get(current_lang, "English"))
        

# ✅ CALL INSIDE INIT (IMPORTANT)
        

    def change_language_ui(self, choice):
        lang_map = {
            "English": "en",
            "Hindi": "hi",
            "Telugu": "te",
            "Kannada": "kn"
        }

        lang_code = lang_map.get(choice, "en")

        if self.change_language_callback:
            self.change_language_callback(lang_code)
    
    def create_title(self):
        """Create page title in header."""
        # Title frame for better alignment
        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=0)
        
        # EdvanceAI logo text
        self.logo_text = ctk.CTkLabel(
            self.title_frame, 
            text=self.translator.t("app_name"),
            font=ctk.CTkFont(family="Roboto", size=get_font_size(18), weight="bold"),
            text_color="#FFFFFF"
        )
        self.logo_text.pack(side="left", padx=(0, 5))
        
        # Separator
        self.separator = ctk.CTkFrame(
            self.title_frame,
            width=1,
            height=30,
            fg_color="#444444"
        )
        self.separator.pack(side="left", padx=10)
        
        # Title label
        self.title_label = ctk.CTkLabel(
            self.title_frame, 
            text=self.translator.t("app_subtitle"),
            font=ctk.CTkFont(family="Roboto", size=get_font_size(16)),
            text_color="#AAAAAA"
        )
        self.title_label.pack(side="left", padx=5)
    
    def create_search_bar(self):
        """Create search bar in header."""
        self.search_frame = ctk.CTkFrame(
            self, 
            fg_color="#333333",
            corner_radius=8,
            border_width=1,
            border_color="#444444",
            height=38,
            width=250
        )
        self.search_frame.grid(row=0, column=1, sticky="e", padx=(0, 20), pady=0)
        
        # Make sure frame maintains its size
        self.search_frame.grid_propagate(False)
        
        # Search icon placeholder
        search_icon = ctk.CTkLabel(
            self.search_frame,
            text="🔍",
            font=ctk.CTkFont(size=get_font_size(14)),
            text_color="#777777",
            width=20
        )
        search_icon.pack(side="left", padx=(10, 0))
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text=self.translator.t("search_placeholder"),
            font=ctk.CTkFont(family="Roboto", size=get_font_size(13)),
            fg_color="transparent",
            border_width=0,
            text_color="#FFFFFF"
        )
        self.search_entry.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    
    def create_theme_switch(self):
        """Create theme switch toggle."""
        self.theme_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.theme_frame.grid(row=0, column=2, sticky="e", padx=10, pady=0)
        
        # Theme mode icon
        self.mode_icon = ctk.CTkLabel(
            self.theme_frame,
            text="🌙" if self.current_theme == "dark" else "☀️",
            font=ctk.CTkFont(size=get_font_size(16)),
            text_color="#AAAAAA"
        )
        self.mode_icon.pack(side="left", padx=(0, 5))
        
        # Switch
        self.switch_var = ctk.StringVar(value="on" if self.current_theme == "dark" else "off")
        self.theme_switch = ctk.CTkSwitch(
            self.theme_frame,
            text="",
            variable=self.switch_var,
            onvalue="on",
            offvalue="off",
            command=self.handle_theme_toggle,
            switch_height=22,
            switch_width=44,
            progress_color="#1E88E5"
        )
        self.theme_switch.pack(side="left")
    
    def create_user_info(self):
        """Create user info section."""
        self.user_frame = ctk.CTkFrame(
            self, 
            fg_color="#333333", 
            corner_radius=20,
            width=40,
            height=40
        )
        self.user_frame.grid(row=0, column=3, sticky="e", padx=20, pady=0)
        
        # Make sure frame maintains its size
        self.user_frame.grid_propagate(False)
        
        # User initial/avatar
        self.user_initial = ctk.CTkLabel(
            self.user_frame,
            text="S",
            font=ctk.CTkFont(family="Roboto", size=get_font_size(14), weight="bold"),
            text_color="#FFFFFF"
        )
        self.user_initial.place(relx=0.5, rely=0.5, anchor="center")
    
    def handle_theme_toggle(self):
        """Handle theme switch toggle."""
        # Update theme mode icon
        if self.switch_var.get() == "on":
            self.mode_icon.configure(text="🌙")  # Moon icon
            self.current_theme = "dark"
        else:
            self.mode_icon.configure(text="☀️")  # Sun icon
            self.current_theme = "light"
        
        # Call the theme toggle callback
        self.toggle_theme()
    
    def update_theme(self, theme):
        """Update header colors based on theme."""
        # Update header background color
        bg_color = "#252525" if theme == "dark" else "#EEEEEE"
        self.configure(fg_color=bg_color)
        
        # Update text colors
        text_color = "#FFFFFF" if theme == "dark" else "#212121"
        secondary_text_color = "#AAAAAA" if theme == "dark" else "#757575"
        
        # Update logo and title text
        self.logo_text.configure(text_color=text_color)
        self.title_label.configure(text_color=secondary_text_color)
        
        # Update separator color
        separator_color = "#444444" if theme == "dark" else "#DDDDDD"
        self.separator.configure(fg_color=separator_color)
        
        # Update search bar
        search_bg = "#333333" if theme == "dark" else "#F5F5F5"
        search_border = "#444444" if theme == "dark" else "#E0E0E0"
        self.search_frame.configure(fg_color=search_bg, border_color=search_border)
        self.search_entry.configure(
            text_color=text_color,
            placeholder_text_color=secondary_text_color
        )
        
        # Update user frame
        user_bg = "#333333" if theme == "dark" else "#1976D2"
        self.user_frame.configure(fg_color=user_bg)
        
        # Update mode icon
        self.mode_icon.configure(
            text="🌙" if theme == "dark" else "☀️",
            text_color=secondary_text_color
        )
        
        # Update switch state without triggering callback
        self.switch_var.set("on" if theme == "dark" else "off")
        
        # Update current theme
        self.current_theme = theme 