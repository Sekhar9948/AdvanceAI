
import platform
import tkinter as tk
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication

def get_screen_metrics():
    """Get the screen width and height using the appropriate method for the platform."""
    
    system = platform.system()
    
    # Use tkinter for screen metrics (works on most platforms)
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        return screen_width, screen_height
    except:
        # Fallback to PySide6 if tkinter fails
        try:
            app = QApplication.instance()
            if not app:
                app = QApplication([])
            screen = QGuiApplication.primaryScreen()
            geometry = screen.availableGeometry()
            return geometry.width(), geometry.height()
        except:
            # Fallback to reasonable defaults
            return 1280, 720

def calculate_responsive_size(base_size, screen_size, min_size=None, max_size=None):
    """
    Calculate a responsive size based on screen size.
    
    Args:
        base_size: The base size in pixels
        screen_size: The current screen size
        min_size: Minimum size (optional)
        max_size: Maximum size (optional)
    
    Returns:
        Calculated responsive size
    """
    # Baseline screen size
    baseline = 1920 if screen_size > 1920 else screen_size
    
    # Calculate scaling factor
    scale_factor = screen_size / baseline
    
    # Calculate responsive size
    responsive_size = int(base_size * scale_factor)
    
    # Apply min/max constraints if specified
    if min_size is not None and responsive_size < min_size:
        return min_size
    if max_size is not None and responsive_size > max_size:
        return max_size
    
    return responsive_size

def get_font_size(base_size=14, screen_width=None):
    """Get a responsive font size."""
    if screen_width is None:
        screen_width, _ = get_screen_metrics()
    
    if screen_width < 800:
        return max(base_size - 2, 10)  # Smaller screens
    elif screen_width < 1280:
        return base_size  # Standard size
    elif screen_width < 1920:
        return base_size + 2  # Larger screens
    else:
        return base_size + 4  # Very large screens

def get_widget_scaling(screen_width=None, screen_height=None):
    """Get scaling factor for widgets based on screen size."""
    if screen_width is None or screen_height is None:
        screen_width, screen_height = get_screen_metrics()
    
    # Base scaling on the smaller dimension
    smaller_dimension = min(screen_width, screen_height)
    
    if smaller_dimension < 800:
        return 0.8  # Smaller screens
    elif smaller_dimension < 1200:
        return 1.0  # Standard size
    elif smaller_dimension < 1600:
        return 1.2  # Larger screens
    else:
        return 1.4  # Very large screens

def get_responsive_padding(base_padding=10, screen_width=None):
    """Get responsive padding based on screen size."""
    if screen_width is None:
        screen_width, _ = get_screen_metrics()
    
    if screen_width < 800:
        return max(base_padding - 4, 4)  # Smaller screens
    elif screen_width < 1280:
        return base_padding  # Standard size
    elif screen_width < 1920:
        return base_padding + 4  # Larger screens
    else:
        return base_padding + 8  # Very large screens 