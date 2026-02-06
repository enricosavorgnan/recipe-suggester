# Recipe Suggester - ML Models

Machine learning models for ingredient detection in the Recipe Suggester application. Uses YOLOv11 for real-time object detection to identify food ingredients from fridge images.

## Table of Contents

- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Design Overview](#design-overview)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [How It Works](#how-it-works)
- [API Interface](#api-interface)
- [Testing](#testing)
- [Model Details](#model-details)
- [Contributing](#contributing)

## Project Structure

```
models/
├── yolo/
│   ├── config/
│   │   ├── config_yolo_inf.yaml      # Inference configuration
│   │   └── config_yolo_ft.yaml       # Fine-tuning configuration
│   ├── model_weights/
│   │   ├── yolo_best.onnx            # Primary inference model (ONNX)
│   │   ├── yolo_best.pt              # PyTorch format
│   │   ├── yolo_last.pt              # Last training checkpoint
│   │   └── yolo11n_base.pt           # Base model for fine-tuning
│   ├── test_images/                  # Test images for unit tests
│   ├── detector.py                   # Main interface - backend entry point
│   ├── yolo_model.py                 # YOLOClass implementation
│   ├── finetuner.py                  # Fine-tuning utilities
│   ├── createjson.py                 # JSON parsing utility
│   └── yolo_test.py                  # Unit tests
├── test_images/                      # Sample fridge images for testing
├── recipesystem_test.py              # Recipe system integration tests
├── visionmodel_test.py               # Vision model tests
├── requirements.txt                  # ML dependencies
├── .gitignore
└── README.md
```

## Tech Stack

- **YOLOv11** (Ultralytics) - Object detection framework
- **ONNX Runtime** - Optimized model inference
- **OpenCV** - Image processing
- **NumPy** - Numerical computations
- **PyYAML** - Configuration management

## Design Overview

### Architecture

The models folder provides **in-process ingredient detection** that runs directly within the backend:

- **No separate service**: The ML model runs embedded in the backend process
- **Singleton pattern**: Model is loaded once and reused for all requests
- **Async compatible**: Detection runs in background tasks to avoid blocking
- **ONNX optimized**: Uses ONNX format for fast CPU/GPU inference

### Detection Pipeline

```
Image Upload → Preprocessing → YOLO Inference → Result Parsing → JSON Output
     │              │                │                │              │
     │              │                │                │              └─ {"name": "Tomato", "confidence": 0.95}
     │              │                │                └─ Extract classes, deduplicate
     │              │                └─ Run ONNX model, get bounding boxes
     │              └─ Resize to 640x640, normalize
     └─ jpg, png, bmp supported
```

### Integration with Backend

```
FRONTEND                    BACKEND                         MODELS
    │                           │                              │
    │  Upload fridge image      │                              │
    ├──────────────────────────>│                              │
    │                           │  Create IngredientsJob       │
    │                           ├─────────────────────────────>│
    │                           │                              │
    │  Return job_id            │  detect_ingredients()        │
    │<──────────────────────────│  (async background task)     │
    │                           │                              │
    │  Poll job status          │                              │
    ├──────────────────────────>│                              │
    │                           │  Return ingredients list     │
    │                           │<─────────────────────────────│
    │  Ingredients detected     │                              │
    │<──────────────────────────│                              │
```

## Getting Started

### Prerequisites

- Python 3.11+
- Backend environment set up (see `code/backend/README.md`)
- ~500MB disk space for model weights

### Installation

**You don't need to run this folder separately!** The models run in-process with the backend.

1. **Install ML dependencies in your backend environment**

   ```bash
   # From the repository root
   pip install -r code/models/requirements.txt
   ```

2. **Verify model weights exist**

   The model weights should be present at:
   ```
   code/models/yolo/model_weights/yolo_best.onnx
   ```

3. **Run the backend as usual**

   ```bash
   cd code/backend
   uvicorn app.main:app --reload
   ```

   The YOLO model will be loaded automatically on the first detection request.

### Standalone Testing

To test the detection module independently:

```bash
cd code/models/yolo

# Run detection on a test image
python -c "
from detector import detect_ingredients
result = detect_ingredients('test_images/fridge_3_items.png')
print(result)
"
```

## Configuration

### Inference Configuration

Located at `yolo/config/config_yolo_inf.yaml`:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `model_path` | Path to ONNX model weights | `../model_weights/yolo_best.onnx` |
| `image_size` | Input image dimensions | `640` |
| `conf_threshold` | Minimum confidence to detect | `0.25` |
| `save` | Save annotated images | `False` |

### Fine-tuning Configuration

Located at `yolo/config/config_yolo_ft.yaml`:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `config_data_path` | Path to dataset YAML | `../../../../data/Yolodataset/...` |
| `epochs` | Training epochs | `100` |
| `early_stop_patience` | Early stopping patience | `15` |
| `image_size` | Training image size | `640` |
| `batch_size` | Training batch size | `32` |
| `augmentation` | Enable data augmentation | `True` |
| `device` | GPU device index | `0` |
| `version_name` | Model version name | `yolo11_ft_v1` |
| `version_format` | Export format | `.onnx` |

## How It Works

### End-to-End Flow

1. **User uploads a fridge image** via the frontend
2. **Backend creates an IngredientsJob** and starts async processing
3. **Backend calls `detect_ingredients(image_path)`** from `detector.py`
4. **Detector loads the YOLO model** (singleton - loads only on first call)
5. **YOLO model runs inference** using the ONNX runtime
6. **Results are parsed and deduplicated** (keeps highest confidence per ingredient)
7. **Structured JSON is returned** to the backend
8. **Backend stores results** in the database and marks job complete
9. **Frontend receives** the detected ingredients with confidence scores

### Output Format

The `detect_ingredients()` function returns:

```python
[
    {"name": "Tomato", "confidence": 0.95},
    {"name": "Lettuce", "confidence": 0.87},
    {"name": "Cheese", "confidence": 0.82},
    ...
]
```

Each ingredient appears only once (deduplicated), with its highest confidence score.

## API Interface

### Main Function

```python
from detector import detect_ingredients

# Detect ingredients from an image
result = detect_ingredients(image_path: str) -> list[dict]
```

**Parameters:**
- `image_path` (str): Absolute or relative path to the image file

**Returns:**
- `list[dict]`: List of detected ingredients, each with `name` and `confidence` keys

**Raises:**
- `FileNotFoundError`: If the image path doesn't exist

**Example:**

```python
from detector import detect_ingredients

# Basic usage
ingredients = detect_ingredients("uploads/recipes/fridge_photo.jpg")

# Result
# [
#     {"name": "Tomato", "confidence": 0.95},
#     {"name": "Eggs", "confidence": 0.88},
#     {"name": "Milk", "confidence": 0.76}
# ]
```

### Supported Image Formats

- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- BMP (`.bmp`)

### Internal Components

| Module | Purpose |
|--------|---------|
| `detector.py` | Entry point - singleton model loading and detection interface |
| `yolo_model.py` | `YOLOClass` - training, validation, and prediction methods |

## Testing

### Running Unit Tests

```bash
cd code/models/yolo
python -m unittest yolo_test.py
```

### Test Cases

The test suite (`yolo_test.py`) covers:

| Test | Description |
|------|-------------|
| `test_image_format_validation` | Validates supported image formats (jpg, jpeg, png, bmp) |
| `test_black_image` | Ensures no false positives on empty/black images |
| `test_empty_fridge` | Handles empty fridge images correctly |
| `test_blurry_image` | Rejects overly blurry images (Gaussian blur) |
| `test_detection_accuracy_items` | Validates detection on known test images |
| `test_bounding_box_area` | Filters false positives by minimum bounding box size |

### Test Images

Test images are located in:
- `yolo/test_images/` - Unit test images

## Model Details

### Model Architecture

- **Base Model**: YOLOv11 nano (lightweight, fast inference)
- **Task**: Object detection for food ingredients
- **Training**: Fine-tuned on custom food ingredient dataset

### Model Weights

| File | Size | Format | Purpose |
|------|------|--------|---------|
| `yolo_best.onnx` | ~10.8 MB | ONNX | **Primary inference model** |
| `yolo_best.pt` | ~5.6 MB | PyTorch | Backup / retraining |
| `yolo_last.pt` | ~5.6 MB | PyTorch | Last training checkpoint |
| `yolo11n_base.pt` | ~5.6 MB | PyTorch | Base model for fine-tuning |

### Performance Characteristics

| Metric | Value |
|--------|-------|
| Model load time | ~2-3 seconds (first request only) |
| Inference time (GPU) | ~100-200ms per image |
| Inference time (CPU) | ~300-500ms per image |
| Memory usage | ~500MB (model + runtime) |
| Input size | 640x640 pixels |
| Confidence threshold | 0.25 (25%) |

### Detected Ingredient Classes

The model can detect common food ingredients including:
- Vegetables: Tomato, Lettuce, Bell Pepper, Beetroot, Carrot, etc.
- Fruits: Banana, Apple, Orange, etc.
- Proteins: Beef, Chicken, Eggs, etc.
- Dairy: Cheese, Milk, etc.
- And more...

## Contributing

### Fine-tuning the Model

To train on new data:

1. **Prepare dataset** in YOLO format with `data.yaml`
2. **Update config** in `yolo/config/config_yolo_ft.yaml`
3. **Run fine-tuning**:
   ```python
   from yolo_model import YOLOClass

   model = YOLOClass(
       yolo_model="yolo/model_weights/yolo11n_base.pt",
       config_data_path="path/to/data.yaml",
       project_folder="runs/train"
   )
   results, metrics = model.fine_tune("yolo/config/config_yolo_ft.yaml")
   ```
4. **Export to ONNX** (done automatically if configured)
5. **Replace** `yolo_best.onnx` with the new model
