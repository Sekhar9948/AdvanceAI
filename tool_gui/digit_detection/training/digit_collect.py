
import tkinter as tk
from PIL import Image, ImageDraw
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
dataset_path = os.path.join(project_root, 'dataset/digit_data')

# Folder to save images
SAVE_DIR = dataset_path
os.makedirs(SAVE_DIR, exist_ok=True)

# Class List (0-9)
classes = [str(i) for i in range(10)]
current_class_index = 0  # Start with 0
image_count = 0  # Track images per class

class DataCollector:
    def __init__(self, root):
        global current_class_index, image_count
        self.root = root
        self.canvas = tk.Canvas(root, width=280, height=280, bg='white')
        self.canvas.pack()

        self.image = Image.new("L", (280, 280), 255)
        self.draw = ImageDraw.Draw(self.image)

        self.canvas.bind("<B1-Motion>", self.paint)

        self.label = tk.Label(root, text=f"Draw: {classes[current_class_index]}", font=("Arial", 16))
        self.label.pack()

        self.save_button = tk.Button(root, text="Save", command=self.save_image)
        self.save_button.pack()

        self.clear_button = tk.Button(root, text="Clear", command=self.reset_board)
        self.clear_button.pack()

    def paint(self, event):
        x1, y1, x2, y2 = (event.x - 5), (event.y - 5), (event.x + 5), (event.y + 5)
        self.canvas.create_oval(x1, y1, x2, y2, fill='black')
        self.draw.ellipse([x1, y1, x2, y2], fill=0)

    def save_image(self):
        global current_class_index, image_count

        # Resize image to 64x64
        resized_image = self.image.resize((64, 64))
        
        # Save in format: "digit_count.png" (e.g., "3_5.png")
        filename = f"{classes[current_class_index]}_{image_count}.png"
        resized_image.save(os.path.join(SAVE_DIR, filename))

        image_count += 1  # Increment count for the current digit

        if image_count == 10:  # Move to next digit after 10 samples
            image_count = 0
            current_class_index += 1
            if current_class_index >= len(classes):  # If all digits are collected
                self.label.config(text="Collection complete! Close the window.")
                self.save_button.config(state=tk.DISABLED)
                return

        self.label.config(text=f"Draw: {classes[current_class_index]}")  # Update label
        self.reset_board()

    def reset_board(self):
        self.canvas.delete("all")
        self.image = Image.new("L", (280, 280), 255)
        self.draw = ImageDraw.Draw(self.image)

if __name__ == "__main__":
    root = tk.Tk()
    app = DataCollector(root)
    root.mainloop()