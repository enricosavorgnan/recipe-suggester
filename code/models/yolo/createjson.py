# External imports
import json


def createJson(results: list):
    """
    Parses object detection results and exports them to a structured JSON file.

    :param results: A list of result objects from the predictor model, 
                    containing bounding boxes, class names, and confidence scores
    :return: None, the function return a JSON file
    """

    # Initialize an empty dictionary to store unique detected classes and 
    # their highest confidence scores, preventing duplicate entries for the same ingredient
    try:
        found_items = {}  
        for result in results:
            # Move tensors to CPU and convert them to NumPy arrays for easier iteration
            # 'cls' contains class IDs while 'conf' contains the model's confidence scores
            if result.boxes is not None:
                class_indices = result.boxes.cls.cpu().numpy().astype(int)
                confidences = result.boxes.conf.cpu().numpy()

                for class_idx, conf in zip(class_indices, confidences):
                    # Map the numerical class index back to its human-readable string name 
                    # using the model's internal metadata
                    class_name = result.names[class_idx]

                    # Update the confidence score for the ingredient only if the current 
                    # detection is more reliable (higher) than the previous one found
                    if class_name in found_items:
                        found_items[class_name] = max(found_items[class_name], float(conf))
                    else:
                        found_items[class_name] = float(conf)

        # Structure the final output 
        output_data = {
            "ingredients": [
                {
                    "name": name,
                    "confidence": round(conf, 2)
                }
                for name, conf in found_items.items()
            ],
            "success": True
        }

    # Fallback mechanism: if the tensor processing fails, return a failure 
    # status and the error message to avoid crashing the entire pipeline.
    except Exception as e:
        # In caso di errore
        output_data = {
            "ingredients": [],
            "success": False,
            "error": str(e),
        }
    with open("detected_ingredients.json", "w") as f:
        json.dump(output_data, f, indent=4)

