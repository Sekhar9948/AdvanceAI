
import tkinter as tk
from PIL import Image, ImageDraw
import torch
import torchvision.transforms as transforms
import torch.nn as nn
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
model_path = os.path.join(project_root, 'trained_models','digit_classification', 'trained_model.pth')

# **🔹 Ensure the model matches the trained one exactly**
class DigitClassifier(nn.Module):
    def __init__(self):
        super(DigitClassifier, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

        self.fc1 = nn.Linear(64 * 16 * 16, 256)  # Matches trained model
        self.fc2 = nn.Linear(256, 10)  # 10 classes (digits 0-9)

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = x.view(x.shape[0], -1)  # Flatten
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# **🔹 Load Model Function (Fixed)**
def load_model():
    model = DigitClassifier()
    model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
    model.eval()
    return model

# **🔹 Inference Class (Same UI, Correct Model)**
class DigitPredictor:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=280, height=280, bg='white')
        self.canvas.pack()

        self.image = Image.new("L", (280, 280), 255)
        self.draw = ImageDraw.Draw(self.image)

        self.canvas.bind("<B1-Motion>", self.paint)

        self.model = load_model()
        self.transform = transforms.Compose([
            transforms.Grayscale(),
            transforms.Resize((64, 64)),  # Match training input size
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))
        ])

        self.label = tk.Label(root, text="Prediction: ?", font=("Arial", 20))
        self.label.pack()

        self.predict_button = tk.Button(root, text="Predict", command=self.predict)
        self.predict_button.pack()

        self.clear_button = tk.Button(root, text="Clear", command=self.reset_board)
        self.clear_button.pack()

    def paint(self, event):
        x1, y1, x2, y2 = (event.x - 5), (event.y - 5), (event.x + 5), (event.y + 5)
        self.canvas.create_oval(x1, y1, x2, y2, fill='black')
        self.draw.ellipse([x1, y1, x2, y2], fill=0)

    def predict(self):
        image = self.image.resize((64, 64))
        image = self.transform(image).unsqueeze(0)

        with torch.no_grad():
            output = self.model(image)
            probabilities = torch.nn.functional.softmax(output, dim=1)
            predicted_class = torch.argmax(probabilities).item()
            confidence = probabilities[0][predicted_class].item()

        self.label.config(text=f"Prediction: {predicted_class} ({confidence*100:.2f}%)")

    def reset_board(self):
        self.canvas.delete("all")
        self.image = Image.new("L", (280, 280), 255)
        self.draw = ImageDraw.Draw(self.image)
        self.label.config(text="Prediction: ?")

if __name__ == "__main__":
    root = tk.Tk()
    app = DigitPredictor(root)
    root.mainloop()