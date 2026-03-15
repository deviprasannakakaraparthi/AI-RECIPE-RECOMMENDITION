import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import io
import logging
import random

logger = logging.getLogger(__name__)

class IngredientDetector:
    def __init__(self, model_name="openai/clip-vit-base-patch32"):
        self.dummy_mode = False
        try:
            logger.info(f"Attempting to load CLIP model {model_name}...")
            self.device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
            self.model = CLIPModel.from_pretrained(model_name, local_files_only=False).to(self.device)
            self.processor = CLIPProcessor.from_pretrained(model_name, local_files_only=False)
            logger.info("CLIP model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load CLIP: {e}. Switching to DUMMY vision mode.")
            self.dummy_mode = True

        
        # Comprehensive list of vegetables and ingredients (especially Indian/Common ones)
        self.common_ingredients = [
            "tomato", "onion", "garlic", "ginger", "potato", "carrot", "broccoli", 
            "spinach", "cauliflower", "cabbage", "green chili", "red chili", 
            "capsicum", "bell pepper", "eggplant", "brinjal", "bitter gourd", 
            "bottle gourd", "ladyfinger", "okra", "paneer", "chicken", "mutton", 
            "fish", "egg", "lemon", "coriander", "mint", "curry leaves", 
            "cucumber", "radish", "beetroot", "mushroom", "corn", "peas", 
            "apple", "banana", "orange", "grape", "mango", "pineapple", 
            "watermelon", "pomegranate", "basil", "parsley", "thyme", "rosemary",
            "curd", "yogurt", "milk", "cheese", "butter", "flour", "rice", "pasta",
            "bread", "lentils", "dal", "chickpeas", "soybean", "tofu", "bread"
        ]

    def detect(self, image_bytes):
        if self.dummy_mode:
            logger.info("Using Dummy Vision Fallback (Randomized sample).")
            return random.sample(self.common_ingredients[:15], 3)

        try:
            if not image_bytes: 
                logger.warning("No image bytes received!")
                return ["vegetables"]
            
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            
            # For Accuracy: We use zero-shot classification on the whole image.
            inputs = self.processor(
                text=[f"a photo of {ing}" for ing in self.common_ingredients], 
                images=image, 
                return_tensors="pt", 
                padding=True
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image # this is the image-text similarity score
                probs = logits_per_image.softmax(dim=1) # we can take the softmax to get probabilities

            # Get top N ingredients with a threshold
            # Improved: Lower threshold and debug logs
            threshold = 0.02 # Lowered from 0.05 to capture more
            
            # Log top 5 for debugging
            top_5_probs, top_5_indices = torch.topk(probs[0], 5)
            logger.info("Top 5 detections confidence:")
            for i in range(5):
                idx = top_5_indices[i].item()
                prob = top_5_probs[i].item()
                name = self.common_ingredients[idx]
                logger.info(f"  - {name}: {prob:.4f}")

            indices = torch.where(probs[0] > threshold)[0]
            
            detected = []
            if len(indices) == 0:
                # Fallback to top 1 if nothing exceeds threshold
                top_idx = torch.argmax(probs[0]).item()
                detected.append(self.common_ingredients[top_idx])
            else:
                for idx in indices:
                    detected.append(self.common_ingredients[idx.item()])
                    
            logger.info(f"CLIP detected (Final): {detected}")
            return list(set(detected))

        except Exception as e:
            logger.error(f"Error in CLIP detection: {e}")
            return ["vegetables"] # Generic fallback
