
import pandas as pd
import re
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from imblearn.under_sampling import RandomUnderSampler
from sklearn.naive_bayes import MultinomialNB
import threading
import queue
import customtkinter as ctk
import os

import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from language_manager import LanguageManager

nltk.download('stopwords')

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
dataset_path = os.path.join(project_root, 'dataset','spam_classification','SMSSpamCollection')


# ---------------------------- #
#  Text Classification Functions #
# ---------------------------- #

def preprocess_messages(messages):
    stemmer = PorterStemmer()
    cleaned = []
    for msg in messages:
        msg = re.sub('[^a-zA-Z]', ' ', msg)
        msg = msg.lower().split()
        msg = [stemmer.stem(word) for word in msg if word not in set(stopwords.words('english'))]
        cleaned.append(' '.join(msg))
    return cleaned

def train_spam_ham_model(file_path, num_samples=None, n_iterations=100):
    df = pd.read_csv(file_path, sep='\t', names=['labels', 'messages'])
    
    if num_samples is not None and num_samples < len(df):
        df = df.sample(n=num_samples, random_state=42)
    
    messages = preprocess_messages(df['messages'])
    vectorizer = CountVectorizer(max_features=5000)
    X = vectorizer.fit_transform(messages).toarray()
    y = pd.get_dummies(df['labels'])['spam'].values  # 1 for spam, 0 for ham
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    X_train, y_train = RandomUnderSampler(random_state=42).fit_resample(X_train, y_train)
    
    model = MultinomialNB()
    # Train the model
    model.fit(X_train, y_train)
    
    return (model, vectorizer)

def predict_label(model_tuple, text):
    model, vectorizer = model_tuple
    stemmer = PorterStemmer()
    words = re.sub('[^a-zA-Z]', ' ', text).lower().split()
    words = [stemmer.stem(word) for word in words if word not in set(stopwords.words('english'))]
    processed = ' '.join(words)
    vectorized = vectorizer.transform([processed]).toarray()
    prob = model.predict_proba(vectorized)[0]
    label = 'spam' if prob[1] > prob[0] else 'ham'
    confidence = max(prob)
    return label, confidence

# ---------------------------- #
#      CustomTkinter UI        #
# ---------------------------- #

class TextClassificationGUI:
    def __init__(self):
        # Set appearance and theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.translator = LanguageManager()
        self.translator.load_language("en")
        
        # Main window settings
        self.root = ctk.CTk()
        self.root.title(self.translator.get("sms_spam_title"))
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Queue to hold the trained model once ready
        self.model_queue = queue.Queue()
        self.model = None  # Will store (model, vectorizer)
        
        # Training parameters variables
        self.num_samples = ctk.StringVar(value="5000")
        self.num_iterations = ctk.StringVar(value="50")
        
        # Status variable
        self.train_status = ctk.StringVar(value="Model not trained")
        
        # Build main container and grid
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)
        
        # Create UI sections
        self.create_header()
        self.create_content_area()
        
    def create_header(self):
        header_frame = ctk.CTkFrame(self.main_container)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0,20))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="SMS Spam Detection",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        desc_label = ctk.CTkLabel(
            header_frame,
            text="Configure the model, train and test with text input",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        desc_label.grid(row=1, column=0)
        
    def create_content_area(self):
        content_frame = ctk.CTkFrame(self.main_container)
        content_frame.grid(row=1, column=0, sticky="nsew")
        # Configure grid: left panel for configuration, right panel for input/results
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=2)
        content_frame.grid_rowconfigure(0, weight=1)
        
        self.create_config_section(content_frame)
        self.create_input_section(content_frame)
        
    def create_config_section(self, parent):
        config_frame = ctk.CTkFrame(parent)
        config_frame.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        config_frame.grid_columnconfigure(0, weight=1)
        
        # Configuration Title
        config_title = ctk.CTkLabel(
            config_frame,
            text="Model Configuration",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        config_title.grid(row=0, column=0, pady=(20,20))
        
        # Number of Samples
        samples_frame = ctk.CTkFrame(config_frame)
        samples_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0,10))
        samples_frame.grid_columnconfigure(1, weight=1)
        samples_label = ctk.CTkLabel(samples_frame, text="Number of Samples:", font=ctk.CTkFont(size=14))
        samples_label.grid(row=0, column=0, sticky="w", padx=(0,10))
        samples_entry = ctk.CTkEntry(samples_frame, textvariable=self.num_samples, font=ctk.CTkFont(size=14))
        samples_entry.grid(row=0, column=1, sticky="e")
        
        # Training Iterations
        iter_frame = ctk.CTkFrame(config_frame)
        iter_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0,10))
        iter_frame.grid_columnconfigure(1, weight=1)
        iter_label = ctk.CTkLabel(iter_frame, text="Training Iterations:", font=ctk.CTkFont(size=14))
        iter_label.grid(row=0, column=0, sticky="w", padx=(0,10))
        iter_entry = ctk.CTkEntry(iter_frame, textvariable=self.num_iterations, font=ctk.CTkFont(size=14))
        iter_entry.grid(row=0, column=1, sticky="e")
        
        # Train Model Button
        self.train_button = ctk.CTkButton(
            config_frame,
            text="Train Model",
            command=self.initialize_model,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.train_button.grid(row=3, column=0, sticky="ew", padx=20, pady=(20,10))
        
        # Training status label
        self.status_label = ctk.CTkLabel(config_frame, textvariable=self.train_status, font=ctk.CTkFont(size=14), text_color="gray")
        self.status_label.grid(row=4, column=0, pady=(0,20))
        
    def create_input_section(self, parent):
        input_frame = ctk.CTkFrame(parent)
        input_frame.grid(row=0, column=1, sticky="nsew", padx=(10,0))
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_rowconfigure(2, weight=1)
        
        # Input Title
        input_title = ctk.CTkLabel(input_frame, text="Text Input", font=ctk.CTkFont(size=20, weight="bold"))
        input_title.grid(row=0, column=0, pady=(20,10))
        
        # Instruction Label
        instr_label = ctk.CTkLabel(input_frame, text="Enter text to classify as spam or ham", font=ctk.CTkFont(size=14), text_color="gray")
        instr_label.grid(row=1, column=0, pady=(0,5))
        
        # Text Area for input
        self.text_area = ctk.CTkTextbox(input_frame, font=ctk.CTkFont(size=14), wrap="word", height=200)
        self.text_area.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0,10))
        
        # Classify Button
        button_frame = ctk.CTkFrame(input_frame)
        button_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0,10))
        button_frame.grid_columnconfigure(0, weight=1)
        
        # Classify Text button
        self.classify_button = ctk.CTkButton(
            button_frame, 
            text="Classify Text", 
            command=self.classify_text, 
            font=ctk.CTkFont(size=14, weight="bold"), 
            height=40
        )
        self.classify_button.grid(row=0, column=0)
        
        # Result display
        self.result_label = ctk.CTkLabel(input_frame, text="Predicted Label: -", font=ctk.CTkFont(size=16, weight="bold"))
        self.result_label.grid(row=4, column=0, pady=(10,5))
        self.confidence_label = ctk.CTkLabel(input_frame, text="Confidence: -", font=ctk.CTkFont(size=14), text_color="gray")
        self.confidence_label.grid(row=5, column=0, pady=(0,10))
        
    def initialize_model(self):
        try:
            num_samples = int(self.num_samples.get())
            num_iterations = int(self.num_iterations.get())
            if num_samples <= 0 or num_iterations <= 0:
                raise ValueError
        except ValueError:
            self.train_status.set("Error: Please enter valid positive numbers")
            return
        
        self.train_status.set("Training model...")
        self.train_button.configure(state="disabled")
        self.classify_button.configure(state="disabled")
        
        def train_model_thread():
            try:
                # Train the model using the provided file (update the path as needed)
                model = train_spam_ham_model(
                    file_path=dataset_path,
                    num_samples=num_samples,
                    n_iterations=num_iterations
                )
                self.model_queue.put(model)
                self.train_status.set("Model trained successfully!")
                # Enable the classify button after training
                self.classify_button.configure(state="normal")
            except Exception as e:
                self.train_status.set(f"Training error: {str(e)}")
                self.train_button.configure(state="normal")
                
        thread = threading.Thread(target=train_model_thread)
        thread.daemon = True
        thread.start()
        
    def classify_text(self):
        # Check if model is available
        if self.model is None:
            if not self.model_queue.empty():
                self.model = self.model_queue.get()
            else:
                self.train_status.set("Error: Train the model first")
                return
        
        text = self.text_area.get("1.0", "end-1c").strip()
        if not text:
            self.train_status.set("Error: Please enter some text")
            return
        
        self.classify_button.configure(state="disabled")
        self.train_status.set("Classifying...")
        
        def process_classification():
            try:
                label, confidence = predict_label(self.model, text)
                # Update result display on main thread
                self.root.after(0, lambda: self.result_label.configure(text=f"Predicted Label: {label}"))
                self.root.after(0, lambda: self.confidence_label.configure(text=f"Confidence: {confidence*100:.2f}%"))
                self.root.after(0, lambda: self.train_status.set("Classification complete"))
                self.root.after(0, lambda: self.text_area.delete("1.0", "end"))
            except Exception as e:
                self.root.after(0, lambda: self.train_status.set(f"Classification error: {str(e)}"))
            finally:
                self.root.after(0, lambda: self.classify_button.configure(state="normal"))
                
        thread = threading.Thread(target=process_classification)
        thread.daemon = True
        thread.start()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TextClassificationGUI()
    app.run()