
import customtkinter as ctk
from ..utils.responsive_utils import get_font_size

class ModelOption(ctk.CTkFrame):
    """A selectable model option within a category."""
    
    def __init__(self, parent, title, description, icon_path=None, theme_manager=None, command=None):
        # Get colors from theme manager
        card_colors = theme_manager.get_ctk_frame_colors() if theme_manager else {"fg_color": "#2D2D2D", "border_color": "#424242"}
        
        # Initialize with theme-specific colors
        super().__init__(
            parent,
            corner_radius=8,
            fg_color=card_colors["fg_color"],
            border_width=1,
            border_color=card_colors["border_color"]
        )
        
        self.title = title
        self.description = description
        self.icon_path = icon_path
        self.theme_manager = theme_manager
        self.command = command
        
        # Create content
        self.create_content()
    
    def create_content(self):
        """Create model option content."""
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.main_container,
            text=self.title,
            font=ctk.CTkFont(family="Roboto", size=get_font_size(15), weight="bold"),
            text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#FFFFFF"
        )
        self.title_label.pack(anchor="w", pady=(0, 5))
        
        # Description
        self.desc_label = ctk.CTkLabel(
            self.main_container,
            text=self.description,
            font=ctk.CTkFont(family="Roboto", size=get_font_size(12)),
            text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#DDDDDD",
            wraplength=250,
            justify="left"
        )
        self.desc_label.pack(anchor="w", fill="x", pady=(0, 10))
        
        # Try button
        button_colors = self.theme_manager.get_ctk_button_colors() if self.theme_manager else {
            "fg_color": "#1E88E5", 
            "hover_color": "#0D47A1",
            "text_color": "#FFFFFF",
            "border_color": "#424242"
        }
        
        self.try_button = ctk.CTkButton(
            self.main_container,
            text="Try Model",
            font=ctk.CTkFont(family="Roboto", size=get_font_size(12)),
            fg_color=button_colors["fg_color"],
            hover_color=button_colors["hover_color"],
            text_color=button_colors["text_color"],
            corner_radius=5,
            height=28,
            command=self.handle_try
        )
        self.try_button.pack(side="right")
    
    def handle_try(self):
        """Handle try button click."""
        if self.command:
            self.command(self.title)
    
    def update_theme(self, theme):
        """Update option colors based on theme."""
        if not self.theme_manager:
            return
            
        # Update frame colors
        card_colors = self.theme_manager.get_ctk_frame_colors()
        self.configure(
            fg_color=card_colors["fg_color"],
            border_color=card_colors["border_color"]
        )
        
        # Update text colors
        text_color = self.theme_manager.get_color("fg_color")
        self.title_label.configure(text_color=text_color)
        self.desc_label.configure(text_color=text_color)
        
        # Update button colors
        button_colors = self.theme_manager.get_ctk_button_colors()
        self.try_button.configure(
            fg_color=button_colors["fg_color"],
            hover_color=button_colors["hover_color"],
            text_color=button_colors["text_color"]
        )

class BaseModelScreen(ctk.CTkFrame):
    """Base class for model category screens."""
    
    def __init__(self, parent, theme_manager=None, title="AI Models", description=None):
        # Initialize with theme-specific colors
        bg_color = theme_manager.get_color("bg_color") if theme_manager else "#1E1E1E"
        
        super().__init__(
            parent,
            corner_radius=0,
            fg_color=bg_color
        )
        
        self.parent = parent
        self.theme_manager = theme_manager
        self.title = title
        self.description = description
        self.models = []
        
        # Main scrollable container
        self.main_scrollable = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_fg_color="transparent",
            scrollbar_button_color="#555555",
            scrollbar_button_hover_color="#777777"
        )
        self.main_scrollable.pack(fill="both", expand=True)
        
        # Create basic components
        self.create_header()
        self.create_model_options_container()
        self.create_preview_area()
    
    def create_header(self):
        """Create the header section with title and description."""
        # Header frame
        self.header_frame = ctk.CTkFrame(
            self.main_scrollable,
            corner_radius=12,
            fg_color=self.theme_manager.get_color("card_bg") if self.theme_manager else "#2D2D2D",
            border_width=1,
            border_color=self.theme_manager.get_color("border_color") if self.theme_manager else "#424242"
        )
        self.header_frame.pack(fill="x", padx=20, pady=20)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=self.title,
            font=ctk.CTkFont(family="Roboto", size=get_font_size(22), weight="bold"),
            text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#FFFFFF"
        )
        self.title_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Description (if provided)
        if self.description:
            self.desc_label = ctk.CTkLabel(
                self.header_frame,
                text=self.description,
                font=ctk.CTkFont(family="Roboto", size=get_font_size(14)),
                text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#EEEEEE",
                wraplength=800,
                justify="left"
            )
            self.desc_label.pack(anchor="w", padx=20, pady=(0, 20), fill="x")
    
    def create_model_options_container(self):
        """Create the container for model options."""
        # Main container frame
        self.content_frame = ctk.CTkFrame(
            self.main_scrollable,
            corner_radius=0,
            fg_color="transparent"
        )
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Two-column layout (using grid)
        self.content_frame.grid_columnconfigure(0, weight=3)  # Model options
        self.content_frame.grid_columnconfigure(1, weight=7)  # Preview area
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Models container
        self.models_container = ctk.CTkFrame(
            self.content_frame,
            corner_radius=12,
            fg_color=self.theme_manager.get_color("card_bg") if self.theme_manager else "#2D2D2D",
            border_width=1,
            border_color=self.theme_manager.get_color("border_color") if self.theme_manager else "#424242"
        )
        self.models_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Models title
        self.models_title = ctk.CTkLabel(
            self.models_container,
            text="Available Models",
            font=ctk.CTkFont(family="Roboto", size=get_font_size(16), weight="bold"),
            text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#FFFFFF"
        )
        self.models_title.pack(anchor="w", padx=15, pady=(15, 15))
        
        # Options frame (scrollable for many models)
        self.options_scroll = ctk.CTkScrollableFrame(
            self.models_container,
            corner_radius=0,
            fg_color="transparent",
            scrollbar_fg_color="transparent",
            scrollbar_button_color="#555555" if self.theme_manager.current_theme == "dark" else "#BBBBBB",
            scrollbar_button_hover_color="#777777" if self.theme_manager.current_theme == "dark" else "#999999"
        )
        self.options_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def create_preview_area(self):
        """Create the model preview area."""
        # Preview frame
        self.preview_frame = ctk.CTkFrame(
            self.content_frame,
            corner_radius=12,
            fg_color=self.theme_manager.get_color("card_bg") if self.theme_manager else "#2D2D2D",
            border_width=1,
            border_color=self.theme_manager.get_color("border_color") if self.theme_manager else "#424242"
        )
        self.preview_frame.grid(row=0, column=1, sticky="nsew")
        
        # Preview title
        self.preview_title = ctk.CTkLabel(
            self.preview_frame,
            text="Model Preview",
            font=ctk.CTkFont(family="Roboto", size=get_font_size(16), weight="bold"),
            text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#FFFFFF"
        )
        self.preview_title.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Preview container (scrollable for large content)
        self.preview_scroll = ctk.CTkScrollableFrame(
            self.preview_frame,
            corner_radius=0,
            fg_color="transparent",
            scrollbar_fg_color="transparent",
            scrollbar_button_color="#555555" if self.theme_manager.current_theme == "dark" else "#BBBBBB",
            scrollbar_button_hover_color="#777777" if self.theme_manager.current_theme == "dark" else "#999999",
            height=400  # Default height, will expand when content is added
        )
        self.preview_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Preview message
        self.preview_message = ctk.CTkLabel(
            self.preview_scroll,
            text="Select a model from the list to preview it here.",
            font=ctk.CTkFont(family="Roboto", size=get_font_size(14)),
            text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#EEEEEE",
        )
        self.preview_message.pack(padx=15, pady=(40, 0))
    
    def add_model(self, title, description, icon_path=None):
        """Add a model option to the list."""
        # Create model option
        model_option = ModelOption(
            self.options_scroll,
            title=title,
            description=description,
            icon_path=icon_path,
            theme_manager=self.theme_manager,
            command=self.show_model_preview
        )
        model_option.pack(fill="x", expand=False, padx=5, pady=5)
        
        # Add to list of models
        self.models.append(model_option)
    
    def show_model_preview(self, model_title):
        """Show the preview for the selected model."""
        # Clear previous preview content
        self.clear_preview()
        
        # Set preview title
        self.set_preview_title(model_title)
        
        # Add "Coming Soon" message as placeholder
        self.add_preview_message("Model integration coming soon...")
        
        # Model preview image placeholder
        preview_frame = ctk.CTkFrame(
            self.preview_scroll, 
            fg_color=self.theme_manager.get_color("bg_color") if self.theme_manager else "#1E1E1E",
            height=200,
            corner_radius=8,
            border_width=1,
            border_color="#444444" if self.theme_manager.current_theme == "dark" else "#DDDDDD"
        )
        preview_frame.pack(fill="x", padx=15, pady=10)
        
        preview_text = ctk.CTkLabel(
            preview_frame,
            text="AI Model Visualization",
            font=ctk.CTkFont(family="Roboto", size=get_font_size(14)),
            text_color="#AAAAAA"
        )
        preview_text.place(relx=0.5, rely=0.5, anchor="center")
        
        # Add placeholder for model parameters
        params_title = ctk.CTkLabel(
            self.preview_scroll,
            text="Model Parameters",
            font=ctk.CTkFont(family="Roboto", size=get_font_size(16), weight="bold"),
            text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#FFFFFF"
        )
        params_title.pack(anchor="w", padx=15, pady=(30, 10))
        
        # Add parameter sliders as placeholders
        for i, param in enumerate(["Parameter 1", "Parameter 2", "Parameter 3"]):
            param_frame = ctk.CTkFrame(self.preview_scroll, fg_color="transparent")
            param_frame.pack(fill="x", padx=15, pady=8)
            
            param_label = ctk.CTkLabel(
                param_frame,
                text=param,
                font=ctk.CTkFont(family="Roboto", size=get_font_size(13)),
                text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#EEEEEE",
                width=100
            )
            param_label.pack(side="left")
            
            slider = ctk.CTkSlider(
                param_frame,
                from_=0,
                to=100,
                number_of_steps=10,
                width=300,
                progress_color=self.theme_manager.get_color("primary_color") if self.theme_manager else "#1E88E5"
            )
            slider.pack(side="left", padx=10, fill="x", expand=True)
            slider.set(0.5)  # Set default value
            
            value_label = ctk.CTkLabel(
                param_frame,
                text="50%",
                font=ctk.CTkFont(family="Roboto", size=get_font_size(13)),
                text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#EEEEEE",
                width=50
            )
            value_label.pack(side="left")
        
        # Add Run button
        button_colors = self.theme_manager.get_ctk_button_colors() if self.theme_manager else {
            "fg_color": "#1E88E5", 
            "hover_color": "#0D47A1",
            "text_color": "#FFFFFF"
        }
        
        run_button = ctk.CTkButton(
            self.preview_scroll,
            text="Run Model",
            font=ctk.CTkFont(family="Roboto", size=get_font_size(14), weight="bold"),
            fg_color=button_colors["fg_color"],
            hover_color=button_colors["hover_color"],
            text_color=button_colors["text_color"],
            corner_radius=8,
            height=40
        )
        run_button.pack(padx=15, pady=(20, 20))
        
        # Model description
        desc_title = ctk.CTkLabel(
            self.preview_scroll,
            text="About This Model",
            font=ctk.CTkFont(family="Roboto", size=get_font_size(16), weight="bold"),
            text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#FFFFFF"
        )
        desc_title.pack(anchor="w", padx=15, pady=(20, 10))
        
        desc_text = (
            f"This is a preview of the {model_title} AI model. When implemented, "
            f"you will be able to adjust parameters and see results in real-time. "
            f"The model will process inputs and visualize outputs in the space above."
        )
        
        self.add_preview_description(desc_text)
    
    def clear_preview(self):
        """Clear the contents of the preview area."""
        for widget in self.preview_scroll.winfo_children():
            widget.destroy()
            
    def set_preview_title(self, title):
        """Set the title of the preview area."""
        self.preview_title.configure(text=f"{title} Preview")
        
    def add_preview_message(self, message):
        """Add a message to the preview area."""
        message_label = ctk.CTkLabel(
            self.preview_scroll,
            text=message,
            font=ctk.CTkFont(family="Roboto", size=get_font_size(14)),
            text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#EEEEEE",
            wraplength=600,
            justify="left"
        )
        message_label.pack(padx=15, pady=20)
        
    def add_preview_description(self, description):
        """Add a description to the preview area."""
        desc_label = ctk.CTkLabel(
            self.preview_scroll,
            text=description,
            font=ctk.CTkFont(family="Roboto", size=get_font_size(14)),
            text_color=self.theme_manager.get_color("fg_color") if self.theme_manager else "#EEEEEE",
            wraplength=600,
            justify="left"
        )
        desc_label.pack(anchor="w", padx=15, pady=(15, 10), fill="x")
    
    def update_theme(self, theme):
        """Update screen colors based on theme."""
        # Update scrollbar colors
        scrollbar_color = "#555555" if theme == "dark" else "#BBBBBB"
        scrollbar_hover = "#777777" if theme == "dark" else "#999999"
        
        # Update main scrollbar
        self.main_scrollable.configure(
            fg_color="transparent",
            scrollbar_button_color=scrollbar_color,
            scrollbar_button_hover_color=scrollbar_hover
        )
        
        # Update options scrollbar
        self.options_scroll.configure(
            fg_color="transparent",
            scrollbar_button_color=scrollbar_color,
            scrollbar_button_hover_color=scrollbar_hover
        )
        
        # Update preview scrollbar
        self.preview_scroll.configure(
            fg_color="transparent",
            scrollbar_button_color=scrollbar_color,
            scrollbar_button_hover_color=scrollbar_hover
        )
        
        # Update background color
        self.configure(fg_color=self.theme_manager.get_color("bg_color"))
        
        # Update header section
        self.header_frame.configure(
            fg_color=self.theme_manager.get_color("card_bg"),
            border_color=self.theme_manager.get_color("border_color")
        )
        self.title_label.configure(text_color=self.theme_manager.get_color("fg_color"))
        if hasattr(self, 'desc_label'):
            self.desc_label.configure(text_color=self.theme_manager.get_color("fg_color"))
        
        # Update models container
        self.models_container.configure(
            fg_color=self.theme_manager.get_color("card_bg"),
            border_color=self.theme_manager.get_color("border_color")
        )
        self.models_title.configure(text_color=self.theme_manager.get_color("fg_color"))
        
        # Update preview area
        self.preview_frame.configure(
            fg_color=self.theme_manager.get_color("card_bg"),
            border_color=self.theme_manager.get_color("border_color")
        )
        self.preview_title.configure(text_color=self.theme_manager.get_color("fg_color"))
        
        # Update all model options
        for model in self.models:
            model.update_theme(theme) 