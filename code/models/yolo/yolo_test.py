# External imports
import unittest
import cv2
import numpy as np
import os
from ultralytics import YOLO


def is_valid_format(filename):
    valid_exts = ['.jpg', '.jpeg', '.png', '.bmp']
    ext = os.path.splitext(filename)[1].lower()
    return ext in valid_exts


class TestVisionPipeline(unittest.TestCase):
    """ 
    This class tests performances of food-detection model.
    """


    @classmethod
    def setUpClass(cls):
        """
        Upload the model only 1 time.
        """

        # Load the detection model
        print("--- Model loading ---")
        cls.test_img_dir = "test_images"

    
    def test_image_format_validation(self):
        """
        Tests the image extention supported (jpg, jpeg, png).
        """

        # Define the supported image format
        valid_exts = ['.jpg', '.jpeg', '.png', '.bmp']
        invalid_exts = ['.gif', '.tiff', '.txt']
        for ext in valid_exts:
            filename = f"image{ext}"
            self.assertTrue(is_valid_format(filename))
        for ext in invalid_exts:
            filename = f"image{ext}"
            self.assertFalse(is_valid_format(filename), f"Error: {ext} should be invalid")


    def test_black_image(self):
        """
        Tests the performance with a black image as input (expected output: None).
        """

        # Create the black image and call the detection model prediction procedure
        black_img = np.zeros((640, 640, 3), dtype=np.uint8)
        model = YOLO("model_weights/yolo_best.onnx")
        result = model.predict(
            source=black_img,
            imgsz=640,
            conf=0.1,
        )
        self.assertEqual(len(result[0].boxes), 0, "Empty image should not return anything.")


    def test_empty_fridge(self):
        """
        Tests the performance with an empty-fridge image as input (expected output: None).
        """

        # Load the image and call the detection model prediction procedure
        img_path = os.path.join(self.test_img_dir, "empty_fridge.png")
        img = cv2.imread(img_path)
        if img is None: 
            self.skipTest("empty_fridge.jpg not found")
        model = YOLO("model_weights/yolo_best.onnx")
        result = model.predict(
            source=img,
            imgsz=640,
            conf=0.1,
        )
        self.assertEqual(len(result[0].boxes), 0, "Empty-fridge image should not return anything.")


    def test_blurry_image(self):
        """
        Tests the performance with a blurry image as input (expected output: None).
        """
        
        # Load a good image and blur it 
        img_path = os.path.join(self.test_img_dir, "frigo.png")
        img = cv2.imread(img_path)
        if img is None: 
            self.skipTest("good_fridge.jpg not found")

        # Apply the blur (moving hand) 
        blurry_img = cv2.GaussianBlur(img, (51, 51), 0)

        # Call the detection model prediction procedure
        model = YOLO("model_weights/yolo_best.onnx")
        result = model.predict(
            source=blurry_img,
            imgsz=640,
            conf=0.1,
        )
        self.assertEqual(len(result[0].boxes), 0, "Pre-processing had to discard the blurred image.")


    def test_detection_accuracy_items(self):
        """
        Tests the detection performance of the model with an image containing 3 objects.
        """

        # Load the image and define the expected output
        img_path = os.path.join(self.test_img_dir, "fridge_3_items.png") 
        img = cv2.imread(img_path)
        expected_labels = sorted(['Garlic', 'Lemon', 'Onion'])
        print('cias')
        # Call the detection model prediction procedure
        model = YOLO("model_weights/yolo_best.onnx")
        result = model.predict(
            source=img,
            imgsz=640,
            conf=0.2,
        )
        results = result[0]
        class_ids = results.boxes.cls.cpu().numpy()
        names = results.names
        detected_labels = sorted([names[int(c)] for c in class_ids])

        # Check if the number of detected items is the same as the expected output
        self.assertTrue(len(result[0].boxes) != 0, "No labels found")
        self.assertEqual(len(result[0].boxes), 3, "Wrong number of items detected ")

        # Check if the detected items were labeled correctly 
        #detected_labels = sorted([item['label'] for item in result[0].boxes])
        self.assertListEqual(detected_labels, expected_labels, "Detected classes are not correct")


    def test_bounding_box_area(self):
        """
        Tests the detection of false-positives.
        Verify the area of detected items. 
        If the area of the item is lesser than 0.5% of the entire image, then likely it is noise.
        """
    
        # Load the image
        img_path = os.path.join(self.test_img_dir, "fridge_4_items.png")
        img = cv2.imread(img_path)
        height, width, _ = img.shape
        total_area = height * width
    
        # Load the YOLO model
        model = YOLO("model_weights/yolo_best.onnx")
    
        # Make prediction
        results = model.predict(
            source=img,
            imgsz=640,
            conf=0.1,
        )
    
        r = results[0]
    
        # Skip test if no detections
        if len(r.boxes) == 0:
            self.skipTest("No detections for this image, skipping test.")
    
        # Extract bounding boxes and class ids
        boxes = r.boxes.xyxy.cpu().numpy()  # shape Nx4
        class_ids = r.boxes.cls.cpu().numpy()  # shape N
        names = r.names
    
        for i, (x1, y1, x2, y2) in enumerate(boxes):
            obj_area = (x2 - x1) * (y2 - y1)
            coverage_perc = (obj_area / total_area) * 100
            label = names[int(class_ids[i])]
            self.assertGreater(coverage_perc, 0.15, f"Too small item: {label} ({coverage_perc:.2f}%)" )
