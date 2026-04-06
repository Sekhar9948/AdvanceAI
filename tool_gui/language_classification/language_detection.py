
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score
import re
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
dataset_path = os.path.join(project_root, 'dataset','language_data','Language Detection.csv')

class LanguageDetectionModel:
    def __init__(self, n_features=3000):
        """
        Initialize the language detection model.
        
        Args:
            n_features (int): Number of top n-gram features to use
        """
        self.n_features = n_features
        self.vectorizer = CountVectorizer(
            analyzer='char', 
            ngram_range=(1, 3), 
            max_features=n_features
        )
        self.W1 = None  # First layer weights
        self.b1 = None  # First layer bias
        self.W2 = None  # Output layer weights
        self.b2 = None  # Output layer bias
        self.classes = None  # List of language classes
        self.n_classes = None  # Number of language classes
        self.hidden_size = 100  # Size of hidden layer
        
    def preprocess_text(self, text):
        """
        Clean and preprocess the text.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Cleaned text
        """
        if not isinstance(text, str):
            return ""
        
        # Lowercase and remove punctuation
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        
        return text
    
    def relu(self, x):
        """ReLU activation function"""
        return np.maximum(0, x)
    
    def relu_derivative(self, x):
        """Derivative of ReLU function"""
        return np.where(x > 0, 1, 0)
    
    def softmax(self, x):
        """Softmax activation function"""
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)
    
    def initialize_parameters(self, input_size):
        """
        Initialize neural network parameters.
        
        Args:
            input_size (int): Size of the input features
        """
        # Xavier/Glorot initialization
        self.W1 = np.random.randn(input_size, self.hidden_size) * np.sqrt(2 / (input_size + self.hidden_size))
        self.b1 = np.zeros((1, self.hidden_size))
        self.W2 = np.random.randn(self.hidden_size, self.n_classes) * np.sqrt(2 / (self.hidden_size + self.n_classes))
        self.b2 = np.zeros((1, self.n_classes))
    
    def forward(self, X):
        """
        Forward pass through the neural network.
        
        Args:
            X (numpy.ndarray): Input features
            
        Returns:
            tuple: Hidden layer output and softmax output
        """
        # Hidden layer
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = self.relu(self.z1)
        
        # Output layer
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.softmax(self.z2)
        
        return self.a1, self.a2
    
    def backward(self, X, y, output, learning_rate):
        """
        Backward pass to update weights.
        
        Args:
            X (numpy.ndarray): Input features
            y (numpy.ndarray): One-hot encoded true labels
            output (numpy.ndarray): Predicted probabilities
            learning_rate (float): Learning rate for gradient descent
            
        Returns:
            float: Loss value
        """
        m = X.shape[0]
        
        # Output layer gradients
        dz2 = output - y
        dW2 = (1/m) * np.dot(self.a1.T, dz2)
        db2 = (1/m) * np.sum(dz2, axis=0, keepdims=True)
        
        # Hidden layer gradients
        dz1 = np.dot(dz2, self.W2.T) * self.relu_derivative(self.z1)
        dW1 = (1/m) * np.dot(X.T, dz1)
        db1 = (1/m) * np.sum(dz1, axis=0, keepdims=True)
        
        # Update parameters
        self.W2 -= learning_rate * dW2
        self.b2 -= learning_rate * db2
        self.W1 -= learning_rate * dW1
        self.b1 -= learning_rate * db1
        
        # Calculate cross-entropy loss
        loss = -np.mean(np.sum(y * np.log(output + 1e-8), axis=1))
        return loss
    
    def one_hot_encode(self, y):
        """
        Convert class labels to one-hot encoding.
        
        Args:
            y (numpy.ndarray): Class labels
            
        Returns:
            numpy.ndarray: One-hot encoded labels
        """
        m = y.shape[0]
        one_hot = np.zeros((m, self.n_classes))
        for i in range(m):
            one_hot[i, y[i]] = 1
        return one_hot
    
    def fit(self, X, y, learning_rate=0.01, n_iterations=1000, batch_size=32, verbose=True, progress_callback=None):
        """
        Train the neural network model.
        
        Args:
            X (numpy.ndarray): Feature matrix
            y (numpy.ndarray): Target labels
            learning_rate (float): Learning rate for gradient descent
            n_iterations (int): Number of training iterations
            batch_size (int): Mini-batch size
            verbose (bool): Whether to print progress
            progress_callback (callable, optional): Callback function to report training progress
            
        Returns:
            list: Training history (losses and accuracies)
        """
        # Get unique classes and their indices
        self.classes = np.unique(y)
        self.n_classes = len(self.classes)
        
        # Map classes to indices
        class_to_idx = {cls: i for i, cls in enumerate(self.classes)}
        y_indices = np.array([class_to_idx[cls] for cls in y])
        
        # One-hot encode the labels
        y_one_hot = self.one_hot_encode(y_indices)
        
        # Initialize parameters
        input_size = X.shape[1]
        self.initialize_parameters(input_size)
        
        # Training history
        history = {'loss': [], 'accuracy': []}
        
        # Number of samples
        m = X.shape[0]
        
        # Number of complete mini-batches
        n_batches = m // batch_size
        
        for iteration in range(n_iterations):
            # Shuffle the data
            indices = np.random.permutation(m)
            X_shuffled = X[indices]
            y_shuffled = y_one_hot[indices]
            
            loss_epoch = 0
            
            # Mini-batch gradient descent
            for batch in range(n_batches):
                start_idx = batch * batch_size
                end_idx = min((batch + 1) * batch_size, m)
                
                X_batch = X_shuffled[start_idx:end_idx]
                y_batch = y_shuffled[start_idx:end_idx]
                
                # Forward pass
                _, output = self.forward(X_batch)
                
                # Backward pass
                loss = self.backward(X_batch, y_batch, output, learning_rate)
                loss_epoch += loss
            
            # Average loss for the epoch
            loss_epoch /= n_batches
            
            # Calculate accuracy
            _, y_pred_probs = self.forward(X)
            y_pred = np.argmax(y_pred_probs, axis=1)
            accuracy = np.mean(y_pred == y_indices)
            
            # Store history
            history['loss'].append(loss_epoch)
            history['accuracy'].append(accuracy)
            
            # Update progress
            if progress_callback:
                progress_callback(iteration + 1, loss_epoch, accuracy, n_iterations)
            
            # Print progress
            if verbose and (iteration + 1) % 10 == 0:
                print(f"Iteration {iteration + 1}/{n_iterations}, Loss: {loss_epoch:.4f}, Accuracy: {accuracy:.4f}")
        
        return history
    
    def predict(self, X):
        """
        Predict language classes for input features.
        
        Args:
            X (numpy.ndarray): Input features
            
        Returns:
            numpy.ndarray: Predicted language classes
        """
        _, y_pred_probs = self.forward(X)
        y_pred_indices = np.argmax(y_pred_probs, axis=1)
        return np.array([self.classes[idx] for idx in y_pred_indices])
    
    def predict_proba(self, X):
        """
        Predict language probabilities for input features.
        
        Args:
            X (numpy.ndarray): Input features
            
        Returns:
            numpy.ndarray: Predicted probabilities for each language
        """
        _, y_pred_probs = self.forward(X)
        return y_pred_probs


def load_data(file_path, num_samples=None):
    """
    Load and preprocess the language detection dataset.
    
    Args:
        file_path (str): Path to the CSV file
        num_samples (int, optional): Number of samples to load, or None for all
        
    Returns:
        tuple: Preprocessed texts and their language labels
    """
    # Load the dataset
    df = pd.read_csv(file_path)
    
    # Basic cleaning
    df = df.dropna()
    
    # Take a random sample if specified
    if num_samples is not None and num_samples < len(df):
        df = df.sample(num_samples, random_state=42)
    
    # Extract texts and languages
    texts = df['Text'].values
    languages = df['Language'].values
    
    return texts, languages


def train_language_detection_model(file_path, num_samples=None, n_iterations=100, learning_rate=0.01, test_size=0.2, random_state=42, progress_callback=None):
    """
    Train a language detection model on the provided dataset.
    
    Args:
        file_path (str): Path to the CSV file
        num_samples (int, optional): Number of samples to use
        n_iterations (int): Number of training iterations
        learning_rate (float): Learning rate for gradient descent
        test_size (float): Proportion of data to use for testing
        random_state (int): Random seed for reproducibility
        progress_callback (callable, optional): Callback function to report training progress
        
    Returns:
        tuple: Trained model and test accuracy
    """
    # Load data
    texts, languages = load_data(file_path, num_samples)
    
    # Preprocess the texts
    model = LanguageDetectionModel()
    processed_texts = [model.preprocess_text(text) for text in texts]
    
    # Split the data
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        processed_texts, languages, test_size=test_size, random_state=random_state
    )
    
    # Vectorize the text data
    X_train = model.vectorizer.fit_transform(X_train_raw).toarray()
    X_test = model.vectorizer.transform(X_test_raw).toarray()
    
    # Train the model
    history = model.fit(
        X_train, 
        y_train, 
        learning_rate=learning_rate, 
        n_iterations=n_iterations,
        progress_callback=progress_callback
    )
    
    # Evaluate on test data
    y_pred = model.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_pred)
    
    if progress_callback:
        progress_callback(n_iterations, history['loss'][-1], history['accuracy'][-1], n_iterations)
    
    print(f"Test Accuracy: {test_accuracy:.4f}")
    
    return model, test_accuracy


def predict_language(model, text):
    """
    Predict the language of a given text.
    
    Args:
        model (LanguageDetectionModel): Trained language detection model
        text (str): Input text
        
    Returns:
        tuple: Predicted language and confidence
    """
    print("--- predict_language function in language_detection.py entered ---")
    # Preprocess the text
    processed_text = model.preprocess_text(text)
    print(f"--- Processed text: '{processed_text[:50]}...' ---")
    # Vectorize the text
    try:
        X = model.vectorizer.transform([processed_text]).toarray()
        print(f"--- Vectorized text shape: {X.shape} ---")
    except Exception as e:
        print(f"--- ERROR: Vectorization failed: {str(e)} ---")
        raise
    
    # Get predictions
    try:
        prediction = model.predict(X)[0]
        probabilities = model.predict_proba(X)[0]
        confidence = probabilities[np.argmax(probabilities)]
        print(f"--- Prediction: {prediction}, Confidence: {confidence} ---")
    except Exception as e:
        print(f"--- ERROR: Prediction failed: {str(e)} ---")
        raise
    
    return prediction, confidence


if __name__ == "__main__":
    # Hardcoded filepath
    file_path = dataset_path  # Change this to your actual file path
    
    # Get user input for number of samples and iterations
    num_samples = None
    try:
        user_samples = input("Enter number of samples to use (or press Enter to use all):(from 10,000) ").strip()
        if user_samples:
            num_samples = int(user_samples)
    except ValueError:
        print("Invalid input. Using all samples.")
    
    n_iterations = 100
    try:
        user_iterations = input("Enter number of training iterations (default: 100): ").strip()
        if user_iterations:
            n_iterations = int(user_iterations)
    except ValueError:
        print("Invalid input. Using default 100 iterations.")
    
    # Get user input for learning rate as float
    learning_rate = 0.01  # Default learning rate
    try:
        user_lr = input("Enter learning rate (default: 0.01): ").strip()
        if user_lr:
            learning_rate = float(user_lr)
            if learning_rate <= 0:
                print("Learning rate must be positive. Using default 0.01.")
                learning_rate = 0.01
    except ValueError:
        print("Invalid input for learning rate. Using default 0.01.")
    
    # Train the model
    print(f"\nTraining model with {num_samples if num_samples else 'all'} samples, {n_iterations} iterations, and learning rate {learning_rate}...")
    model, accuracy = train_language_detection_model(
        file_path=file_path,
        num_samples=num_samples,
        n_iterations=n_iterations,
        learning_rate=learning_rate
    )
    
    # Interactive testing
    print("\nModel trained! You can now test it with your own text.")
    print("Type 'exit' to quit.")
    
    while True:
        text = input("\nEnter text to detect language: ")
        if text.lower() == 'exit':
            break
        
        prediction, confidence = predict_language(model, text)
        print(f"Predicted language: {prediction} (Confidence: {confidence:.4f})")