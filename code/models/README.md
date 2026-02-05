# Models Folder

This folder contains the machine learning models for ingredient detection.

## Structure

```
models/
├── yolo/
│   ├── config/
│   │   └── config_yolo_inf.yaml    # Inference configuration
│   ├── model_weights/
│   │   └── yolo_best.onnx          # Trained YOLO model weights
│   ├── test_images/                # Sample images for testing
│   ├── detector.py                 # Main interface - use this from backend
│   ├── yolo_model.py               # YOLO model class (training, testing, prediction)
│   └── yolo_test.py                # Unit tests for the model
├── requirements.txt                # ML dependencies
└── .gitignore
```

## Setup

### 1. Install Dependencies

```bash
cd code/models
pip install -r requirements.txt
```

### 2. Usage from Backend

The backend automatically imports the detection function from this folder. No separate service needed.

The backend calls:
```python
from detector import detect_ingredients

# Pass image path, get ingredients back
result = detect_ingredients("path/to/image.jpg")
# Returns: {"ingredients": [{"name": "Tomato", "confidence": 0.95}, ...]}
```

### 3. Local Development

**You don't need to run this folder separately!**

When running locally:
1. Install ML dependencies: `pip install -r code/models/requirements.txt` (in your backend environment)
2. Run backend as usual: `cd code/backend && uvicorn app.main:app --reload`
3. The backend will automatically load the YOLO model when needed

### 4. Testing the Model

To run unit tests:
```bash
cd code/models/yolo
python -m unittest yolo_test.py
```

## How It Works

1. **Backend calls `detect_ingredients(image_path)`** from `detector.py`
2. **Detector module** loads the YOLO model (singleton pattern - loads once)
3. **YOLO model** runs inference on the image
4. **Results are parsed** and returned as a structured dict
5. **Backend receives** the ingredients list with confidence scores

No Docker container needed - the model runs in-process with the backend!

## Model Information

- **Model**: YOLOv11 fine-tuned for food ingredient detection
- **Format**: ONNX (optimized for inference)
- **Input**: Image file (jpg, png, etc.)
- **Output**: List of detected ingredients with confidence scores
