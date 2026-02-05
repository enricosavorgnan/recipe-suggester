"""
Ingredient detection interface for the backend.
This module provides a clean interface to detect ingredients from images.
"""
import logging
import os
from pathlib import Path
from yolo_model import YOLOClass

logger = logging.getLogger(__name__)

# Global model instance (singleton pattern)
_model_instance = None


def get_model():
    """
    Get or initialize the YOLO model instance (singleton pattern).

    Returns:
        YOLOClass: Initialized YOLO model
    """
    global _model_instance
    if _model_instance is None:
        # Get the path to this file's directory
        current_dir = Path(__file__).parent
        model_path = current_dir / "model_weights" / "yolo_best.pt"
        _model_instance = YOLOClass(str(model_path))
    return _model_instance


def detect_ingredients(image_path: str) -> dict:
    """
    Detect ingredients from an image using YOLO model.

    This is the main interface function that the backend should call.

    Args:
        image_path: Path to the image file (absolute or relative)

    Returns:
        dict: Detected ingredients with confidence scores in the format:
        {
            "ingredients": [
                {"name": "Tomato", "confidence": 0.95},
                {"name": "Banana", "confidence": 0.88},
                ...
            ]
        }

    Raises:
        FileNotFoundError: If the image file doesn't exist
        Exception: For other errors during detection
    """
    logger.info(f"Detect ingredients from {image_path}")
    # Validate image path
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    try:
        # Get model instance
        model = get_model()

        # Get config path
        current_dir = Path(__file__).parent
        config_path = current_dir / "config" / "config_yolo_inf.yaml"

        logger.info(f"Loading config from {config_path}")
        # Run prediction
        results = model.predict(
            config_path=str(config_path),
            image_path=image_path,
            project_folder=None  # Don't save results
        )

        # Parse results
        ingredients = []
        if results and len(results) > 0:
            result = results[0]
            if hasattr(result, 'boxes') and len(result.boxes) > 0:
                boxes = result.boxes
                class_ids = boxes.cls.cpu().numpy()
                confidences = boxes.conf.cpu().numpy()
                names = result.names

                for i, class_id in enumerate(class_ids):
                    ingredient_name = names[int(class_id)]
                    confidence = float(confidences[i])
                    ingredients.append({
                        "name": ingredient_name,
                        "confidence": confidence
                    })

        logger.info(f"Detected {len(results)} ingredients")

        return {"ingredients": ingredients}

    except Exception as e:
        print(f"Error in detect_ingredients: {e}")
        raise
