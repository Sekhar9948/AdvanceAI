
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D, BatchNormalization
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
model_path = os.path.join(project_root, 'trained_models','emotion_detection')
dataset_path = os.path.join(project_root, 'dataset','emotion_detection')

print("TensorFlow version:", tf.__version__)

# Define input shape
IMG_SIZE = 48
CHANNELS = 3  # RGB input
input_shape = (IMG_SIZE, IMG_SIZE, CHANNELS)

# Load pre-trained MobileNetV2 model with ImageNet weights
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=input_shape)
base_model.trainable = False  # Freeze the base model

# Add custom layers
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(512, activation='relu')(x)
x = BatchNormalization()(x)
x = Dropout(0.5)(x)
x = Dense(256, activation='relu')(x)
x = BatchNormalization()(x)
x = Dropout(0.5)(x)
output_layer = Dense(3, activation='softmax')(x)  # Output layer with 3 emotions

model = Model(inputs=base_model.input, outputs=output_layer)

# Model summary
model.summary()

# Compile the model
model.compile(
    optimizer=Adam(learning_rate=0.0005),  # Lower learning rate for stability
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Data augmentation and dataset loading
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest',
    validation_split=0.2  # Auto split 80-20
)

val_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

dataset_path = dataset_path  # Ensure your dataset is inside 'dataset/'
if not os.path.exists(dataset_path):
    raise FileNotFoundError(f"Dataset folder '{dataset_path}' not found! Make sure it exists.")

train_generator = train_datagen.flow_from_directory(
    dataset_path,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=32,
    class_mode='categorical',
    subset='training',
    shuffle=True
)

val_generator = val_datagen.flow_from_directory(
    dataset_path,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=32,
    class_mode='categorical',
    subset='validation'
)

# Callbacks
callbacks = [
    ModelCheckpoint('emotion_model_best.h5', monitor='val_accuracy', save_best_only=True, verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5, min_lr=1e-6, verbose=1),
    EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=1)
]

# Train the model
history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=5,  # Increased for better learning
    callbacks=callbacks
)

# Save the model
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
save_dir = os.path.join(project_root, 'trained_models/emotion_detection')
os.makedirs(save_dir, exist_ok=True)
save_path = os.path.join(save_dir, 'emotion_model.h5')

model.save(save_path)
print("Model saved as emotion_model.h5")

# Convert to TensorFlow Lite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

with open(f"{model_path}/emotion_model.tflite", "wb") as f:
    f.write(tflite_model)

print("Model training complete and saved as emotion_model.tflite.")