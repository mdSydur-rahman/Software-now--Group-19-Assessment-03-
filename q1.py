import tkinter as tk  # For Tkinter GUI components
from tkinter import filedialog  # For opening file dialog to select images
from PIL import Image, ImageTk  # For handling image loading and displaying in Tkinter
import tensorflow as tf  # For using TensorFlow models
import numpy as np  # For array operations (needed for object detection)
import logging  # For logging actions

# Enable logging to track actions
logging.basicConfig(level=logging.INFO)

# Decorator for logging actions
def log_action(func):
    def wrapper(self, *args, **kwargs):
        logging.info(f"Action: {func.__name__} started.")
        result = func(self, *args, **kwargs)
        logging.info(f"Action: {func.__name__} completed.")
        return result
    return wrapper

# Base class for image classifiers
class ImageClassifier:
    def __init__(self):
        self._model = None  # Encapsulating model; only accessible via class methods
    
    # Encapsulation: Method to set model
    def set_model(self, model):
        self._model = model

    # Polymorphism: Placeholder method for subclass implementation
    def classify_image(self, image):
        raise NotImplementedError("This method should be overridden by subclasses")

# Subclass that inherits from ImageClassifier and uses MobileNetV2 model
class MobileNetV2Classifier(ImageClassifier):
    def __init__(self):
        super().__init__()
        self.set_model(tf.keras.applications.MobileNetV2(weights='imagenet'))  # Load MobileNetV2 model

    # Method overriding: Classify image using MobileNetV2
    @log_action
    def classify_image(self, image):
        image_array = tf.keras.preprocessing.image.img_to_array(image)
        image_array = tf.expand_dims(image_array, axis=0)
        image_array = tf.keras.applications.mobilenet_v2.preprocess_input(image_array)
        predictions = self._model.predict(image_array)
        decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=1)[0]
        result = decoded_predictions[0][1]  # Get the top prediction
        return f"MobileNetV2 classified: {result}"

# Object Detector class using TensorFlow
class ObjectDetector(ImageClassifier):
    def __init__(self):
        super().__init__()
        # Correctly indented line
        self.set_model(tf.saved_model.load(r'C:\Users\surface\Desktop\HIT137 Software now\Assignment 3\object_detection_model\faster-rcnn-inception-resnet-v2-tensorflow1-faster-rcnn-openimages-v4-inception-resnet-v2-v1'))

    @log_action
    def classify_image(self, image):
        # Prepare the image for object detection
        image_np = np.array(image)
        input_tensor = tf.convert_to_tensor(image_np)
        input_tensor = input_tensor[tf.newaxis, ...]  # Add batch dimension

        # Run object detection
        detections = self._model(input_tensor)  # Use self._model to access the encapsulated model
        
        # Extract detection results
        class_ids = detections['detection_classes'][0].numpy().astype(int)
        scores = detections['detection_scores'][0].numpy()

        # Filter out detections with low confidence
        results = []
        for i in range(len(scores)):
            if scores[i] > 0.5:  # Confidence threshold
                results.append(f"Detected: {class_ids[i]} with confidence: {scores[i]:.2f}")

        return "\n".join(results) if results else "No objects detected"

# Tkinter Application with Multiple Inheritance
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Image Classifier with OOP Concepts")
        self.geometry("800x600")

        # GUI components
        self.load_button = tk.Button(self, text="Load Image", command=self.load_image)
        self.load_button.pack(pady=20)

        self.image_label = tk.Label(self)
        self.image_label.pack(pady=20)

        self.classify_button = tk.Button(self, text="Classify", command=self.classify)
        self.classify_button.pack(pady=20)

        self.result_label = tk.Label(self, text="Classification: ")
        self.result_label.pack(pady=20)

        # Button to switch between models
        self.model_button = tk.Button(self, text="Switch to Object Detection", command=self.switch_model)
        self.model_button.pack(pady=20)

        # Initialize MobileNetV2 as the default classifier
        self.classifier = MobileNetV2Classifier()

    # Encapsulation: Method to load and display the image
    @log_action
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.image = Image.open(file_path).resize((224, 224))  # Resize to match model input size
            self.photo = ImageTk.PhotoImage(self.image)
            self.image_label.config(image=self.photo)
            self.result_label.config(text="")  # Clear previous result

    # Use the classifier to classify the image
    @log_action
    def classify(self):
        if hasattr(self, 'image'):
            result = self.classifier.classify_image(self.image)  # Use the current classifier
            self.result_label.config(text=result)  # Display the classification result
        else:
            self.result_label.config(text="No image loaded!")

    # Switch between different classifiers (Polymorphism in action)
    def switch_model(self):
        if isinstance(self.classifier, MobileNetV2Classifier):
            self.classifier = ObjectDetector()
            self.model_button.config(text="Switch to MobileNetV2")
            self.result_label.config(text="Switched to Object Detector")
        else:
            self.classifier = MobileNetV2Classifier()
            self.model_button.config(text="Switch to Object Detection")
            self.result_label.config(text="Switched to MobileNetV2 Classifier")

if __name__ == "__main__":
    app = Application()
    app.mainloop()

