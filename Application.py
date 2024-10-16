import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import torch
from torchvision import models, transforms
import numpy as np

# ModelLoader class to handle loading the AI model and making predictions using PyTorch
# 1. Encapsulation: Wrapping related functionality in a class (ModelLoader)
class ModelLoader:
    def __init__(self):
        # Load a pre-trained ResNet18 model (encapsulation)
        self.model = models.resnet18(pretrained=True)
        self.model.eval()  # Set the model to evaluation mode

        # Image transformation (resize, normalize)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        # Load class labels (ImageNet)
        with open("imagenet_classes.txt") as f:
            self.labels = [line.strip() for line in f.readlines()]

    def classify(self, image_array):
        # Convert the image array to a PyTorch tensor and preprocess (encapsulation)
        image_tensor = self.transform(Image.fromarray(image_array)).unsqueeze(0)
        
        with torch.no_grad():
            outputs = self.model(image_tensor)
            _, predicted = outputs.max(1)
            label = self.labels[predicted.item()]
            confidence = torch.nn.functional.softmax(outputs, dim=1)[0][predicted].item()
        
        return label, confidence

# The main GUI application inheriting from Tkinter's Tk class
# 2. Multiple Inheritance: ImageClassifierApp inherits from both Tk class and ModelLoader class
class ImageClassifierApp(tk.Tk, ModelLoader):
    def __init__(self):
        tk.Tk.__init__(self)  # Initialize Tkinter
        ModelLoader.__init__(self)  # Initialize the ModelLoader

        self.title("AI Image Classifier")

        # Make the window full screen
        self.attributes('-fullscreen', True)

        # Exit Full-Screen button at the top-right corner
        self.exit_button = tk.Button(self, text="Exit Fullscreen", command=self.exit_fullscreen)
        self.exit_button.place(relx=0.95, rely=0.05, anchor=tk.NE)

        # Create a label to display the image (initially empty)
        self.image_label = tk.Label(self)
        self.image_label.pack(pady=20)

        # Center frame to hold buttons and result
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        # Create a button to upload an image
        self.upload_button = tk.Button(button_frame, text="Upload Image", command=self.upload_image, width=15)
        self.upload_button.pack(side=tk.TOP, pady=10)

        # Create a button to classify the image
        self.classify_button = tk.Button(button_frame, text="Classify Image", command=self.classify_image, width=15)
        self.classify_button.pack(side=tk.TOP, pady=10)

        # Label to display classification result, placed below the buttons
        self.result_label = tk.Label(self, text="Result will be shown here", font=("Helvetica", 12))
        self.result_label.pack(pady=10)

        self.image_array = None  # Variable to hold the image array

    def upload_image(self):
        # Open a file dialog to choose an image
        file_path = filedialog.askopenfilename()
        if file_path:
            img = Image.open(file_path)
            img = img.resize((400, 300))  # Resize image to 400x300
            self.image_array = np.array(img)  # Store the image in numpy array format for model input

            # Convert the image to ImageTk to display
            img_tk = ImageTk.PhotoImage(img)
            self.image_label.config(image=img_tk, text="")
            self.image_label.image = img_tk  # Keep a reference to prevent garbage collection
# 3. Method Overriding: Overriding Tk's mainloop method (from tk.Tk) to handle custom events
    def classify_image(self):
        if self.image_array is not None:
            # Use the model to classify the uploaded image
            label, confidence = self.classify(self.image_array)
            self.result_label.config(text=f"Prediction: {label} (Confidence: {confidence*100:.2f}%)")
        else:
            self.result_label.config(text="Please upload an image first.")

    def exit_fullscreen(self):
        self.attributes('-fullscreen', False)  # Exit full-screen mode
        self.geometry("900x800")  # Set window size to 900x800 after exiting full screen

# 4. Polymorphism: This allows the classify_image method to behave differently based on the class that invokes it
# We can have multiple different classes inheriting from ImageClassifierApp, each implementing its own classify_image method.
# Main entry point
if __name__ == "__main__":
    # Download ImageNet class labels
    import urllib.request
    urllib.request.urlretrieve("https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt", "imagenet_classes.txt")

    app = ImageClassifierApp()  # Create an instance of the application
    app.mainloop()  # Start the Tkinter event loop
