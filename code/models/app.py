"""
FastAPI application for the Models Service.
Provides ingredient detection as a microservice.
"""
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add yolo directory to path for imports
yolo_path = Path(__file__).parent / "yolo"
if str(yolo_path) not in sys.path:
    sys.path.insert(0, str(yolo_path))

from detector import detect_ingredients  # type: ignore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Recipe Suggester - Models Service",
    description="Ingredient detection service using YOLO",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class PredictRequest(BaseModel):
    """Request model for ingredient detection."""
    image_path: str

    class Config:
        json_schema_extra = {
            "example": {
                "image_path": "uploads/recipes/fridge_photo.jpg"
            }
        }


class Ingredient(BaseModel):
    """Ingredient model with name and confidence."""
    name: str
    confidence: float


class PredictResponse(BaseModel):
    """Response model for ingredient detection."""
    ingredients: list[Ingredient]
    count: int

    class Config:
        json_schema_extra = {
            "example": {
                "ingredients": [
                    {"name": "Tomato", "confidence": 0.95},
                    {"name": "Lettuce", "confidence": 0.87}
                ],
                "count": 2
            }
        }


@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Recipe Suggester Models Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "predict": "/predict"
        }
    }


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "models"
    }


@app.post("/predict", response_model=PredictResponse, status_code=status.HTTP_200_OK)
async def predict(request: PredictRequest):
    """
    Detect ingredients from an image using YOLO model.

    The image should be accessible via a shared volume between backend and models service.

    Args:
        request: PredictRequest containing the image_path

    Returns:
        PredictResponse with detected ingredients and their confidence scores

    Raises:
        HTTPException: If image not found or detection fails
    """
    logger.info(f"Received prediction request for image: {request.image_path}")

    try:
        # Call the detector
        ingredients_list = detect_ingredients(request.image_path)

        # Format response
        response = PredictResponse(
            ingredients=ingredients_list,
            count=len(ingredients_list)
        )

        logger.info(f"Successfully detected {response.count} ingredients")
        return response

    except FileNotFoundError as e:
        logger.error(f"Image not found: {request.image_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image not found: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
