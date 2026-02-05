# External imports
import unittest
import cv2
import numpy as np
import os
from finetuner import YOLOClass


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
        cls.model = YOLOClass("./model_weights/yolo_best.onnx")
        cls.test_img_dir = "test_images"
        cls.config_path = "./config/config_yolo_inf.yaml"
        cls.project_folder = "./results/"
        

    
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
        result = self.model.predict(
            config_path=self.config_path,
            image_path=black_img,
            project_folder=self.project_folder
        )
        self.assertEqual(len(result[0].boxes), 0, "Empty image should not return anything.")


    def test_empty_fridge(self):
        """
        Tests the performance with an empty-fridge image as input (expected output: None).
        """

        # Load the image and call the detection model prediction procedure
        img_path = os.path.join(self.test_img_dir, "empty_fridge.png")
        img = cv2.imread(img_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if img_rgb is None: 
            self.skipTest("empty_fridge.jpg not found")
        result = self.model.predict(
            config_path=self.config_path,
            image_path=img_path,
            project_folder=self.project_folder
        )
        self.assertEqual(len(result[0].boxes), 0, "Empty-fridge image should not return anything.")


    def test_blurry_image(self):
        """
        Tests the performance with a blurry image as input (expected output: None).
        """
        
        # Load a good image and blur it 
        img_path = os.path.join(self.test_img_dir, "frigo.png")
        img = cv2.imread(img_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if img_rgb is None: 
            self.skipTest("good_fridge.jpg not found")

        # Apply the blur (moving hand) 
        blurry_img = cv2.GaussianBlur(img_rgb, (51, 51), 0)

        # Call the detection model prediction procedure
        result = self.model.predict(
            config_path=self.config_path,
            image_path=blurry_img,
            project_folder=self.project_folder
        )
        self.assertEqual(len(result[0].boxes), 0, "Pre-processing had to discard the blurred image.")


    def test_detection_accuracy_items(self):
        """
        Tests the detection performance of the model with an image containing 3 objects.
        """

        # Load the image and define the expected output
        img_path = os.path.join(self.test_img_dir, "fridge_3_items.png") 
        img = cv2.imread(img_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        expected_labels = sorted(['Banana', 'Beef', 'Tomato'])

        # Call the detection model prediction procedure
        result = self.model.predict(
            config_path=self.config_path,
            image_path=img_path,
            project_folder=self.project_folder
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
        img_path = os.path.join(self.test_img_dir, "fridge_3_items.png")
        img = cv2.imread(img_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        height, width, _ = img_rgb.shape
        total_area = height * width
        
        # Call the detection model prediction procedure
        results = self.model.predict(
            config_path=self.config_path,
            image_path=img_path,
            project_folder=self.project_folder
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
