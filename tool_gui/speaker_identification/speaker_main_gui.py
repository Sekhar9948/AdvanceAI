
import customtkinter as ctk
import pyaudio
import numpy as np
import threading
import time
import wave
import os
import librosa
import torch
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
import torch.optim as optim
import threading
import time
import json

import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from language_manager import LanguageManager

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
model_path = os.path.join(project_root, 'trained_models','speaker_identification')
dataset_path = os.path.join(project_root, 'dataset','speaker_identification')

class SpeakerIDApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.translator = LanguageManager()
        self.translator.load_language("en")

        self.title(self.translator.get("speaker_identification_title"))
        self.geometry("800x500")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Layout Frames
        self.left_frame = ctk.CTkFrame(self, width=250, corner_radius=10)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.right_frame = ctk.CTkFrame(self, corner_radius=10)
        self.right_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        # Left Panel - Recording Controls
        self.speaker_label = ctk.CTkLabel(self.left_frame, text="Speaker Name:")
        self.speaker_label.pack(pady=(20, 5))

        self.speaker_entry = ctk.CTkEntry(self.left_frame)
        self.speaker_entry.pack(pady=5)

        self.record_button = ctk.CTkButton(self.left_frame, text="Start Recording", command=self.start_recording)
        self.record_button.pack(pady=10)

        # Extract Data Button
        self.extract_button = ctk.CTkButton(self.left_frame, text="Extract Data", command=self.extract_data, fg_color="yellow", text_color="black")
        self.extract_button.pack(pady=10)

        # Timer Label
        self.timer_label = ctk.CTkLabel(self.left_frame, text="Recording Time: 0s", font=("Arial", 14))
        self.timer_label.pack(pady=10)

        # Separator Line
        self.separator = ctk.CTkFrame(self.left_frame, height=2, fg_color="gray")
        self.separator.pack(fill="x", pady=15)

        # Learning Rate Input
        self.lr_label = ctk.CTkLabel(self.left_frame, text="Learning Rate:")
        self.lr_label.pack(pady=(10, 2))
        self.lr_entry = ctk.CTkEntry(self.left_frame)
        self.lr_entry.pack(pady=5)

        # Epochs Input
        self.epochs_label = ctk.CTkLabel(self.left_frame, text="Epochs:")
        self.epochs_label.pack(pady=(10, 2))
        self.epochs_entry = ctk.CTkEntry(self.left_frame)
        self.epochs_entry.pack(pady=5)

        # Train Model Button
        self.train_button = ctk.CTkButton(self.left_frame, text="Train Model", fg_color="green", command=self.train_model)
        self.train_button.pack(pady=15)

        # Progress bar (Initially hidden)
        self.progress_bar = ctk.CTkProgressBar(self.left_frame)
        self.progress_bar.set(0)  # Start at 0%
        self.progress_bar.pack(pady=15)
        self.progress_bar.pack_forget()  # Hide initially

        # Label for Loss & Accuracy
        self.result_label = ctk.CTkLabel(self.left_frame, text="", font=("Arial", 14))
        self.result_label.pack(pady=5)

        # Right Panel - Waveform Display (Strip)
        self.waveform_frame = ctk.CTkFrame(self.right_frame, height=100, corner_radius=10)
        self.waveform_frame.pack(fill="x", padx=10, pady=10)

        # Detection Button (Orange, full width)
        self.detect_button = ctk.CTkButton(self.right_frame, text="Detect Speaker", command=lambda: threading.Thread(target=self.detect_speaker).start(), fg_color="orange", text_color="black", height=40)
        self.detect_button.pack(pady=30, padx=50, fill="x")

        # Prediction Result Label (big font, centered below detect button)
        self.prediction_label = ctk.CTkLabel(self.right_frame, text="", font=("Arial", 24))
        self.prediction_label.pack(pady=20)

        
        self.figure, self.ax = plt.subplots(figsize=(5, 1.2), dpi=100)
        self.ax.set_ylim(-1, 1)
        self.ax.set_xlim(0, 1024)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.line, = self.ax.plot(np.zeros(1024), 'c')

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.waveform_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.recording = False
        self.audio_thread = None
        self.start_time = None
        self.audio_frames = []
        self.audio_stream = None
        self.audio = pyaudio.PyAudio()
        self.clip_count = 1

    def detect_speaker(self):
        """Records a new audio clip and uses the trained model to predict the speaker."""
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        SECONDS = 3
        FRAMES = []

        # Open stream and record
        stream = self.audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        self.result_label.configure(text="Listening...")
        for _ in range(0, int(RATE / CHUNK * SECONDS)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            FRAMES.append(data)
            normalized_data = np.frombuffer(data, dtype=np.int16) / 32768.0
            self.line.set_ydata(normalized_data)
            self.canvas.draw()

        stream.stop_stream()
        stream.close()
        self.result_label.configure(text="Processing...")

        # Save temporary clip
        os.makedirs("temp", exist_ok=True)
        path = "temp/temp_clip.wav"
        with wave.open(path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(FRAMES))

        # Extract MFCC
        y, sr = librosa.load(path, sr=16000)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        delta = librosa.feature.delta(mfcc)
        delta2 = librosa.feature.delta(mfcc, order=2)
        features_stack = np.vstack([mfcc, delta, delta2])
        mean = np.mean(features_stack, axis=1)
        std = np.std(features_stack, axis=1)
        features = np.concatenate([mean, std])  # Shape: (120,)


        features = torch.tensor(features, dtype=torch.float32).unsqueeze(0)  # (1, 120)

        # Load model and run inference
        class SpeakerIDModel(nn.Module):
            def __init__(self):
                super(SpeakerIDModel, self).__init__()
                self.fc1 = nn.Linear(78, 32)
                self.fc2 = nn.Linear(32, 16)
                self.fc3 = nn.Linear(16, 2)

            def forward(self, x):
                x = torch.relu(self.fc1(x))
                x = torch.relu(self.fc2(x))
                return self.fc3(x)

        model = SpeakerIDModel()

        load_path = os.path.join(model_path, 'speaker_model.pth')
        model.load_state_dict(torch.load(load_path))
        model.eval()

        with torch.no_grad():
            output = model(features)
            prediction = torch.argmax(output, dim=1).item()

        # Mapping speaker names from file names
        with open("label_map.json") as f:
            label_map = json.load(f)
        
        reverse_map = {v: k for k, v in label_map.items()}


        # Use prediction index to get speaker name
        detected_name = reverse_map.get(prediction, "Unknown")


        # Update label with detected name
        self.prediction_label.configure(text=f"Detected: {detected_name}")
        self.result_label.configure(text=f"Prediction complete.")
        # print(f"Detected speaker: {detected_name}")


    def train_model(self):
        """Trains a neural network using the extracted MFCC features."""
        try:
            learning_rate = float(self.lr_entry.get().strip())
            epochs = int(self.epochs_entry.get().strip())
        except ValueError:
            print("Invalid learning rate or epoch input. Please enter valid numbers.")
            return

        # Load dataset
        x_load = f'{dataset_path}/X.npy'
        y_load = f'{dataset_path}/Y.npy'
        X = np.load(x_load)
        y = np.load(y_load)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Convert to PyTorch tensors
        X_train = torch.tensor(X_train, dtype=torch.float32)
        y_train = torch.tensor(y_train, dtype=torch.long)
        X_test = torch.tensor(X_test, dtype=torch.float32)
        y_test = torch.tensor(y_test, dtype=torch.long)

        # Define a simple neural network
        class SpeakerIDModel(nn.Module):
            def __init__(self):
                super(SpeakerIDModel, self).__init__()
                self.fc1 = nn.Linear(78, 32)
                self.fc2 = nn.Linear(32, 16)
                self.fc3 = nn.Linear(16, 2)  # 2 output classes (speaker_1 or other)
            
            def forward(self, x):
                x = torch.relu(self.fc1(x))
                x = torch.relu(self.fc2(x))
                return self.fc3(x)

        model = SpeakerIDModel()
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=learning_rate)

        # Training loop
        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = model(X_train)
            loss = criterion(outputs, y_train)
            loss.backward()
            optimizer.step()
            if epoch % 10 == 0:
                print(f"Epoch {epoch}, Loss: {loss.item()}")

        # Evaluate model accuracy
        with torch.no_grad():
            test_outputs = model(X_test)
            predicted = torch.argmax(test_outputs, dim=1)
            accuracy = (predicted == y_test).sum().item() / len(y_test)

        # Save model
        save_path = os.path.join(model_path, 'speaker_model.pth')
        torch.save(model.state_dict(), save_path)
        print("Model training complete and saved.")

        # Start progress bar in a separate thread
        self.progress_bar.pack()  # Show progress bar
        threading.Thread(target=self.fill_progress_bar, args=(loss.item(), accuracy)).start()

    def fill_progress_bar(self, final_loss, final_accuracy):
        """Fills the progress bar over 10 seconds and displays loss & accuracy."""
        for i in range(101):  # 0% to 100%
            self.progress_bar.set(i / 100)
            time.sleep(0.1)  # 10 seconds total
        
        # Show final loss and accuracy
        self.result_label.configure(text=f"Loss: {final_loss:.4f}, Accuracy: {final_accuracy:.2%}")


    def start_recording(self):
        if not self.recording:
            self.recording = True
            self.record_button.configure(text="Stop Recording", fg_color="red")
            self.start_time = time.time()
            self.clip_count = 1  # Reset clip count
            self.audio_frames = []
            self.update_timer()
            self.audio_thread = threading.Thread(target=self.record_audio)
            self.audio_thread.start()
        else:
            self.recording = False
            self.record_button.configure(text="Start Recording", fg_color="blue")
            self.audio_stream.stop_stream()
            self.audio_stream.close()

    def update_timer(self):
        """Updates the timer label while recording is active."""
        if self.recording:
            elapsed_time = int(time.time() - self.start_time)
            self.timer_label.configure(text=f"Recording Time: {elapsed_time}s")
            self.after(1000, self.update_timer)

    def record_audio(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        SECONDS_PER_CLIP = 10
        CLIP_SIZE = RATE * SECONDS_PER_CLIP // CHUNK  # Number of chunks per clip

        self.audio_stream = self.audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

        while self.recording:
            clip_frames = []
            for _ in range(CLIP_SIZE):
                if not self.recording:
                    break
                data = self.audio_stream.read(CHUNK, exception_on_overflow=False)
                clip_frames.append(data)
                normalized_data = np.frombuffer(data, dtype=np.int16) / 32768.0
                self.line.set_ydata(normalized_data)
                self.canvas.draw()

            if clip_frames:
                self.save_audio_clip(clip_frames)

    def save_audio_clip(self, frames):
        """Saves each 5-second audio clip immediately upon recording."""
        speaker_name = self.speaker_entry.get().strip()
        if not speaker_name:
            speaker_name = "unknown"

        filename = f"{dataset_path}/{speaker_name}_{self.clip_count}.wav"
        os.makedirs(dataset_path, exist_ok=True)

        RATE = 44100
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

        print(f"Saved: {filename}")
        self.clip_count += 1

    def extract_data(self):
        """Extracts features from saved audio files and saves them as X.npy and y.npy."""
        self.extract_button.configure(fg_color="green", text="Extracting...")  # Change color to green
        self.update()  # Force GUI to update immediately

        def extract_features(file_path, sample_rate=16000):
            y, sr = librosa.load(file_path, sr=sample_rate)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            delta = librosa.feature.delta(mfcc)
            delta2 = librosa.feature.delta(mfcc, order=2)
            features = np.vstack([mfcc, delta, delta2])
            mean = np.mean(features, axis=1)
            std = np.std(features, axis=1)
            return np.concatenate([mean, std])  # Shape: (120,)



        def prepare_data(directory=dataset_path):
            X, y = [], []
            speaker_names = sorted({f.split("_")[0] for f in os.listdir(directory) if f.endswith(".wav")})
            label_map = {name: idx for idx, name in enumerate(speaker_names)}
            print("Label Map:", label_map)

            for file in os.listdir(directory):
                if file.endswith(".wav"):
                    speaker_name = file.split("_")[0]
                    label = label_map[speaker_name]
                    features = extract_features(os.path.join(directory, file))
                    X.append(features)
                    y.append(label)

            with open("label_map.json", "w") as f:
                json.dump(label_map, f)
            
            return np.array(X), np.array(y)


        X, Y = prepare_data()
        np.save(f"{dataset_path}/X.npy", X)
        np.save(f"{dataset_path}/Y.npy", Y)
        print("Data saved for training.")

        self.extract_button.configure(fg_color="yellow", text="Extract Data")  # Revert back after extraction


# Run the app
if __name__ == "__main__":
    app = SpeakerIDApp()
    app.mainloop()