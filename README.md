# EdvanceAI Education Tool

A modern, responsive AI education tool featuring a sleek UI built with CustomTkinter and PyQt6. This application provides an immersive learning experience for various AI models including Vision, Speech, Text, and Emotion detection models.

## Table of Contents
- [Features](#features)
- [System Requirements](#system-requirements)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Available Models](#available-models)
- [License](#license)

## Features

- **Dynamic UI**: Combines CustomTkinter and PyQt6 for maximum flexibility and aesthetics
- **Theme Switching**: Elegant dark/light mode toggle
- **Responsive Design**: Optimized for various screen sizes, including Raspberry Pi compatibility
- **Multi-Language Support**: English, Hindi, Kannada, Telugu translations
- **Model Categories**:
  - **Vision Models**: Hand Gesture Detection, Object Classification, Digit Recognition
  - **Speech Models**: Speaker Identification, 3D Voice Command
  - **Text Models**: Spam Detection, Language Classification
  - **Emotion Detection**: Facial Emotion Recognition
- **Autonomous Car Module**: Complete autonomous vehicle control system with YOLO detection
- **Smooth Animations**: Fluid transitions between screens and components
- **Expandable Architecture**: Designed for easy integration of new AI models

## System Requirements

- **OS**: Windows 10/11, macOS, or Linux
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended for running all models)
- **GPU**: Optional (NVIDIA GPU with CUDA for faster inference)
- **Display**: 800x600 resolution or higher
- **Raspberry Pi**: Compatible with Raspberry Pi 4 or newer (with adjusted performance)

## Prerequisites

Before setting up the project on a new laptop, ensure you have installed:

1. **Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"

2. **Git**
   - Download from [git-scm.com](https://git-scm.com/download/win)
   - Verify installation: `git --version`

3. **pip** (comes with Python)
   - Verify: `pip --version`

4. **Virtual Environment Support**
   - Should come with Python, verify: `python -m venv --help`

5. **Optional - CUDA & cuDNN** (for GPU acceleration)
   - Only needed if you have an NVIDIA GPU
   - Download from [NVIDIA Developer](https://developer.nvidia.com/cuda-downloads)

6. **Optional - FFmpeg** (for audio processing)
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Or use: `choco install ffmpeg` (if you have Chocolatey)

7. **Audio Libraries**
   - Windows: May need Visual C++ Build Tools
   - Download from [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

## Installation & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/Sekhar9948/AdvanceAI.git
cd AdvanceAI
```

### Step 2: Create a Virtual Environment

**On Windows (PowerShell/CMD):**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note**: If you encounter issues with specific packages:
- For PyAudio: May require additional system dependencies
- For TensorFlow: Can be memory-intensive, use CPU version if needed
- For CUDA support: Install `tensorflow-gpu` and `torch::cuda` versions

### Step 4: Download Pre-trained Models (Optional)

Pre-trained models are included in the `trained_models/` directory. If you need to retrain:

```bash
# Navigate to specific training modules
cd tool_gui/digit_detection/training
python digit_train_model.py

cd tool_gui/emotion_detection
python emotion_train_model.py

cd tool_gui/hand_gesture
python gesture_train_model.py
```

## Running the Application

### Start the Main Application

```bash
python main.py
```

This will launch the main EdvanceAI GUI with access to all models and features.

### Run Individual Models

**Digit Detection:**
```bash
python tool_gui/digit_detection/digit_main_gui.py
```

**Emotion Detection:**
```bash
python tool_gui/emotion_detection/facial_emotion_detection.py
```

**Hand Gesture Recognition:**
```bash
python tool_gui/hand_gesture/gesture_main_gui.py
```

**Object Detection:**
```bash
python tool_gui/object_detection/object_main_gui.py
```

**Language Detection:**
```bash
python tool_gui/language_classification/language_detection_main_gui.py
```

**Spam Classification:**
```bash
python tool_gui/spam_classification/spam_main_gui.py
```

**Speaker Identification:**
```bash
python tool_gui/speaker_identification/speaker_main_gui.py
```

**3D Speech to Text:**
```bash
python tool_gui/3d_speech_to_text/3d_model_control.py
```

**Autonomous Car:**
```bash
python src/screens/autonomous_car.py
```

## Project Structure

```
AdvanceAI/
├── main.py                          # Entry point for the application
├── requirements.txt                 # Python dependencies
├── language_manager.py              # Language management utilities
├── class_names.txt                  # Model class definitions
├── emotion_model_best.h5            # Emotion detection model
│
├── src/                             # Source code
│   ├── screens/                     # UI screens
│   │   ├── autonomous_car.py        # Autonomous vehicle control
│   │   ├── dashboard.py             # Main dashboard
│   │   ├── vision_models.py         # Vision model interface
│   │   ├── speech_models.py         # Speech model interface
│   │   └── text_models.py           # Text model interface
│   ├── components/                  # UI components
│   │   ├── header.py                # Header component
│   │   └── sidebar.py               # Sidebar navigation
│   ├── autonomous_car/              # Autonomous car module
│   │   ├── camera.py                # Camera interface
│   │   ├── command_handler.py       # Command processing
│   │   ├── decision_engine.py       # AI decision logic
│   │   ├── motor_controller.py      # Motor control
│   │   ├── yolo_detector.py         # YOLO object detection
│   │   ├── ultrasonic.py            # Ultrasonic sensors
│   │   └── ssh_client.py            # SSH communication
│   ├── themes/                      # UI themes
│   │   └── theme_manager.py         # Theme management
│   ├── translations/                # Language files
│   │   ├── en.json                  # English
│   │   ├── hi.json                  # Hindi
│   │   ├── kn.json                  # Kannada
│   │   └── te.json                  # Telugu
│   ├── utils/                       # Utility functions
│   │   └── responsive_utils.py      # Responsive design utilities
│   └── translator.py                # Translation engine
│
├── tool_gui/                        # Model training & testing GUIs
│   ├── digit_detection/             # Digit recognition
│   │   └── training/
│   ├── emotion_detection/           # Emotion recognition
│   ├── hand_gesture/                # Gesture recognition
│   ├── language_classification/     # Language detection
│   ├── object_detection/            # Object classification
│   ├── spam_classification/         # Spam detection
│   ├── speaker_identification/      # Speaker recognition
│   └── 3d_speech_to_text/           # 3D voice commands
│
├── trained_models/                  # Pre-trained model weights
│   ├── digit_classification/
│   ├── emotion_detection/
│   ├── hand_gesture_detection/
│   └── speaker_identification/
│
├── dataset/                         # Training datasets
│   ├── digit_data/
│   ├── emotion_detection/
│   ├── hand_data/
│   ├── language_data/
│   ├── object_data/
│   ├── spam_classification/
│   └── 3d_speech_to_text/
│
├── models/                          # Exported/compiled models
├── assets/                          # UI assets
│   └── icons/
└── captured_images/                 # User-captured training images
```

## Available Models

### Vision Models
- **Hand Gesture Detection**: Recognizes hand gestures in real-time
- **Object Detection**: Classifies objects using YOLO
- **Digit Recognition**: Recognizes handwritten digits

### Speech Models
- **Speaker Identification**: Identifies speakers from audio
- **3D Voice Commands**: Voice-based control with 3D visualization

### Text Models
- **Spam Classification**: Detects SMS spam messages
- **Language Detection**: Identifies text language

### Emotion Detection
- **Facial Emotion Recognition**: Detects emotions from facial expressions

### Autonomous Systems
- **Autonomous Car**: Complete vehicle control with obstacle detection

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError` for packages
- **Solution**: Ensure virtual environment is activated and run `pip install -r requirements.txt` again

**Issue**: Camera/Audio not working
- **Solution**: Check system permissions and ensure camera/microphone is connected

**Issue**: GPU not detected (TensorFlow/PyTorch)
- **Solution**: Install CUDA and cuDNN, then reinstall TensorFlow/PyTorch GPU versions

**Issue**: Out of memory errors
- **Solution**: Close other applications or use CPU-only models

**Issue**: PyAudio installation fails
- **Solution**: Install Visual C++ Build Tools (Windows) or use `pip install pipwin && pipwin install pyaudio`

## Performance Tips

1. Use GPU acceleration for faster inference (requires NVIDIA GPU + CUDA)
2. Close unnecessary applications to free up RAM
3. Adjust model input resolution for faster processing
4. Use lighter models for Raspberry Pi deployment

## Development

To add new models:

1. Create a new directory under `tool_gui/`
2. Implement training and inference scripts
3. Create a GUI wrapper in the same directory
4. Add menu option in `src/screens/` to access the model
5. Update translations in `src/translations/`

## Contributing

Contributions are welcome! Please feel free to submit pull requests or issues.

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or feature requests, please create an issue on GitHub.

---

**Last Updated**: 2026-06-26  
**Version**: 1.0.0  
**Author**: Sekhar9948 