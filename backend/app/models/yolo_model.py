import torch
from PIL import Image
import io

# Load pretrained YOLOv5 model
# Using torch.hub to load yolov5s from ultralytics
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

def detect_ingredients(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        results = model(image)
        # Extract names of detected objects
        # The user code: ingredients = results.pandas().xyxy[0]['name'].tolist()
        ingredients = results.pandas().xyxy[0]['name'].tolist()
        return ingredients
    except Exception as e:
        print(f"Error in detection: {e}")
        return []
