
import customtkinter as ctk
import cv2
import numpy as np
import tensorflow as tf
import os
from PIL import Image, ImageTk
import threading
import queue
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import collections

import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from language_manager import LanguageManager

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
model_path1 = os.path.join(project_root, 'trained_models','emotion_detection', 'emotion_model.tflite')
dataset_path = os.path.join(project_root, 'dataset','emotion_detection')


class EmotionDetectionUI:
    def __init__(self):
        # Set theme and color scheme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.translator = LanguageManager()
        self.translator.load_language("en")  # or config

        
        # Initialize main window
        self.root = ctk.CTk()
        self.root.title(self.translator.get("emotion_title"))
        self.root.geometry("1280x720")
        
        # Initialize variables
        self.cap = None
        self.is_capturing = False
        self.is_training = False
        self.is_inferring = False
        self.current_emotion = "happy"
        self.img_count = 0
        self.emotions = ["happy", "sad", "neutral"]
        self.base_dir = dataset_path
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Create main layout
        self.setup_ui()
        
        # Initialize queues for thread communication
        self.frame_queue = queue.Queue()
        self.status_queue = queue.Queue()
        
        # Start status update thread
        self.status_thread = threading.Thread(target=self.update_status_loop, daemon=True)
        self.status_thread.start()
        
    def setup_ui(self):
        # Create main container
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create left and right panels
        self.left_panel = ctk.CTkFrame(self.main_container, width=400)
        self.left_panel.pack(side="left", fill="y", padx=5, pady=5)
        
        self.right_panel = ctk.CTkFrame(self.main_container)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Setup left panel (controls)
        self.setup_left_panel()
        
        # Setup right panel (display)
        self.setup_right_panel()
        
    def setup_left_panel(self):
        # Title
        title_label = ctk.CTkLabel(
            self.left_panel,
            text=self.translator.t("Emotion Detection System"),
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=20)
        
        # Data Collection Section
        self.create_section_label("Data Collection")
        
        # Emotion selection
        emotion_frame = ctk.CTkFrame(self.left_panel)
        emotion_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(emotion_frame, text="Select Emotion:").pack(side="left", padx=5)
        self.emotion_var = ctk.StringVar(value="happy")
        emotion_menu = ctk.CTkOptionMenu(
            emotion_frame,
            values=self.emotions,
            variable=self.emotion_var,
            command=self.on_emotion_change
        )
        emotion_menu.pack(side="right", padx=5)
        
        # Sample count display
        self.sample_count_label = ctk.CTkLabel(
            self.left_panel,
            text="Samples: 0/500",
            font=("Arial", 14)
        )
        self.sample_count_label.pack(pady=5)
        
        # Capture button
        self.capture_btn = ctk.CTkButton(
            self.left_panel,
            text=self.translator.t("Start Capturing"),
            command=self.toggle_capture,
            width=200
        )
        self.capture_btn.pack(pady=10)
        
        # Training Section
        self.create_section_label("Model Training")
        
        # Training status
        self.training_status = ctk.CTkLabel(
            self.left_panel,
            text=self.translator.t("Not Training"),
            font=("Arial", 14)
        )
        self.training_status.pack(pady=5)
        
        # Training progress
        self.training_progress = ctk.CTkProgressBar(self.left_panel)
        self.training_progress.pack(fill="x", padx=10, pady=5)
        self.training_progress.set(0)
        
        # Train button
        self.train_btn = ctk.CTkButton(
            self.left_panel,
            text=self.translator.t("Train Model"),
            command=self.toggle_training,
            width=200
        )
        self.train_btn.pack(pady=10)
        
        # Inference Section
        self.create_section_label("Real-time Inference")
        
        # Confidence threshold
        threshold_frame = ctk.CTkFrame(self.left_panel)
        threshold_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(threshold_frame, text="Confidence:").pack(side="left", padx=5)
        self.confidence_var = ctk.DoubleVar(value=40.0)
        confidence_slider = ctk.CTkSlider(
            threshold_frame,
            from_=0,
            to=100,
            variable=self.confidence_var,
            command=self.update_confidence
        )
        confidence_slider.pack(side="right", fill="x", expand=True, padx=5)
        
        # Inference button
        self.inference_btn = ctk.CTkButton(
            self.left_panel,
            text=self.translator.t("Start Inference"),
            command=self.toggle_inference,
            width=200
        )
        self.inference_btn.pack(pady=10)
        
        # Status section
        self.create_section_label("System Status")
        
        # Status display
        self.status_label = ctk.CTkLabel(
            self.left_panel,
            text="Ready",
            font=("Arial", 14)
        )
        self.status_label.pack(pady=5)
        
        # FPS counter
        self.fps_label = ctk.CTkLabel(
            self.left_panel,
            text="FPS: 0",
            font=("Arial", 14)
        )
        self.fps_label.pack(pady=5)
        
    def setup_right_panel(self):
        # Create video display frame
        self.video_frame = ctk.CTkFrame(self.right_panel)
        self.video_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create video label
        self.video_label = ctk.CTkLabel(self.video_frame, text="")
        self.video_label.pack(fill="both", expand=True)
        
        # Create emotion distribution plot
        self.fig, self.ax = plt.subplots(figsize=(6, 2))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_panel)
        self.canvas.get_tk_widget().pack(fill="x", padx=10, pady=5)
        
        # Initialize plot
        self.update_emotion_plot()
        
    def create_section_label(self, text):
        label = ctk.CTkLabel(
            self.left_panel,
            text=text,
            font=("Arial", 16, "bold")
        )
        label.pack(pady=(20, 10))
        
    def on_emotion_change(self, choice):
        self.current_emotion = choice
        self.img_count = 0
        self.update_sample_count()
        
    def update_sample_count(self):
        self.sample_count_label.configure(text=f"Samples: {self.img_count}/500")
        
    def update_confidence(self, value):
        self.confidence_var.set(value)
        
    def update_status_loop(self):
        while True:
            try:
                status = self.status_queue.get(timeout=0.1)
                self.status_label.configure(text=status)
            except queue.Empty:
                continue
                
    def update_emotion_plot(self):
        self.ax.clear()
        self.ax.bar(self.emotions, [0] * len(self.emotions))
        self.ax.set_title("Emotion Distribution")
        self.ax.set_ylim(0, 100)
        self.canvas.draw()
        
    def toggle_capture(self):
        if not self.is_capturing:
            self.start_capture()
        else:
            self.stop_capture()
            
    def start_capture(self):
        self.is_capturing = True
        self.capture_btn.configure(text="Stop Capturing")
        self.status_queue.put("Capturing data...")
        
        # Start capture thread
        self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
        self.capture_thread.start()
        
    def stop_capture(self):
        self.is_capturing = False
        self.capture_btn.configure(text="Start Capturing")
        self.status_queue.put("Capture stopped")
        
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            
    def capture_loop(self):
        self.cap = cv2.VideoCapture(0)
        start_time = time.time()
        frame_count = 0
        
        while self.is_capturing:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            # Calculate FPS
            frame_count += 1
            if frame_count >= 10:
                fps = 10 / (time.time() - start_time)
                self.fps_label.configure(text=f"FPS: {fps:.1f}")
                start_time = time.time()
                frame_count = 0
            
            # Process frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
            
            # Draw face detection
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            # Save frame if capturing
            if self.is_capturing and len(faces) > 0:
                x, y, w, h = faces[0]
                if w > 100 and h > 100:
                    face_img = frame[y:y+h, x:x+w]
                    enhanced_face = self.enhance_face(face_img)
                    resized_face = cv2.resize(enhanced_face, (48, 48))
                    
                    os.makedirs(os.path.join(self.base_dir, self.current_emotion), exist_ok=True)
                    img_path = os.path.join(self.base_dir, self.current_emotion, f"{self.img_count}.jpg")
                    cv2.imwrite(img_path, resized_face)
                    
                    self.img_count += 1
                    self.update_sample_count()
                    
                    if self.img_count >= 500:
                        self.stop_capture()
                        self.status_queue.put(f"Captured 500 images for {self.current_emotion}")
                        break
            
            # Update display
            self.update_video_display(frame)
            
    def enhance_face(self, face):
        lab = cv2.cvtColor(face, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        updated_lab = cv2.merge((cl, a, b))
        enhanced_face = cv2.cvtColor(updated_lab, cv2.COLOR_LAB2BGR)
        return enhanced_face
        
    def update_video_display(self, frame):
        # Convert frame to PhotoImage
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        frame_tk = ImageTk.PhotoImage(image=frame_pil)
        
        # Update label
        self.video_label.imgtk = frame_tk  # prevents garbage collection
        self.video_label.configure(image=frame_tk)

        
    def toggle_training(self):
        if not self.is_training:
            self.start_training()
        else:
            self.stop_training()
            
    def start_training(self):
        self.is_training = True
        self.train_btn.configure(text="Stop Training")
        self.status_queue.put("Training model...")
        
        # Start training thread
        self.training_thread = threading.Thread(target=self.training_loop, daemon=True)
        self.training_thread.start()
        
    def stop_training(self):
        self.is_training = False
        self.train_btn.configure(text="Train Model")
        self.status_queue.put("Training stopped")
        
    def training_loop(self):
        try:
            # Import training code
            import emotion_train_model 
            # The training code runs automatically when imported
            # No need to call a specific function
            
            self.status_queue.put("Training completed")
            self.is_training = False
            self.train_btn.configure(text="Train Model")
            
        except Exception as e:
            self.status_queue.put(f"Training error: {str(e)}")
            self.is_training = False
            self.train_btn.configure(text="Train Model")
            
    def toggle_inference(self):
        if not self.is_inferring:
            self.start_inference()
        else:
            print("Stop Inference button clicked")
            self.stop_inference()
            
    def start_inference(self):
        print("Start Inference button clicked")
        self.is_inferring = True
        self.inference_btn.configure(text="Stop Inference")
        self.status_queue.put("Starting inference...")
        
        # Check if model file exists
        if not os.path.exists(model_path1):
            print("Model file not found")
            self.status_queue.put("Error: Model file not found. Please train the model first.")
            self.stop_inference()
            return
            
        # Load model
        try:
            print("Model loaded")
            self.interpreter = tf.lite.Interpreter(model_path=model_path1)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            # Verify input shape
            input_shape = self.input_details[0]['shape']
            print(input_shape[1:])
            if tuple(input_shape[1:]) != (48, 48, 3):
                print("Model input shape mismatch")
                self.status_queue.put("Error: Model input shape mismatch")
                self.stop_inference()
                return
            print("Input shape verified")
            # Start inference thread
            self.inference_thread = threading.Thread(target=self.inference_loop, daemon=True)
            self.inference_thread.start()
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            self.status_queue.put(f"Error loading model: {str(e)}")
            self.stop_inference()
            
    def stop_inference(self):
        self.is_inferring = False
        self.inference_btn.configure(text="Start Inference")
        self.status_queue.put("Inference stopped")
        
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            
        # Reset emotion plot
        self.update_emotion_plot()
        
    def inference_loop(self):
        print("Inference loop started")
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Could not open camera")
            self.status_queue.put("Error: Could not open camera")
            self.stop_inference()
            return
            
        start_time = time.time()
        frame_count = 0
        prediction_history = {}
        HISTORY_LENGTH = 30
        
        while self.is_inferring:
            ret, frame = self.cap.read()
            if not ret:
                self.status_queue.put("Error: Failed to read frame")
                break
                
            # Calculate FPS
            frame_count += 1
            if frame_count >= 10:
                fps = 10 / (time.time() - start_time)
                self.fps_label.configure(text=f"FPS: {fps:.1f}")
                start_time = time.time()
                frame_count = 0
            
            # Process frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
            
            # Process each face
            for (x, y, w, h) in faces:
                try:
                    face_roi = frame[y:y+h, x:x+w]
                    face_resized = cv2.resize(face_roi, (48, 48))
                    face_normalized = face_resized / 255.0
                    face_input = np.expand_dims(face_normalized, axis=0).astype(np.float32)
                    
                    # Run inference
                    self.interpreter.set_tensor(self.input_details[0]['index'], face_input)
                    self.interpreter.invoke()
                    output = self.interpreter.get_tensor(self.output_details[0]['index'])
                    
                    # Process prediction
                    face_id = f"{x}_{y}"
                    if face_id not in prediction_history:
                        prediction_history[face_id] = collections.deque(maxlen=HISTORY_LENGTH)
                    
                    prediction_history[face_id].append(output[0])
                    
                    if len(prediction_history[face_id]) >= 5:
                        # Apply weighted average
                        weights = np.exp(np.linspace(0, 1, len(prediction_history[face_id])))
                        weights = weights / weights.sum()
                        
                        weighted_predictions = []
                        for i, pred in enumerate(prediction_history[face_id]):
                            weighted_predictions.append(pred * weights[i])
                        
                        avg_prediction = np.sum(weighted_predictions, axis=0)
                        emotion_idx = np.argmax(avg_prediction)
                        confidence = float(avg_prediction[emotion_idx]) * 100
                        
                        if confidence > self.confidence_var.get():
                            emotion = self.emotions[emotion_idx].capitalize()
                            color = (0, 255, 0) if emotion.lower() == "happy" else \
                                   (0, 0, 255) if emotion.lower() == "sad" else \
                                   (255, 255, 0)
                            
                            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                            label = f"{emotion} ({confidence:.1f}%)"
                            cv2.putText(frame, label, (x, y - 10),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                            
                            # Update emotion plot
                            self.ax.clear()
                            self.ax.bar(self.emotions, avg_prediction * 100)
                            self.ax.set_title("Emotion Distribution")
                            self.ax.set_ylim(0, 100)
                            self.canvas.draw()
                except Exception as e:
                    print(f"Error processing face: {str(e)}")
                    continue
            
            # Update display
            self.update_video_display(frame)
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = EmotionDetectionUI()
    app.run()