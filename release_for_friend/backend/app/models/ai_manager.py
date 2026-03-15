import google.generativeai as genai
from PIL import Image
import io
import os
import torch
import random
from transformers import pipeline, T5Tokenizer, T5ForConditionalGeneration
from app.utils.similarity import recommend_recipes_full
from dotenv import load_dotenv

load_dotenv()

# --- AI Model Initialization ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
if not GOOGLE_API_KEY:
    GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY", "")

if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        print("Gemini AI (Premium) is ACTIVE.")
    except Exception as e:
        print(f"Error initializing Gemini: {e}")
        gemini_model = None
else:
    print("Gemini AI Key not found. Using Advanced Local Culinary Logic.")
    gemini_model = None

# CLIP for local vision
print("Loading Universal Food Vision (CLIP)...")
device = 0 if torch.cuda.is_available() else -1
vision_classifier = pipeline("zero-shot-image-classification", 
                             model="openai/clip-vit-base-patch32", 
                             device=device)

# --- Culinary Knowledge Database (Local Intelligence) ---
# This ensures that even without an API key, the recipes feel "real" and professional.
KNOWLEDGE_BASE = {
    "curry": {
        "pantry": ["Oil/Ghee", "Onion", "Tomato", "Ginger-Garlic Paste", "Turmeric Powder", "Red Chili Powder", "Coriander Powder", "Garam Masala", "Salt"],
        "prep": ["Wash and chop {ingredients} and vegetables into uniform pieces.", "Finely dice onions and prepare fresh ginger-garlic paste."],
        "steps": [
            "Heat {fat} in a heavy-bottomed pan. Sauté onions until deep golden brown.",
            "Add ginger-garlic paste and sauté for 2 minutes until fragrant.",
            "Pour in tomato puree and cook until the oil starts to separate from the masala.",
            "Add the main items ({ingredients}) along with all the dry spices.",
            "Pour in 1-2 cups of warm water. Cover and simmer on low heat until tender.",
            "Finish with a pinch of garam masala and fresh coriander leaves."
        ]
    },
    "biryani": {
        "pantry": ["Basmati Rice", "Yogurt", "Fried Onions (Birista)", "Mint Leaves", "Saffron", "Whole Spices (Cardamom, Cloves, Cinnamon)", "Ghee"],
        "prep": ["Soak Basmati rice for 30 minutes. Par-boil until 70% cooked.", "Marinate {ingredients} in yogurt, spices, and mint for at least 1 hour."],
        "steps": [
            "In a large pot, melt ghee and sauté whole spices until they crackle.",
            "Add the marinated {ingredients} and cook on medium heat until half-done.",
            "Layer the par-boiled rice over the base mixture.",
            "Sprinkle fried onions, saffron milk, and fresh mint on top.",
            "Seal the pot tightly with dough or foil (Dum).",
            "Slow-cook on very low flame for 25-30 minutes. Fluff and serve."
        ]
    },
    "masala": {
        "pantry": ["Butter/Oil", "Onion Paste", "Heavy Cream", "Kasturi Methi", "Tomato Puree", "Cashew Paste", "Spices"],
        "prep": ["Dice {ingredients} into bite-sized cubes.", "Prepare a smooth cashew and tomato base."],
        "steps": [
            "Sauté onions in butter until translucent.",
            "Add the tomato-cashew paste and cook until rich and thick.",
            "Stir in {ingredients} and coat well with the creamy sauce.",
            "Add a splash of water and simmer for 10-12 minutes.",
            "Stir in heavy cream and crushed Kasturi Methi for that authentic restaurant flavor."
        ]
    },
    "fry": {
        "pantry": ["Oil", "Curry Leaves", "Mustard Seeds", "Dry Red Chilies", "Asafoetida (Hing)", "Spices"],
        "prep": ["Slice {ingredients} into thin strips for even frying.", "Ensure the vegetables are completely dry to maintain crispness."],
        "steps": [
            "Heat oil in a wide skillet until shimmering.",
            "Add mustard seeds and curry leaves; let them temper.",
            "Add {ingredients} and toss on high heat for 3-5 minutes.",
            "Lower heat, add dry spices, and cook uncovered until golden and crisp.",
            "Serve as a perfect side dish with rice or dal."
        ]
    }
}

from recommendation import RecipeIntelligence

# Initialize the new intelligence engine
# We use the same dataset path as defined in recommendation.py
recipe_engine = RecipeIntelligence()

EXPANSIVE_INGREDIENTS = [
    "tomato", "onion", "garlic", "ginger", "potato", "green chili", "red chili", "paneer", 
    "chicken", "mutton", "beef", "fish", "prawn", "egg", "cauliflower", "okra", "brinjal", 
    "bitter gourd", "bottle gourd", "cabbage", "carrot", "beetroot", "spinach", "coriander", 
    "mint", "curry leaves", "lemon", "broccoli", "capsicum", "mushroom", "peas", "corn", 
    "apple", "banana", "mango", "orange", "pineapple", "grapes", "pomegranate", "lemon",
    "rice", "wheat flour", "dal", "lentils", "milk", "cheese", "butter", "bread", "pasta",
    "turmeric", "cumin", "cloves", "cinnamon", "cardamom", "black pepper", "curry powder"
]

def process_image_and_get_recipes(image_bytes, meal_type="Lunch", cuisine="Indian", spice_level="Medium", food_style="Curry"):
    image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    detected = []
    
    if gemini_model:
        try:
            # Enhanced prompt for higher accuracy
            prompt = (
                "Act as a Master Chef and Vision Expert. Identify every food ingredient, vegetable, fruit, or spice in this image. "
                "Be extremely accurate. Distinguish between similar items (e.g., Tomato vs Red Bell Pepper, Ginger vs Turmeric). "
                "Return only the comma-separated names of the ingredients."
            )
            response = gemini_model.generate_content([prompt, image_pil])
            detected = [x.strip().lower() for x in response.text.split(",") if x.strip()]
            print(f"Gemini detected: {detected}")
        except Exception as e:
            print(f"Gemini Vision Error: {e}")

    if not detected:
        print("Falling back to Local Vision (CLIP)...")
        results = vision_classifier(image_pil, candidate_labels=EXPANSIVE_INGREDIENTS)
        detected = [res['label'] for res in results[:5] if res['score'] > 0.08]
    
    if not detected: 
        detected = ["vegetables"]

    # Use the new RecipeIntelligence engine for higher accuracy
    match = recipe_engine.recommend_recipe(
        detected, 
        cuisine=cuisine, 
        spice_level=spice_level, 
        meal_type=meal_type, 
        food_style=food_style
    )
    
    if match:
        return {"success": True, "detected_ingredients": detected, "recipe": match}
    
    return {"error": "Could not find a recipe match."}

