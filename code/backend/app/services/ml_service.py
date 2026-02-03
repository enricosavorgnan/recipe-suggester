"""
ML service for ingredient detection from images (external)
"""


def detect_ingredients_from_image(image_path: str) -> dict:
    """
    Detect ingredients from an image using ML model.

    CURRENTLY MOCKED - Comment for Luca:
     here instead of returning the mocked ingredients, you should of course call the ML service,
     which should take as input the image path (the image is found in upload folder) and return the
     dictionary of the ingredients, with the same format that you see in the mocked return.

    Args:
        image_path: Path to the uploaded image file

    Returns:
        dict: Detected ingredients with confidence scores
    """
    # MOCK RESPONSE - Remove this and uncomment ML call below when ready
    return {
        "ingredients": [
            {"name": "Tomato", "confidence": 0.95},
            {"name": "Onion", "confidence": 0.88},
            {"name": "Garlic", "confidence": 0.72},
            {"name": "Olive Oil", "confidence": 0.65}
        ]
    }
