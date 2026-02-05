import yaml

from ultralytics import YOLO
from ultralytics.utils.metrics import DetMetrics


class YOLOClass:
    """
    Class implemented to make cleaner and easier fine-tune given version of YOLO.
    """

    def __init__(self, yolo_model : str, config_data_path : str | None = None, project_folder : str | None = None):
        """
        Initializer method for YOLOFineTuner

        Params:
        - yolo_model : string, name to a valid YOLO model
        - config_data_path : string, path to a dataset configuration YAML file
        - project_folder : string, path to a specific folder where to store results of training, validation and predictions
        """
        
        try:
            self.model = YOLO(yolo_model)
        except Exception as e:
            print(f"An exception occurred while trying to instantiate the class:\n\n{e}")

        self.config_data_path = config_data_path # Path to an eventual fine-tuning configuration file. Possibly None 
        self.project_folder = project_folder # Path to an eventual project folder where store results of predictions and results. Possibly None


    def fine_tune(self, config_path : str) -> tuple:
        """
        Fine-tune of a model given the weights

        Params:
        - config_path : string, path linking to a configuration YAML file

        Returns:
        - train_results : object, results of the fine-tuning
        - ft_metrics : object, metrics of the fine-tuning validation
        """
        # Load configuration path
        try:
            with open(config_path, 'r') as f:
                config = yaml.save_load(f)
        except FileNotFoundError as e:
            print(f"File {config_path} not found\nError:\n\n{e}")
            return

        # Define variables for eventual use
        self.config_data_path = config['config_data_path']
        ft_folder = self.project_folder + 'finetune/' if self.project_folder is not None else None

        # Start fine-tuning
        train_results = self.model.train(
            data = self.config_data_path,
            epochs = config['epochs'],
            patience = config['early_stop_patience'],
            imgsz = config['image_size'],
            batch = config['batch_size'],
            augment = config['augmentation'],
            device = config['device'],
            name = config['version_name'],
            project = ft_folder
        )

        # Export the model
        self.model.export(format=config['version_format'])

        # Validate the fine-tuning
        ft_metrics = self.model.val()
        print(f"mAP50-95: {ft_metrics.box.map}")

        return train_results, ft_metrics


    def load_module(self, finetuned_model_path : str):
        """
        Loads a fine-tuned version of YOLO from a given path

        Params:
        - finetuned_model_path : string, path to the fine-tuned model weights
        """
        assert finetuned_model_path.endswith(('.pt', '.onnx')), "The model path must end with .pt or .onnx"
        self.model = YOLO(finetuned_model_path)


    def test(self, model_path : str | None = None, split : str = "val", project_folder : str | None = None) -> DetMetrics:
        """
        Test the model on a given split of the dataset.

        Params:
        - model_path : string or None, path to the model weights to be used for testing (if None, use loaded model)
        - split : string, dataset split to be used for testing (e.g., 'val', 'test')
        - project_folder : string, path to a folder where to store test results. Automatically adds an inner folder 'validation/'

        Returns:
        - val_metrics : object, metrics obtained from the testing
        """
        if self.model is None:
            assert model_path is not None, "No model loaded. Please provide a model path."
            self.load_module(model_path)
            self.project_folder = project_folder

        val_folder = self.project_folder + 'validation/' if self.project_folder is not None else None

        val_metrics = self.model.val(split=split, project=val_folder)

        print(f"{split} mAP50-95: {val_metrics.box.map}")

        return val_metrics


    def predict(self, config_path : str,  image_path : str, project_folder : str | None = None):
        """
        Make the prediction on a given image.

        Params:
        - image_path : string, path to the image where to make prediction
        - config_path : string, path to the inference configuration YAML file.
        - project_folder : string, path to a folder where to store test results. Automatically adds an inner folder 'prediction/'

        Returns:
        - predictions : object, predictions made by the model
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.save_load(f)
        except FileNotFoundError as e:
            print(f"File {config_path} not found\nError:\n\n{e}")
            return
            
        if self.model is None:
            assert config['model_path'] is not None, "No model loaded. Please provide a model path."
            self.load_module(config['model_path'])
            self.project_folder = project_folder

        predict_folder = self.project_folder + 'prediction/' if self.project_folder is not None else None

        predictions = self.model.predict(
            source=image_path,
            imgsz=conifg['img_size'],
            conf=config['conf_threshold'],
            save=config['save'],
            project = predict_folder
        )
        
        return predictions


if __name__ == '__main__':
    yolo_finetuner = YOLOClass("../../../yolo11n.pt")

    config_ft_path = "./config_yolo_finetune.yaml"
    results_ft, metrics = yolo_finetuner.fine_tune(config_ft_path)
    print(f"Final mAP50-95 after fine-tuning: {metrics.box.map}")

    config_inf_path = './config_yolo_inference.yaml'
    image_path = '../tests/frigo.png'
    results_inf = yolo_finetuner.predict(config_inf_path, image_path)
    print(results_inf)