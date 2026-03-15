import os
import shutil
import logging
import uuid
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import torch
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from detection import IngredientDetector
from recommendation import RecipeIntelligence
from app.models.video_maker import create_recipe_video_sync
from contextlib import asynccontextmanager

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import threading
video_lock = threading.Lock()

def locked_create_video(*args, **kwargs):
    """Wrapper to ensure only one video is generated at a time to prevent CPU overload."""
    with video_lock:
        try:
            return create_recipe_video_sync(*args, **kwargs)
        except Exception as e:
            logger.error(f"Video generation failed: {e}")

import sys
# Fix for MoviePy/ImageMagick 7 on macOS
if sys.platform == "darwin":
    mac_magick = "/opt/homebrew/bin/magick"
    if os.path.exists(mac_magick):
        os.environ["IMAGEMAGICK_BINARY"] = mac_magick
else:
    magick_path = shutil.which("magick")
    if magick_path:
        os.environ["IMAGEMAGICK_BINARY"] = magick_path

# Verify API Key
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if api_key and api_key != "your_key_here":
    logger.info(f"API Key detected: {api_key[:5]}...{api_key[-5:]}")
else:
    logger.warning("No valid API Key found in environment variables!")

# Global instances
detector = None
recommender = None


# ──────────────────────────────────────────────
# Request / Response Models
# ──────────────────────────────────────────────
class RecipeGenerateRequest(BaseModel):
    ingredients: List[str]
    recipe_name: Optional[str] = None
    meal_type: str = "Lunch"
    cuisine: str = "Indian"
    spice_level: str = "Medium"
    food_style: str = "Curry"


def _format_recipes_for_android(recipe_data, detected_ingredients: List[str]):
    """Convert the recommender output into the flat RecipeResponse format
    expected by the Android app (list of RecipeModel objects)."""
    recipes_out = []

    # recipe_data can be a single dict OR a list of dicts
    if isinstance(recipe_data, dict):
        recipe_data = [recipe_data]

    for r in recipe_data:
        title = r.get("title", "Unknown Recipe")
        instructions = r.get("instructions", [])
        if isinstance(instructions, str):
            instructions = [s.strip() for s in instructions.split("\n") if s.strip()]
        ingredients = r.get("ingredients", detected_ingredients)
        if isinstance(ingredients, str):
            ingredients = [s.strip() for s in ingredients.split(",") if s.strip()]

        recipes_out.append({
            "title": title,
            "style": r.get("style"),
            "description": r.get("description"),
            "prep_time": r.get("prep_time"),
            "cook_time": r.get("cook_time"),
            "serving_suggestion": r.get("serving_suggestion"),
            "nutrition": r.get("nutrition"),
            "video_link": r.get("video_link"),
            "ingredients": ingredients,
            "instructions": instructions,
            "user_ingredients_used": r.get("user_ingredients_used"),
            "additional_ingredients_needed": r.get("additional_ingredients_needed"),
        })
    return recipes_out


import urllib.parse

def _generate_videos_and_links(recipes: list, background_tasks: BackgroundTasks, request: Request):
    """Generates the AI video for each recipe and assigns the local URL."""
    # Get base URL dynamically from request to support tunnel
    forwarded_host = request.headers.get("x-forwarded-host")
    if forwarded_host:
        proto = request.headers.get("x-forwarded-proto", "https")
        base_url = f"{proto}://{forwarded_host}"
    else:
        base_url = str(request.base_url).rstrip("/")

    for recipe in recipes:
        recipe_id = str(uuid.uuid4())[:8]
        output_path = f"static/videos/{recipe_id}.mp4"
        
        # Queue the video generation as a background task
        background_tasks.add_task(
            locked_create_video, 
            title=recipe.get('title', 'Delicious Recipe'),
            ingredients=recipe.get('ingredients', []),
            instructions=recipe.get('instructions', []),
            output_filename=output_path
        )
        
        recipe["video_link"] = f"{base_url}/videos/view/{recipe_id}"
        logger.info(f"Assigned custom AI video link for '{recipe.get('title')}'")


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

# Serve generated video files
os.makedirs("static/videos", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


# ──────────────────────────────────────────────
# GET /videos/view/{recipe_id}  –  Watch generated recipe video
# ──────────────────────────────────────────────
@app.get("/videos/view/{recipe_id}")
async def view_generated_video(recipe_id: str):
    """HTML page that plays the generated recipe video"""
    video_path = f"static/videos/{recipe_id}.mp4"
    if os.path.exists(video_path):
        return HTMLResponse(content=f'''
        <html><body style="margin:0; background:black; display:flex; justify-content:center; align-items:center; height:100vh;">
            <video width="100%" height="100%" controls autoplay>
              <source src="/{video_path}" type="video/mp4">
            </video>
        </body></html>
        ''')
    else:
        return HTMLResponse(content='''
        <html><head><meta http-equiv="refresh" content="3"></head>
        <body style="margin:0; background:#1A1A2E; color:white; display:flex; justify-content:center; align-items:center; height:100vh; font-family:sans-serif;">
            <div style="text-align:center;">
                <h2>🍳 Chef AI is cooking your video...</h2>
                <p>Please wait a few seconds, this page will auto-refresh.</p>
                <div style="margin-top:20px; width:40px; height:40px; border:4px solid #E94560; border-top-color:transparent; border-radius:50%; animation:spin 1s linear infinite; margin:20px auto;"></div>
            </div>
            <style>@keyframes spin { to { transform: rotate(360deg); } }</style>
        </body></html>
        ''')


# ──────────────────────────────────────────────
# POST /analyze  –  Image-based ingredient detection + recipe gen
# ──────────────────────────────────────────────
@app.post("/analyze")
async def analyze_image(
    background_tasks: BackgroundTasks,
    request: Request,
    file: UploadFile = File(...),
    meal_type: str = Form("Lunch"),
    cuisine: str = Form("Indian"),
    spice_level: str = Form("Medium"),
    food_style: str = Form("Curry")
):
    if not detector or not recommender:
        raise HTTPException(status_code=500, detail="Engines not ready")

    try:
        image_bytes = await file.read()

        logger.info("Running advanced ingredient detection...")
        detected_ingredients = detector.detect(image_bytes)
        if not detected_ingredients:
            detected_ingredients = ["vegetables"]

        logger.info(f"Retrieving/Generating best {cuisine} {food_style} for: {detected_ingredients}")
        recipe_data = recommender.recommend_recipe(
            detected_ingredients,
            cuisine=cuisine,
            spice_level=spice_level,
            meal_type=meal_type,
            food_style=food_style,
        )

        if not recipe_data:
            raise HTTPException(status_code=404, detail="No matching recipe found")

        formatted = _format_recipes_for_android(recipe_data, detected_ingredients)
        
        _generate_videos_and_links(formatted, background_tasks, request)
        
        logger.info(f"Returning {len(formatted)} recipes to client.")
        return {
            "success": len(formatted) > 0,
            "detected_ingredients": detected_ingredients,
            "recipes": formatted,
        }

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return {
            "success": False,
            "detected_ingredients": [],
            "recipes": [],
        }


# ──────────────────────────────────────────────
# POST /recipes/generate  –  Ingredient-text based recipe generation
# ──────────────────────────────────────────────
@app.post("/recipes/generate")
async def generate_recipes(req: RecipeGenerateRequest, request: Request, background_tasks: BackgroundTasks):
    if not recommender:
        raise HTTPException(status_code=500, detail="Recipe engine not ready")

    try:
        logger.info(f"[/recipes/generate] ingredients={req.ingredients}, cuisine={req.cuisine}, style={req.food_style}")

        recipe_data = recommender.recommend_recipe(
            req.ingredients,
            cuisine=req.cuisine,
            spice_level=req.spice_level,
            meal_type=req.meal_type,
            food_style=req.food_style,
        )

        if not recipe_data:
            return {
                "success": False,
                "detected_ingredients": req.ingredients,
                "recipes": [],
            }

        formatted = _format_recipes_for_android(recipe_data, req.ingredients)
        
        _generate_videos_and_links(formatted, background_tasks, request)

        logger.info(f"[/recipes/generate] Returning {len(formatted)} recipes to client.")
        return {
            "success": len(formatted) > 0,
            "detected_ingredients": req.ingredients,
            "recipes": formatted,
        }

    except Exception as e:
        logger.error(f"Error in /recipes/generate: {e}")
        return {
            "success": False,
            "detected_ingredients": req.ingredients,
            "recipes": [],
        }


@app.get("/health")
async def health():
    return {"status": "ok", "engines_active": detector is not None and recommender is not None}

# Serve Flutter Web App
if os.path.exists("static/web"):
    logger.info("Serving Flutter Web UI from static/web")
    # We mount this last so it doesn't intercept API routes
    app.mount("/", StaticFiles(directory="static/web", html=True), name="web")

if __name__ == "__main__":
    import uvicorn
    # Using 0.0.0.0 to allow access from Android Emulator/Devices
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
