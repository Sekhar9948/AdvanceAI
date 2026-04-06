
import customtkinter as ctk
from training.digit_inference import load_model
import os
from PIL import Image, ImageDraw, ImageGrab
from threading import Thread
from training.digit_train_model import train_model
import torch
from torchvision import transforms


import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from language_manager import LanguageManager

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
dataset_path = os.path.join(project_root, 'dataset','digit_data')


# Initialize the main window
class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.translator = LanguageManager()
        self.translator.load_language("en")
        self.title(self.translator.t("digit_recognition_gui"))
        self.geometry('1000x600')

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

        # Initialize digit and sample tracking
        self.digits = [str(i) for i in range(10)]
        self.current_digit_index = 0
        self.sample_count = 0

        # Create digit_data directory if it doesn't exist
        os.makedirs(dataset_path, exist_ok=True)

        # Left Column - Row 1: Drawing Board
        self.drawing_frame = ctk.CTkFrame(self)
        self.drawing_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        self.canvas = ctk.CTkCanvas(self.drawing_frame, width=280, height=280, bg='lightgray', highlightthickness=0)
        self.canvas.pack(pady=10)

        self.save_button = ctk.CTkButton(self.drawing_frame, text='Save', command=self.save_drawing, fg_color='blue', text_color='white', font=('Arial', 12, 'bold'))
        self.clear_button = ctk.CTkButton(self.drawing_frame, text='Clear', command=self.clear_canvas, fg_color='red', text_color='white', font=('Arial', 12, 'bold'))

        self.save_button.pack(side='left', padx=10)
        self.clear_button.pack(side='right', padx=10)

        # Display current digit and sample number
        self.digit_label = ctk.CTkLabel(self.drawing_frame, text=f'Draw: {self.digits[self.current_digit_index]} Sample: {self.sample_count + 1}', font=('Arial', 12))
        self.digit_label.pack(pady=5)

        # Initialize image for drawing
        self.image = Image.new('L', (280, 280), 255)
        self.draw = ImageDraw.Draw(self.image)

        # Bind mouse events for drawing
        self.canvas.bind('<B1-Motion>', self.paint)
        self.canvas.bind('<ButtonRelease-1>', self.reset)

        # Initialize drawing state
        self.last_x, self.last_y = None, None

        # Add a text field for the number of samples per digit
        self.samples_entry = ctk.CTkEntry(self.drawing_frame, placeholder_text='Samples per Digit')
        self.samples_entry.pack(pady=5)

        # Left Column - Row 2: Train Model
        self.train_frame = ctk.CTkFrame(self)
        self.train_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)

        self.epochs_entry = ctk.CTkEntry(self.train_frame, placeholder_text='Epochs')
        self.learning_rate_entry = ctk.CTkEntry(self.train_frame, placeholder_text='Learning Rate')
        self.train_button = ctk.CTkButton(self.train_frame, text='Train Model', command=self.train_model, fg_color='green', text_color='white', font=('Arial', 12, 'bold'))

        self.epochs_entry.pack(pady=5)
        self.learning_rate_entry.pack(pady=5)
        self.train_button.pack(pady=5)

        # Right Column: Inference Board
        self.inference_frame = ctk.CTkFrame(self)
        self.inference_frame.grid(row=0, column=1, rowspan=2, sticky='nsew', padx=10, pady=10)

        self.inference_canvas = ctk.CTkCanvas(self.inference_frame, width=280, height=280, bg='lightgray', highlightthickness=0)
        self.inference_canvas.pack(pady=10)

        # Add predict and clear buttons to the inference board
        self.predict_button = ctk.CTkButton(self.inference_frame, text='Predict', command=self.predict_digit, fg_color='orange', text_color='white', font=('Arial', 12, 'bold'))
        self.clear_inference_button = ctk.CTkButton(self.inference_frame, text='Clear', command=self.clear_inference_canvas, fg_color='red', text_color='white', font=('Arial', 12, 'bold'))

        self.predict_button.pack(side='left', padx=10)
        self.clear_inference_button.pack(side='right', padx=10)

        # Label to display prediction result
        self.prediction_label = ctk.CTkLabel(self.inference_frame, text='Prediction: ?', font=('Arial', 16))
        self.prediction_label.pack(pady=10)

        # Bind mouse events for inference drawing
        self.inference_canvas.bind('<B1-Motion>', self.paint_inference)
        self.inference_canvas.bind('<ButtonRelease-1>', self.reset_inference)

        # Initialize inference drawing state
        self.inference_last_x, self.inference_last_y = None, None

    def clear_canvas(self):
        # Clear the drawing board
        self.canvas.delete('all')
        self.image = Image.new('L', (280, 280), 255)
        self.draw = ImageDraw.Draw(self.image)

    def save_drawing(self):
        # Get the number of samples per digit from the user input
        try:
            samples_per_digit = int(self.samples_entry.get())
        except ValueError:
            print("Invalid input for samples per digit.")
            return

        # Resize image to 64x64
        resized_image = self.image.resize((64, 64))
        filename = f'{dataset_path}/{self.digits[self.current_digit_index]}_{self.sample_count}.png'
        resized_image.save(filename)

        # Update sample count and digit index
        self.sample_count += 1
        if self.sample_count == samples_per_digit:
            self.sample_count = 0
            self.current_digit_index += 1
            if self.current_digit_index >= len(self.digits):
                self.digit_label.configure(text='Collection complete!')
                self.save_button.config(state='disabled')
                return

        # Update label and clear board
        self.digit_label.configure(text=f'Draw: {self.digits[self.current_digit_index]} Sample: {self.sample_count + 1}')
        self.clear_canvas()

    def paint(self, event):
        if self.last_x and self.last_y:
            self.canvas.create_line((self.last_x, self.last_y, event.x, event.y), fill='black', width=5)
            self.draw.line((self.last_x, self.last_y, event.x, event.y), fill=0, width=5)
        self.last_x, self.last_y = event.x, event.y

    def reset(self, event):
        self.last_x, self.last_y = None, None

    def train_model(self):
        # Start training in a separate thread
        self.train_thread = Thread(target=self.run_training)
        self.train_thread.start()

        # Create a progress bar
        self.progress_bar = ctk.CTkProgressBar(self.train_frame, width=200)
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)

    def run_training(self):
        # Retrieve user inputs for epochs and learning rate
        try:
            epochs = int(self.epochs_entry.get())
            learning_rate = float(self.learning_rate_entry.get())
        except ValueError:
            print("Invalid input for epochs or learning rate.")
            return

        # Run the actual training function with user inputs
        epoch_loss, accuracy = train_model(epochs=epochs, learning_rate=learning_rate)

        # Reset progress bar after training
        self.progress_bar.set(1)  # Set to complete after training
        self.update_idletasks()

        # Display accuracy and loss
        if hasattr(self, 'result_label'):
            self.result_label.configure(text=f'Loss: {epoch_loss:.4f}, Accuracy: {accuracy:.2f}%')
        else:
            self.result_label = ctk.CTkLabel(self.train_frame, text=f'Loss: {epoch_loss:.4f}, Accuracy: {accuracy:.2f}%', font=('Arial', 12))
            self.result_label.pack(pady=5)

    def clear_inference_canvas(self):
        # Clear the inference drawing board
        self.inference_canvas.delete('all')

    def predict_digit(self):
        # Ensure the canvas is updated
        self.inference_canvas.update()

        # Capture the canvas content as an image
        x = self.inference_canvas.winfo_rootx()
        y = self.inference_canvas.winfo_rooty()
        x1 = x + self.inference_canvas.winfo_width()
        y1 = y + self.inference_canvas.winfo_height()
        img = ImageGrab.grab().crop((x, y, x1, y1)).convert('L').resize((64, 64))

        # Debugging: Save the captured image to verify
        img.save('debug_captured_image.png')

        # Load the model and perform inference
        model = load_model()
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))
        ])
        image_tensor = transform(img).unsqueeze(0)

        # Debugging: Print the image tensor
        print('Image Tensor:', image_tensor)

        with torch.no_grad():
            output = model(image_tensor)
            probabilities = torch.nn.functional.softmax(output, dim=1)
            predicted_class = torch.argmax(probabilities).item()
            confidence = probabilities[0][predicted_class].item()

        # Debugging: Print the prediction and confidence
        print(f'Prediction: {predicted_class}, Confidence: {confidence*100:.2f}%')

        # Display the prediction and probability
        self.prediction_label.configure(text=f'Prediction: {predicted_class} ({confidence*100:.2f}%)')
        self.update_idletasks()

    def paint_inference(self, event):
        if self.inference_last_x and self.inference_last_y:
            self.inference_canvas.create_line((self.inference_last_x, self.inference_last_y, event.x, event.y), fill='black', width=5)
        self.inference_last_x, self.inference_last_y = event.x, event.y

    def reset_inference(self, event):
        self.inference_last_x, self.inference_last_y = None, None

if __name__ == '__main__':
    app = MainApp()
    app.mainloop() 