
import customtkinter as ctk
from language_detection import train_language_detection_model, predict_language
import threading
import queue
import os

import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from language_manager import LanguageManager

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
model_path = os.path.join(project_root, 'trained_models','hand_gesture_detection', 'gesture_model.pkl')
dataset_path = os.path.join(project_root, 'dataset','language_data','Language Detection.csv')

class LanguageDetectionGUI:
    def __init__(self):
        # Set theme and color scheme
        # ctk.set_appearance_mode("light")
        ctk.set_appearance_mode("dark")
        # ctk.set_default_color_theme("blue")
        ctk.set_default_color_theme("dark-blue")

        self.translator = LanguageManager()
        self.translator.load_language("en")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title(self.translator.get("language_detection_title"))
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Initialize model
        self.model = None
        self.model_queue = queue.Queue()
        
        # Model configuration variables
        self.num_samples = ctk.StringVar(value="1000")
        self.num_iterations = ctk.StringVar(value="50")
        self.learning_rate = ctk.StringVar(value="0.01")
        
        # Training progress variables
        self.current_iteration = ctk.StringVar(value="0")
        self.current_loss = ctk.StringVar(value="0.0000")
        self.current_accuracy = ctk.StringVar(value="0.0000")
        
        # Create main container with padding
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure grid weights
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)
        
        # Create header
        self.create_header()
        
        # Create content area
        self.create_content_area()
        
    def create_header(self,translator=None):
        """Create the header section with title and description"""
        header_frame = ctk.CTkFrame(self.main_container)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Configure header grid
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text=self.translator.t("Language Detection System"),
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Description
        desc_label = ctk.CTkLabel(
            header_frame,
            text=self.translator.t("Configure the model and monitor training progress in real-time"),
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        desc_label.grid(row=1, column=0)
        
    def create_content_area(self):
        """Create the main content area with configuration, progress, and input sections"""
        # Create content frame
        content_frame = ctk.CTkFrame(self.main_container)
        content_frame.grid(row=1, column=0, sticky="nsew")
        
        # Configure content grid
        content_frame.grid_columnconfigure(1, weight=2)  # Progress section
        content_frame.grid_columnconfigure(2, weight=1)  # Input section
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Create configuration section
        self.create_config_section(content_frame)
        
        # Create progress section
        self.create_progress_section(content_frame)
        
        # Create input section
        self.create_input_section(content_frame)
        
    def create_config_section(self, parent):
        """Create the model configuration section"""
        config_frame = ctk.CTkFrame(parent)
        config_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Configure config frame grid
        config_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            config_frame,
            text=self.translator.t("Model Configuration"),
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(20, 20))
        
        # Number of samples
        samples_frame = ctk.CTkFrame(config_frame)
        samples_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        samples_frame.grid_columnconfigure(1, weight=1)
        
        samples_label = ctk.CTkLabel(
            samples_frame,
            text=self.translator.t("Number of Samples:"),
            font=ctk.CTkFont(size=14)
        )
        samples_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        samples_entry = ctk.CTkEntry(
            samples_frame,
            textvariable=self.num_samples,
            width=100,
            font=ctk.CTkFont(size=14)
        )
        samples_entry.grid(row=0, column=1, sticky="e")
        
        # Number of iterations
        iterations_frame = ctk.CTkFrame(config_frame)
        iterations_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        iterations_frame.grid_columnconfigure(1, weight=1)
        
        iterations_label = ctk.CTkLabel(
            iterations_frame,
            text=self.translator.t("Training Iterations:"),
            font=ctk.CTkFont(size=14)
        )
        iterations_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        iterations_entry = ctk.CTkEntry(
            iterations_frame,
            textvariable=self.num_iterations,
            width=100,
            font=ctk.CTkFont(size=14)
        )
        iterations_entry.grid(row=0, column=1, sticky="e")
        
        # Learning rate
        lr_frame = ctk.CTkFrame(config_frame)
        lr_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))
        lr_frame.grid_columnconfigure(1, weight=1)
        
        lr_label = ctk.CTkLabel(
            lr_frame,
            text="Learning Rate:",
            font=ctk.CTkFont(size=14)
        )
        lr_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        lr_entry = ctk.CTkEntry(
            lr_frame,
            textvariable=self.learning_rate,
            width=100,
            font=ctk.CTkFont(size=14)
        )
        lr_entry.grid(row=0, column=1, sticky="e")
        
        # Initialize button
        self.init_button = ctk.CTkButton(
            config_frame,
            text=self.translator.t("Initialize Model"),
            command=self.initialize_model,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.init_button.grid(row=4, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        # Status label
        self.status_label = ctk.CTkLabel(
            config_frame,
            text="",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.status_label.grid(row=5, column=0, pady=(0, 20))
        
    def create_progress_section(self, parent):
        """Create the training progress section"""
        progress_frame = ctk.CTkFrame(parent)
        progress_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        
        # Configure progress frame grid
        progress_frame.grid_columnconfigure(0, weight=1)
        progress_frame.grid_rowconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            progress_frame,
            text="Training Progress",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(20, 10))
        
        # Progress display
        progress_display = ctk.CTkFrame(progress_frame)
        progress_display.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        progress_display.grid_columnconfigure(0, weight=1)
        
        # Current iteration
        iteration_frame = ctk.CTkFrame(progress_display)
        iteration_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        iteration_frame.grid_columnconfigure(1, weight=1)
        
        iteration_label = ctk.CTkLabel(
            iteration_frame,
            text="Current Iteration:",
            font=ctk.CTkFont(size=14)
        )
        iteration_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        iteration_value = ctk.CTkLabel(
            iteration_frame,
            textvariable=self.current_iteration,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        iteration_value.grid(row=0, column=1, sticky="e")
        
        # Current loss
        loss_frame = ctk.CTkFrame(progress_display)
        loss_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        loss_frame.grid_columnconfigure(1, weight=1)
        
        loss_label = ctk.CTkLabel(
            loss_frame,
            text="Current Loss:",
            font=ctk.CTkFont(size=14)
        )
        loss_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        loss_value = ctk.CTkLabel(
            loss_frame,
            textvariable=self.current_loss,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        loss_value.grid(row=0, column=1, sticky="e")
        
        # Current accuracy
        accuracy_frame = ctk.CTkFrame(progress_display)
        accuracy_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        accuracy_frame.grid_columnconfigure(1, weight=1)
        
        accuracy_label = ctk.CTkLabel(
            accuracy_frame,
            text="Current Accuracy:",
            font=ctk.CTkFont(size=14)
        )
        accuracy_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        accuracy_value = ctk.CTkLabel(
            accuracy_frame,
            textvariable=self.current_accuracy,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        accuracy_value.grid(row=0, column=1, sticky="e")
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(progress_display)
        self.progress_bar.grid(row=3, column=0, sticky="ew", pady=(20, 0))
        self.progress_bar.set(0)
        
    def create_input_section(self, parent):
        """Create the input section with text area and detect button"""
        input_frame = ctk.CTkFrame(parent)
        input_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 0))
        
        # Configure input frame grid
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_rowconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            input_frame,
            text="Text Input",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(20, 10))
        
        # Add instruction label above text area
        instruction_label = ctk.CTkLabel(
            input_frame,
            text="Enter input below",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="gray"
        )
        instruction_label.grid(row=1, column=0, pady=(0, 5))
        
        # Remove placeholder text from text area
        self.text_area = ctk.CTkTextbox(
            input_frame,
            font=ctk.CTkFont(size=14),
            wrap="word",
            height=200
        )
        self.text_area.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self.text_area.bind("<FocusIn>", self.on_text_area_focus)
        
        # Detect button
        self.detect_button = ctk.CTkButton(
            input_frame,
            text="Detect Language",
            command=self.detect_language,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.detect_button.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Create result display section
        result_frame = ctk.CTkFrame(input_frame)
        result_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(0, 10))
        result_frame.grid_columnconfigure(0, weight=1)
        
        # Language display
        self.language_label = ctk.CTkLabel(
            result_frame,
            text="Predicted Language: -",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.language_label.grid(row=0, column=0, pady=(10, 5))
        
        # Confidence display
        self.confidence_label = ctk.CTkLabel(
            result_frame,
            text="Confidence: -",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.confidence_label.grid(row=1, column=0, pady=(0, 10))
        
    def on_text_area_focus(self, event):
        """Handle text area focus event"""
        current_text = self.text_area.get("1.0", "end-1c")
        if current_text == "Enter text here to detect language...":
            self.text_area.delete("1.0", "end")
            # Rebind focus event to ensure it triggers correctly
            self.text_area.bind("<FocusIn>", self.on_text_area_focus)
            
    def update_progress(self, iteration, loss, accuracy, total_iterations):
        """Update the training progress display"""
        self.current_iteration.set(str(iteration))
        self.current_loss.set(f"{loss:.4f}")
        self.current_accuracy.set(f"{accuracy:.4f}")
        self.progress_bar.set(iteration / total_iterations)
        
    def initialize_model(self):
        """Initialize the language detection model in a background thread"""
        try:
            # Validate inputs
            num_samples = int(self.num_samples.get())
            num_iterations = int(self.num_iterations.get())
            learning_rate = float(self.learning_rate.get())
            
            if num_samples <= 0 or num_iterations <= 0 or learning_rate <= 0:
                raise ValueError("All values must be positive")
                
        except ValueError as e:
            self.status_label.configure(text="Error: Please enter valid numbers")
            return
        
        self.status_label.configure(text="Initializing model...")
        self.init_button.configure(state="disabled")
        
        def init_model():
            try:
                file_path = dataset_path
                model, _ = train_language_detection_model(
                    file_path=file_path,
                    num_samples=num_samples,
                    n_iterations=num_iterations,
                    learning_rate=learning_rate,
                    progress_callback=self.update_progress
                )
                self.model_queue.put(model)
                self.root.after(0, self.update_status, "Model ready!")
                self.root.after(0, self.detect_button.configure, {"state": "normal"})
                print("--- Model initialized successfully, detect button enabled ---")
            except Exception as e:
                self.root.after(0, self.update_status, f"Error: {str(e)}")
                self.root.after(0, self.init_button.configure, {"state": "normal"})
                print(f"--- Error during model initialization: {str(e)} ---")
        
        thread = threading.Thread(target=init_model)
        thread.daemon = True
        thread.start()
        
    def update_status(self, text):
        """Update the status label text"""
        self.status_label.configure(text=text)
        
    def detect_language(self):
        """Detect language from input text"""
        try:
            # Check if model is initialized
            if self.model is None and self.model_queue.empty():
                self.update_status("Please initialize the model first")
                return
            elif self.model is None:
                self.model = self.model_queue.get()
            
            # Get text from text area
            text = self.text_area.get("1.0", "end-1c").strip()
            if not text:
                self.update_status("Please enter some text")
                return
            
            # Disable button while processing
            self.detect_button.configure(state="disabled")
            self.update_status("Detecting language...")
            
            def process_text():
                try:
                    # --- Start Debug ---
                    print("--- process_text thread started ---")
                    if self.model is None:
                        print("--- ERROR: self.model is None inside process_text ---")
                        self.root.after(0, lambda: self.update_status("Error: Model is not available."))
                        self.root.after(0, lambda: self.detect_button.configure(state="normal"))
                        return
                    else:
                         print(f"--- Model type in process_text: {type(self.model)} ---")

                    if not text:
                        print("--- ERROR: Text is empty in process_text ---")
                        self.root.after(0, lambda: self.update_status("Error: Input text is empty."))
                        self.root.after(0, lambda: self.detect_button.configure(state="normal"))
                        return
                    else:
                        print(f"--- Text to predict in process_text: '{text[:50]}...' ---")
                    # --- End Debug ---

                    # Use the predict_language function imported at the top level
                    print("--- Attempting to call predict_language from GUI ---")
                    predicted_lang, confidence = predict_language(self.model, text)
                    print(f"--- Called predict_language. Result: {predicted_lang}, Confidence: {confidence} ---")
                    
                    # Update the result display
                    self.root.after(0, lambda: self.update_result(predicted_lang, confidence))
                    
                    # Clear text area and restore placeholder
                    self.root.after(0, lambda: self.text_area.delete("1.0", "end"))
                    # self.root.after(0, lambda: self.text_area.insert("1.0", "Enter text here to detect language..."))
                    
                    # Re-enable button and update status
                    self.root.after(0, lambda: self.detect_button.configure(state="normal"))
                    self.root.after(0, lambda: self.update_status("Ready for next text"))
                    
                except Exception as e:
                    print(f"--- Error in detection thread: {str(e)} ---")
                    self.root.after(0, lambda: self.update_status(f"Error: {str(e)}"))
                    self.root.after(0, lambda: self.detect_button.configure(state="normal"))
            
            # Start detection in a separate thread
            thread = threading.Thread(target=process_text)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            print(f"Error in detect_language method: {str(e)}")
            self.update_status(f"Error: {str(e)}")
            self.detect_button.configure(state="normal")
        
    def update_result(self, language, confidence):
        """Update the result display"""
        self.language_label.configure(text=f"Predicted Language: {language}")
        self.confidence_label.configure(text=f"Confidence: {confidence * 100:.2f}%")
        
    def clear_result(self):
        """Clear the result display"""
        self.language_label.configure(text="Predicted Language: -")
        self.confidence_label.configure(text="Confidence: -")
        
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = LanguageDetectionGUI()
    app.run() 