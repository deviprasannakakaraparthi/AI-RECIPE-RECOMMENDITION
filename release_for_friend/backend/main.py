import os
import shutil
import logging
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import torch
import pandas as pd

from detection import IngredientDetector
from recommendation import RecipeIntelligence
from contextlib import asynccontextmanager

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
detector = None
recommender = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global detector, recommender
    logger.info("Initializing Intelligence Engines...")
    try:
        detector = IngredientDetector()
        recommender = RecipeIntelligence()
    except Exception as e:
        logger.error(f"Failed to initialize engines: {e}")
    yield

app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    meal_type: str = Form("Lunch"),
    cuisine: str = Form("Indian"),
    spice_level: str = Form("Medium"),
    food_style: str = Form("Curry")
):
    if not detector or not recommender:
        raise HTTPException(status_code=500, detail="Engines not ready")

    try:
        # 1. Read Image Bytes
        image_bytes = await file.read()
        
        # 2. Advanced Detection (CLIP Zero-Shot)
        logger.info("Running advanced ingredient detection...")
        detected_ingredients = detector.detect(image_bytes)
        
        if not detected_ingredients:
            detected_ingredients = ["vegetables"]

        # 3. High-Quality Recipe Retrieval & Generation
        logger.info(f"Retrieving/Generating best {cuisine} {food_style} for: {detected_ingredients}")
        recipe_data = recommender.recommend_recipe(
            detected_ingredients, 
            cuisine=cuisine, 
            spice_level=spice_level,
            meal_type=meal_type,
            food_style=food_style
        )
        
        if not recipe_data:
            raise HTTPException(status_code=404, detail="No matching recipe found")

        # 4. Prepare Response
        # The Android app often expects 'Category' for the title display in some models
        return {
            "success": True,
            "detected_ingredients": detected_ingredients,
            "matched_recipe": {
                "Recipe_ID": "Retrieved",
                "Title": recipe_data["title"],
                "Cuisine": cuisine,
                "Ingredients": recipe_data["ingredients"],
                "Category": recipe_data["title"], 
                "Difficulty": "Medium",
                "Cooking_Time": "30-45 mins",
                "is_ai_generated": recipe_data.get("is_ai_generated", False)
            },
            "generated_steps": recipe_data["instructions"]
        }

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return {
            "success": False,
            "detected_ingredients": [],
            "matched_recipe": {"Title": "Error Matching Recipe"},
            "generated_steps": f"We encountered an issue: {str(e)}"
        }


@app.get("/health")
async def health():
    return {"status": "ok", "engines_active": detector is not None and recommender is not None}

if __name__ == "__main__":
    import uvicorn
    # Using 0.0.0.0 to allow access from Android Emulator/Devices
    uvicorn.run(app, host="0.0.0.0", port=8000)
