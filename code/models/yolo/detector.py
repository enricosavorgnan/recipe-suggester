"""
Ingredient detection interface for the backend.
This module provides a clean interface to detect ingredients from images.
"""
import logging
import os
from pathlib import Path
from yolo_model import YOLOClass

logger = logging.getLogger(__name__)

# Global model instance 
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

    Raises:
        FileNotFoundError: If the image file doesn't exist
        Exception: For other errors during detection
    """

    # Validate image path
    logger.info(f"Detect ingredients from {image_path}")
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    try:
        # Get model instance
        model = get_model()

        # Get config path
        current_dir = Path(__file__).parent
        config_path = current_dir / "config" / "config_yolo_inf.yaml"
        
        # Run prediction
        logger.info(f"Loading config from {config_path}")
        results = model.predict(
            config_path=str(config_path),
            image_path=image_path,
            project_folder=None  # Don't save results
        )

        # Parse results
        ingredients_map = {}
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
                    if ingredient_name not in ingredients_map or confidence > ingredients_map[ingredient_name]:
                        ingredients_map[ingredient_name] = confidence

        # Convert the dictionary into a list of dictionaries to return
        unique_ingredients_list = [
            {"name": name, "confidence": conf} 
            for name, conf in ingredients_map.items()
        ]
        logger.info(f"Detected {len(unique_ingredients_list)} ingredients")
        return unique_ingredients_list

    except Exception as e:
        print(f"Error in detect_ingredients: {e}")
        raise
