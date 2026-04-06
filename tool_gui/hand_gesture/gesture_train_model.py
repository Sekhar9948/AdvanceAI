
import pandas as pd
import numpy as np
import sys
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
dataset_path = os.path.join(project_root, 'dataset','hand_data','hand_gesture_data.csv')

# Get hyperparameters from command-line arguments
try:
    n_estimators = int(sys.argv[1])  # First argument
    max_depth = int(sys.argv[2]) if sys.argv[2] != "None" else None  # Second argument (can be None)
except (IndexError, ValueError):
    print("Invalid arguments! Using default values: n_estimators=100, max_depth=None")
    n_estimators = 100
    max_depth = None

# Load dataset
df = pd.read_csv(dataset_path)

# Convert labels to numerical values
labels = df["label"].astype("category").cat.codes
features = df.drop(columns=["label"])

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

# Train Random Forest classifier with dynamic parameters
clf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth)
clf.fit(X_train, y_train)

# Save trained model
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
save_dir = os.path.join(project_root, 'trained_models/hand_gesture_detection')
os.makedirs(save_dir, exist_ok=True)
save_path = os.path.join(save_dir, 'gesture_model.pkl')
joblib.dump(clf, save_path)



# Evaluate model
accuracy = clf.score(X_test, y_test)
print(f"Model trained successfully! Accuracy: {accuracy * 100:.2f}%")