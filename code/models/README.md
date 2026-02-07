# Recipe Suggester - Models Service

**Ingredient detection microservice** for the Recipe Suggester application. Provides a REST API for detecting food ingredients from fridge images using YOLOv11.

The choice of separating this from the backend was in order to have independent deployment and simplify the logic to connect backend with models (otherwise, local dev was different from deployed environment).

## Table of Contents

- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Design Overview](#design-overview)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [How It Works](#how-it-works)
- [API Interface](#api-interface)
- [Testing](#testing)
- [Contributing](#contributing)

## Project Structure

```
models/
├── app.py                            # FastAPI application (entry point)
├── Dockerfile                        # Docker build configuration
├── requirements.txt                  # Service dependencies (FastAPI + ML)
├── yolo/
│   ├── config/
│   │   ├── config_yolo_inf.yaml     
│   │   └── config_yolo_ft.yaml       
│   ├── model_weights/
│   │   ├── yolo_best.onnx            
│   │   ├── yolo_best.pt              
│   │   ├── yolo_last.pt              
│   │   └── yolo11n_base.pt           
│   ├── test_images/                  
│   ├── detector.py                   # Detection logic (called by FastAPI)
│   ├── yolo_model.py                 # YOLOClass implementation
│   └── yolo_test.py                  # Unit tests
├── test_images/                      # Sample fridge images for testing
├── .gitignore
└── README.md
```

## Tech Stack

- **FastAPI** - web framework for the API
- **Uvicorn** - ASGI server for serving FastAPI
- **YOLOv11** (Ultralytics) - Object detection framework
- **ONNX Runtime** - Optimized model inference
- **OpenCV** - Image processing
- **NumPy** - Numerical computations
- **PyYAML** - Configuration management

## Design Overview

### Microservice Architecture

The models service is a **standalone FastAPI microservice** that provides ingredient detection via REST API. These are some of the
features:

- **Separate service**: It runs independently on port 8001
- **REST API**: Backend calls HTTP endpoints instead of direct function calls
- **Singleton pattern**: YOLO model loaded once and reused across requests
- **Shared volume**: Accesses images via shared filesystem with backend
- **ONNX optimized**: Uses ONNX format for fast CPU/GPU inference
- **Stateless**: No database, purely computational service

### Integration with Backend

```
FRONTEND                    BACKEND                     MODELS SERVICE
    │                           │                              │
    │  Upload fridge image      │                              │
    ├──────────────────────────>│                              │
    │                           │  Save to uploads/            │
    │                           │  Create IngredientsJob       │
    │                           │                              │
    │  Return job_id            │  POST /predict               │
    │<──────────────────────────│  (async background task)     │
    │                           ├─────────────────────────────>│
    │                           │                              │
    │  Poll job status          │  Detect ingredients          │
    ├──────────────────────────>│  Return JSON                 │
    │                           │<─────────────────────────────│
    │  Ingredients detected     │  Store in DB                 │
    │<──────────────────────────│                              │
```

## Getting Started

### Prerequisites

- Python 3.11+
- ~500MB disk space for model weights
- Shared volume access to `uploads/` directory (for Docker deployment)

### Local Development

1. **Install dependencies**

   ```bash
   cd code/models
   pip install -r requirements.txt
   ```

2. **Verify model weights exist**

   ```
   code/models/yolo/model_weights/yolo_best.pt
   ```

3. **Run the service**

   ```bash
   # Start the FastAPI service on port 8001
   uvicorn app:app --reload --port 8001

   # Or use the direct Python command
   python app.py
   ```

4. **Access the API**
   - **Service info**: `http://localhost:8001/`
   - **Health check**: `http://localhost:8001/health`
   - **API docs**: `http://localhost:8001/docs`
   - **Prediction endpoint**: POST `http://localhost:8001/predict`

### Docker Deployment

The models service is deployed as a container alongside backend and frontend:

```bash
# Included in docker-compose.yml
docker-compose up models
```

See the root README.md for full deployment instructions.

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

### REST Endpoints

#### `GET /health`
Health check for monitoring.

#### `POST /predict`
Detect ingredients from an image.

**Request:**
```json
{
  "image_path": "uploads/recipes/fridge_photo.jpg"
}
```

**Response:**
```json
{
  "ingredients": [
    {"name": "Tomato", "confidence": 0.95},
    {"name": "Lettuce", "confidence": 0.87},
    {"name": "Cheese", "confidence": 0.82}
  ],
}
```

### Usage Examples

**cURL:**
```bash
curl -X POST "http://localhost:8001/predict" \
  -H "Content-Type: application/json" \
  -d '{"image_path": "uploads/recipes/fridge_photo.jpg"}'
```

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
