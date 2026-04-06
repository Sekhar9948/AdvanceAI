
import customtkinter as ctk
import cv2
import mediapipe as mp
import csv
import os
from PIL import Image, ImageTk
import subprocess
import threading
import joblib

import sys

import warnings
warnings.filterwarnings("ignore")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from language_manager import LanguageManager

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
 
model_path = os.path.join(project_root, 'trained_models','hand_gesture_detection', 'gesture_model.pkl')
dataset_path = os.path.join(project_root, 'dataset','hand_data','hand_gesture_data.csv')

# Load trained model
clf = joblib.load(model_path)

# Initialize main window
app = ctk.CTk()


translator = LanguageManager()
translator.load_language("en")  # or from config

app.title(translator.get("gesture_title"))
app.geometry("800x600")

# Configure grid layout
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=2)
app.grid_rowconfigure(0, weight=1)
app.grid_rowconfigure(1, weight=1)

# Global variables
detecting = False
cap = None
collecting = False
gesture_labels = ["Fist", "Open Palm", "Thumbs Up", "Thumbs Down", "Victory"]
gesture_index = 0
frame_count = 0
max_frames = 500

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

# Open CSV file in append mode
file_exists = os.path.exists(dataset_path)
f = open(dataset_path, mode="a", newline="")
writer = csv.writer(f)

# Write header if file is new
if not file_exists:
    writer.writerow(["label"] + [f"x{i}" for i in range(21)] + [f"y{i}" for i in range(21)])

# Function to update the right-side webcam feed
def update_main_webcam():
    global cap, detecting

    if cap is not None and detecting:
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Extract landmarks for model prediction
                    landmarks = [lm.x for lm in hand_landmarks.landmark] + [lm.y for lm in hand_landmarks.landmark]

                    if len(landmarks) == 42:  # Ensure valid input for model
                        prediction = clf.predict([landmarks])
                        label = gesture_labels[prediction[0]]

                        # Display prediction on frame
                        cv2.putText(frame, label, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Convert frame to Tkinter-compatible format
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            main_webcam_label.imgtk = imgtk
            main_webcam_label.configure(image=imgtk)

    # Ensure the function updates continuously
    if detecting:
        main_webcam_label.after(10, update_main_webcam)


# Function to start detection and open the right-side webcam
def start_detection():
    global cap, detecting
    if cap is None:
        cap = cv2.VideoCapture(0)
    detecting = True
    update_main_webcam()


# Function to update the left-side webcam feed
def update_webcam():
    global cap, frame_count, collecting, gesture_index

    if cap is not None:
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    if collecting and frame_count < max_frames:
                        landmarks = [lm.x for lm in hand_landmarks.landmark] + [lm.y for lm in hand_landmarks.landmark]
                        writer.writerow([gesture_labels[gesture_index]] + landmarks)
                        frame_count += 1

            overlay_text = f"Gesture: {gesture_labels[gesture_index]} ({frame_count}/{max_frames})"
            cv2.putText(frame, overlay_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            top_webcam_label.imgtk = imgtk
            top_webcam_label.configure(image=imgtk)

        top_webcam_label.after(10, update_webcam)

# Function to open webcam for data collection
def open_webcam():
    global cap
    if cap is None:
        cap = cv2.VideoCapture(0)
        update_webcam()

# Function to close webcam
def close_webcam():
    global cap
    if cap is not None:
        cap.release()
        cap = None
        top_webcam_label.configure(image=None)
        main_webcam_label.configure(image=None)
        status_label.configure(text=translator.get("webcam_closed"))

# Function to start recording
def start_recording():
    toggle_collection()

# Function to toggle gesture data collection
def toggle_collection():
    global collecting, frame_count, max_frames
    collecting = not collecting
    if collecting:
        frame_count = 0
        try:
            max_frames = int(frames_entry.get())
        except ValueError:
            max_frames = 500
    status_label.configure(
        text=f"{translator.get('recording')}: {gesture_labels[gesture_index]}"
    )

# Function to switch gesture
def next_gesture():
    global gesture_index, frame_count
    gesture_index = (gesture_index + 1) % len(gesture_labels)
    frame_count = 0
    status_label.configure(
        text=f"{translator.get('gesture')}: {gesture_labels[gesture_index]}"
    )

# Function to train model
def train_model():
    train_button.configure(state="disabled")
    progress_bar.set(0)

    n_estimators = n_estimator_entry.get()
    max_depth = max_depth_entry.get()

    def run_training():
        subprocess.run(["python", "tool_gui\hand_gesture\gesture_train_model.py", n_estimators, max_depth])
        progress_bar.set(1)
        train_button.configure(state="normal")

    threading.Thread(target=run_training).start()

# Function to handle key presses
def key_press(event):
    if event.char.lower() == 'c':
        toggle_collection()
        
def stop_detection():
    global cap, detecting
    detecting = False
    if cap is not None and cap.isOpened():
        cap.release()
        cap = None
    main_webcam_label.configure(image=None)  # Clear webcam feed

# Right column - Main webcam view
right_frame = ctk.CTkFrame(app, corner_radius=10)
right_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)
right_frame.grid_rowconfigure(0, weight=1)
right_frame.grid_columnconfigure(0, weight=1)

main_webcam_label = ctk.CTkLabel(right_frame, text=translator.get("main_webcam_view"), width=400, height=300)
main_webcam_label.grid(row=0, column=0, padx=10, pady=10)

start_button = ctk.CTkButton(right_frame, text=translator.get("start_detection"), command=start_detection)
start_button.grid(row=1, column=0, padx=10, pady=10)

stop_button = ctk.CTkButton(right_frame, text=translator.get("stop_detection"), command=stop_detection)
stop_button.grid(row=2, column=0, padx=5, pady=10)

# Left column - Webcam controls
left_top_frame = ctk.CTkFrame(app, corner_radius=10)
left_top_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
left_top_frame.grid_rowconfigure(0, weight=1)
left_top_frame.grid_columnconfigure(0, weight=1)

top_webcam_label = ctk.CTkLabel(left_top_frame, text=translator.get("top_webcam_view"), width=200, height=150)
top_webcam_label.grid(row=0, column=0, padx=10, pady=10)

open_button = ctk.CTkButton(left_top_frame, text=translator.get("open"), command=open_webcam)
open_button.grid(row=1, column=0, padx=10, pady=10)

start_recording_button = ctk.CTkButton(left_top_frame,  text=translator.get("start_recording"), command=start_recording)
start_recording_button.grid(row=2, column=0, padx=10, pady=10)

close_button = ctk.CTkButton(left_top_frame, text=translator.get("close"), command=close_webcam)
close_button.grid(row=3, column=0, padx=10, pady=10)

status_label = ctk.CTkLabel(left_top_frame, text=translator.get("idle"), width=200)
status_label.grid(row=4, column=0, padx=10, pady=5)

switch_button = ctk.CTkButton(left_top_frame, text=translator.get("next_gesture"), command=next_gesture)
switch_button.grid(row=5, column=0, padx=10, pady=10)

frames_entry = ctk.CTkEntry(left_top_frame, placeholder_text=translator.get("number_of_frames"), width=100)
frames_entry.insert(0, "500")
frames_entry.grid(row=6, column=0, padx=10, pady=10)

# Bottom row - Training section
left_bottom_frame = ctk.CTkFrame(app, corner_radius=10)
left_bottom_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

n_estimator_entry = ctk.CTkEntry(left_bottom_frame, placeholder_text=translator.get("n_estimators"), width=100)
n_estimator_entry.insert(0, "100")
n_estimator_entry.grid(row=0, column=0, padx=10, pady=10)

max_depth_entry = ctk.CTkEntry(left_bottom_frame, placeholder_text=translator.get("max_depth"), width=100)
max_depth_entry.insert(0, "10")
max_depth_entry.grid(row=0, column=1, padx=10, pady=10)

train_button = ctk.CTkButton(left_bottom_frame,  text=translator.get("train_model"), command=train_model)
train_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

progress_bar = ctk.CTkProgressBar(left_bottom_frame, width=200)
progress_bar.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
progress_bar.set(0)

app.bind("<Key>", key_press)
app.mainloop()