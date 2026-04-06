
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from torch.utils.data import DataLoader, Dataset
import torchvision.models as models
import os
from PIL import Image

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
dataset_path = os.path.join(project_root, 'dataset','digit_data')



# Custom Dataset for Handwritten Digits
class DigitDataset(Dataset):
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.files = os.listdir(root_dir)
        self.transform = transforms.Compose([
            transforms.Grayscale(),
            transforms.Resize((64, 64)),  # Ensure images are 64x64
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))
        ])

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        filename = self.files[idx]
        label = int(filename.split("_")[0])  # Extract label from filename
        image = Image.open(os.path.join(self.root_dir, filename))
        image = self.transform(image)
        return image, label

# **🔹 Updated Model with Correct Flattening**
class DigitClassifier(nn.Module):
    def __init__(self):
        super(DigitClassifier, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

        # Compute final feature map size: 64x64 → (after pooling) → 16x16
        self.fc1 = nn.Linear(64 * 16 * 16, 256)  # **Fixed Incorrect Size**
        self.fc2 = nn.Linear(256, 10)  # 10 output classes

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))

        x = x.view(x.shape[0], -1)  # **Flatten Properly**
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Training Function
def train_model(epochs=7, learning_rate=0.0005):
    dataset = DigitDataset(dataset_path)
    dataloader = DataLoader(dataset, batch_size=16, shuffle=True)

    model = DigitClassifier()
    device = torch.device("cpu")
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    print("Starting training...")
    for epoch in range(epochs):
        epoch_loss = 0
        correct = 0
        total = 0
        for images, labels in dataloader:
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

            # Calculate accuracy
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        accuracy = 100 * correct / total
        print(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss:.4f}, Accuracy: {accuracy:.2f}%")
    
    
    #save model in the trained_models directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
    save_dir = os.path.join(project_root, 'trained_models/digit_classification')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, 'trained_model.pth')
    torch.save(model.state_dict(), save_path)

    print("Training complete. Model saved as 'trained_model.pth'.")
    return epoch_loss, accuracy

# Run the Training Process
if __name__ == "__main__":
    train_model()