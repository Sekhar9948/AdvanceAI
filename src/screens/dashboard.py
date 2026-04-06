
import customtkinter as ctk
from src.translator import Translator
from ..utils.responsive_utils import get_font_size

class ModelCard(ctk.CTkFrame):
    """A card representing a model category."""
    
    
    def __init__(self, parent, title, description, icon_path=None, category="vision_models", theme_manager=None, command=None,translator=None):
        # Get colors from theme manager
        self.translator = translator if translator else Translator("en")
        self.t = self.translator.t
        card_colors = theme_manager.get_ctk_frame_colors() if theme_manager else {"fg_color": "#2D2D2D", "border_color": "#424242"}
        button_colors = theme_manager.get_ctk_button_colors() if theme_manager else {"fg_color": "#1E88E5", "hover_color": "#0D47A1"}
        
        # Initialize with theme-specific colors
        super().__init__(
            parent,
            corner_radius=12,
            fg_color=card_colors["fg_color"],
            border_width=1,
            border_color=card_colors["border_color"]
        )
        
        self.title = title
        self.description = description
        self.icon_path = icon_path
        self.category = category
        self.theme_manager = theme_manager
        self.command = command
        
        # Create card content
        self.create_content()
    
    def create_content(self):
        """Create card content."""
        # Create gradient overlay at the top
        accent_color = self.theme_manager.get_color("primary_color") if self.theme_manager else "#1E88E5"
        self.accent_bar = ctk.CTkFrame(
            self, 
            corner_radius=6,
            fg_color=accent_color,
            height=6,
            width=80
        )
        self.accent_bar.place(x=15, y=15)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text=self.title,
            font=ctk.CTkFont(family="Roboto", size=get_font_size(18), weight="bold"),
            text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#FFFFFF"
        )
        self.title_label.pack(anchor="w", padx=15, pady=(30, 5))
        
        # Description
        self.desc_label = ctk.CTkLabel(
            self,
            text=self.description,
            font=ctk.CTkFont(family="Roboto", size=get_font_size(12)),
            text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#DDDDDD",
            wraplength=300,
            justify="left"
        )
        self.desc_label.pack(anchor="w", padx=15, pady=(0, 20), fill="x")
        
        # Explore button
        button_colors = self.theme_manager.get_ctk_button_colors() if self.theme_manager else {
            "fg_color": "#1E88E5", 
            "hover_color": "#0D47A1",
            "text_color": "#FFFFFF",
            "border_color": "#424242"
        }
        
        # Button frame for bottom alignment
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(side="bottom", fill="x", padx=15, pady=15)
        
        # Icon placeholder on the left side
        model_count = {"vision_models": 4, "speech_models": 2, "text_models": 3}
        count_text = f"{model_count.get(self.category, 0)} {self.translator.t('models')}"
        
        self.count_label = ctk.CTkLabel(
            self.btn_frame,
            text=count_text,
            font=ctk.CTkFont(family="Roboto", size=get_font_size(11)),
            text_color="#AAAAAA" if self.theme_manager.current_theme == "dark" else "#777777"
        )
        self.count_label.pack(side="left")
        
        self.explore_button = ctk.CTkButton(
            self.btn_frame,
            text=self.translator.t("explore"),
            font=ctk.CTkFont(family="Roboto", size=get_font_size(12), weight="bold"),
            fg_color=button_colors["fg_color"],
            hover_color=button_colors["hover_color"],
            text_color=button_colors["text_color"],
            corner_radius=8,
            height=32,
            width=100,
            command=self.handle_explore
        )
        self.explore_button.pack(side="right")
    
    def handle_explore(self):
        """Handle explore button click."""
        if self.command:
            self.command(self.category)
    
    def update_theme(self, theme):
        """Update card colors based on theme."""
        if not self.theme_manager:
            return
            
        # Update frame colors
        card_colors = self.theme_manager.get_ctk_frame_colors()
        self.configure(
            fg_color=card_colors["fg_color"],
            border_color=card_colors["border_color"]
        )
        
        # Update accent bar
        accent_color = self.theme_manager.get_color("primary_color")
        self.accent_bar.configure(fg_color=accent_color)
        
        # Update text colors
        text_color = self.theme_manager.get_color("fg_color")
        self.title_label.configure(text_color=text_color)
        self.desc_label.configure(text_color=text_color)
        
        # Update count label
        self.count_label.configure(
            text_color="#AAAAAA" if theme == "dark" else "#777777"
        )
        
        # Update button colors
        button_colors = self.theme_manager.get_ctk_button_colors()
        self.explore_button.configure(
            fg_color=button_colors["fg_color"],
            hover_color=button_colors["hover_color"],
            text_color=button_colors["text_color"]
        )

class Dashboard(ctk.CTkFrame):
    def __init__(self, parent, theme_manager=None, translator=None):
        self.translator = translator 
        # Initialize with theme-specific colors
        bg_color = theme_manager.get_color("bg_color") if theme_manager else "#1E1E1E"
        
        super().__init__(
            parent,
            corner_radius=0,
            fg_color=bg_color
        )
        
        self.parent = parent
        self.theme_manager = theme_manager
        
        # Create scrollable main frame
        self.main_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_fg_color="transparent",
            scrollbar_button_color="#555555" if theme_manager.current_theme == "dark" else "#BBBBBB", 
            scrollbar_button_hover_color="#777777" if theme_manager.current_theme == "dark" else "#999999"
        )
        self.main_scroll.pack(fill="both", expand=True)
        
        # Create content
        self.create_welcome_section()
        self.create_quick_stats()
        self.create_model_categories()
    
    def create_welcome_section(self):
        """Create welcome section."""
        # Welcome frame
        self.welcome_frame = ctk.CTkFrame(
            self.main_scroll,
            corner_radius=14,
            fg_color=self.theme_manager.get_color("card_bg") if self.theme_manager else "#2D2D2D",
            border_width=1,
            border_color=self.theme_manager.get_color("border_color") if self.theme_manager else "#424242"
        )
        self.welcome_frame.pack(fill="x", padx=20, pady=20)
        
        # Welcome title
        self.welcome_title = ctk.CTkLabel(
            self.welcome_frame,
            text=self.translator.t("welcome"),
            font=ctk.CTkFont(family="Roboto", size=get_font_size(24), weight="bold"),
            text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#FFFFFF"
        )
        self.welcome_title.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Welcome message
        welcome_text = self.translator.t("welcome_description")
        self.welcome_message = ctk.CTkLabel(
            self.welcome_frame,
            text=welcome_text,
            font=ctk.CTkFont(family="Roboto", size=get_font_size(14)),
            text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#EEEEEE",
            wraplength=800,
            justify="left"
        )
        self.welcome_message.pack(anchor="w", padx=20, pady=(0, 20), fill="x")
        
        # Get started button
        button_colors = self.theme_manager.get_ctk_button_colors() if self.theme_manager else {
            "fg_color": "#1E88E5", 
            "hover_color": "#0D47A1",
            "text_color": "#FFFFFF"
        }
        
        self.start_button = ctk.CTkButton(
            self.welcome_frame,
            text=self.translator.t("get_started"),
            font=ctk.CTkFont(family="Roboto", size=get_font_size(14), weight="bold"),
            fg_color=button_colors["fg_color"],
            hover_color=button_colors["hover_color"],
            text_color=button_colors["text_color"],
            corner_radius=8,
            height=38,
            width=150
        )
        self.start_button.pack(anchor="w", padx=20, pady=(0, 20))
    
    def create_quick_stats(self):
        """Create quick stats row."""
        # Stats container
        self.stats_frame = ctk.CTkFrame(
            self.main_scroll,
            fg_color="transparent"
        )
        self.stats_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Configure grid for stats
        self.stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="stats")
        
        # Create stat cards
        stats = [
            {"title": self.translator.t("ai_models"), "value": "8", "color": "#1E88E5"},
            {"title": self.translator.t("categories"), "value": "4", "color": "#43A047"},
            {"title": self.translator.t("interactive"), "value": "100%", "color": "#FB8C00"},
            {"title": self.translator.t("easy_to_learn"), "value": "✓", "color": "#E53935"}
        ]
        
        for i, stat in enumerate(stats):
            card_bg = self.theme_manager.get_color("card_bg") if self.theme_manager else "#2D2D2D"
            
            stat_card = ctk.CTkFrame(
                self.stats_frame,
                corner_radius=10,
                fg_color=card_bg,
                border_width=1,
                border_color=self.theme_manager.get_color("border_color") if self.theme_manager else "#424242"
            )
            stat_card.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
            
            # Add colored indicator
            indicator = ctk.CTkFrame(
                stat_card,
                corner_radius=2,
                fg_color=stat["color"],
                width=30,
                height=4
            )
            indicator.pack(anchor="w", padx=12, pady=(12, 0))
            
            # Value
            value_label = ctk.CTkLabel(
                stat_card,
                text=stat["value"],
                font=ctk.CTkFont(family="Roboto", size=get_font_size(24), weight="bold"),
                text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#FFFFFF"
            )
            value_label.pack(anchor="w", padx=12, pady=(8, 2))
            
            # Title
            title_label = ctk.CTkLabel(
                stat_card,
                text=stat["title"],
                font=ctk.CTkFont(family="Roboto", size=get_font_size(12)),
                text_color="#AAAAAA" if self.theme_manager.current_theme == "dark" else "#777777"
            )
            title_label.pack(anchor="w", padx=12, pady=(0, 12))
            
            # Store references for theme updates
            stat["card"] = stat_card
            stat["value_label"] = value_label
            stat["title_label"] = title_label
            stat["indicator"] = indicator
            
        self.stats = stats
    
    def create_model_categories(self):
        """Create model category cards."""
        # Category section title
        self.category_title = ctk.CTkLabel(
            self.main_scroll,
            text=self.translator.t("model_categories"),
            font=ctk.CTkFont(family="Roboto", size=get_font_size(20), weight="bold"),
            text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#FFFFFF"
        )
        self.category_title.pack(anchor="w", padx=20, pady=(10, 15))
        
        # Create a grid layout for categories
        self.categories_frame = ctk.CTkFrame(
            self.main_scroll,
            fg_color="transparent"
        )
        self.categories_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Configure grid - 2 columns, responsive
        self.categories_frame.grid_columnconfigure((0, 1), weight=1, uniform="categories")
        
        # Vision Models card
        self.vision_card = ModelCard(
            self.categories_frame,
            title=self.translator.t("vision_models"),
            description=self.translator.t("vision_description"),
            category="vision_models",
            theme_manager=self.theme_manager,
            command=self.show_model_category,
            translator=self.translator   
        )
        self.vision_card.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Speech Models card
        self.speech_card = ModelCard(
            self.categories_frame,
            title=self.translator.t("speech_models"),
            description=self.translator.t("speech_description"),
            category="speech_models",
            theme_manager=self.theme_manager,
            command=self.show_model_category,
            translator=self.translator   # ✅ ADD THIS
        )
        self.speech_card.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Text Models card
        self.text_card = ModelCard(
            self.categories_frame,
            title=self.translator.t("text_models"),
            description=self.translator.t("text_description"),
            category="text_models",
            theme_manager=self.theme_manager,
            command=self.show_model_category,
            translator=self.translator   # ✅ ADD THIS
        )
        self.text_card.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        
        # Footer section
        self.create_footer()
    
    def create_footer(self):
        """Create footer section with additional info."""
        # Footer frame
        self.footer_frame = ctk.CTkFrame(
            self.main_scroll,
            corner_radius=14,
            fg_color=self.theme_manager.get_color("card_bg") if self.theme_manager else "#2D2D2D",
            border_width=1,
            border_color=self.theme_manager.get_color("border_color") if self.theme_manager else "#424242"
        )
        self.footer_frame.pack(fill="x", padx=20, pady=(20, 20))
        
        # Footer title
        self.footer_title = ctk.CTkLabel(
            self.footer_frame,
            text=self.translator.t("about"),
            font=ctk.CTkFont(family="Roboto", size=get_font_size(16), weight="bold"),
            text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#FFFFFF"
        )
        self.footer_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Footer message
        footer_text = self.translator.t("about_description")
        self.footer_message = ctk.CTkLabel(
            self.footer_frame,
            text=footer_text,
            font=ctk.CTkFont(family="Roboto", size=get_font_size(12)),
            text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#EEEEEE",
            wraplength=800,
            justify="left"
        )
        self.footer_message.pack(anchor="w", padx=20, pady=(0, 15), fill="x")
    
    def show_model_category(self, category):
        """Show the selected model category screen."""
        # This will be connected to the main app's show_screen function
        if self.parent and hasattr(self.parent, "master"):
            if hasattr(self.parent.master, "show_screen"):
                self.parent.master.show_screen(category)
            elif hasattr(self.parent.master, "master") and hasattr(self.parent.master.master, "show_screen"):
                self.parent.master.master.show_screen(category)
    
    def update_theme(self, theme):
        """Update dashboard colors based on theme."""
        # Update background color
        cards = ["vision_card", "speech_card", "text_card", "emotion_card"]
        self.configure(fg_color=self.theme_manager.get_color("bg_color"))
        
        # Update scrollbar colors
        scrollbar_color = "#555555" if theme == "dark" else "#BBBBBB"
        scrollbar_hover = "#777777" if theme == "dark" else "#999999"
        self.main_scroll.configure(
            scrollbar_button_color=scrollbar_color,
            scrollbar_button_hover_color=scrollbar_hover
        )
        
        # Update welcome section
        self.welcome_frame.configure(
            fg_color=self.theme_manager.get_color("card_bg"),
            border_color=self.theme_manager.get_color("border_color")
        )
        self.welcome_title.configure(text_color=self.theme_manager.get_color("fg_color"))
        self.welcome_message.configure(text_color=self.theme_manager.get_color("fg_color"))
        
        # Update start button
        button_colors = self.theme_manager.get_ctk_button_colors()
        self.start_button.configure(
            fg_color=button_colors["fg_color"],
            hover_color=button_colors["hover_color"],
            text_color=button_colors["text_color"]
        )
        
        # Update stats cards
        card_bg = self.theme_manager.get_color("card_bg")
        text_color = self.theme_manager.get_color("fg_color")
        subtitle_color = "#AAAAAA" if theme == "dark" else "#777777"
        
        for stat in self.stats:
            stat["card"].configure(
                fg_color=card_bg,
                border_color=self.theme_manager.get_color("border_color")
            )
            stat["value_label"].configure(text_color=text_color)
            stat["title_label"].configure(text_color=subtitle_color)
        
        # Update category title
        self.category_title.configure(text_color=self.theme_manager.get_color("fg_color"))
        
        # Update cards
        for card_name in cards:
            card = getattr(self, card_name, None)
            if card:
                card.update_theme(theme)
            
        # Update footer
        self.footer_frame.configure(
            fg_color=self.theme_manager.get_color("card_bg"),
            border_color=self.theme_manager.get_color("border_color")
        )
        self.footer_title.configure(text_color=self.theme_manager.get_color("fg_color"))
        self.footer_message.configure(text_color=self.theme_manager.get_color("fg_color")) 