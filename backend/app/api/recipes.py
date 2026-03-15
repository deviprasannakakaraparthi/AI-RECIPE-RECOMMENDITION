from fastapi import APIRouter, Request, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import uuid

router = APIRouter()

class RecipeRequest(BaseModel):
    ingredients: List[str]
    recipe_name: Optional[str] = None
    meal_type: Optional[str] = "Lunch"
    cuisine: Optional[str] = "Indian"
    spice_level: Optional[str] = "Medium"
    food_style: Optional[str] = "Curry"

from app.models.ai_manager import recipe_engine
from app.models.video_maker import create_recipe_video_sync

@router.post("/generate")
def recipe(body: RecipeRequest, request: Request, background_tasks: BackgroundTasks):
    """
    Expert Recipe Generation.
    Uses the high-accuracy RecipeIntelligence engine.
    """
    # Use the robust engine for all requests
    # We pass target_name as food_style if it's provided to guide the search
    matches = recipe_engine.recommend_recipe(
        body.ingredients, 
        cuisine=body.cuisine, 
        spice_level=body.spice_level, 
        meal_type=body.meal_type, 
        food_style=body.recipe_name if body.recipe_name else body.food_style
    )
    
    if matches:
        # Determine base url
        forwarded_host = request.headers.get("x-forwarded-host")
        if forwarded_host:
            proto = request.headers.get("x-forwarded-proto", "https")
            base_url = f"{proto}://{forwarded_host}"
        else:
            base_url = str(request.base_url).rstrip("/")

        # Process matches to add video links
        for recipe_match in matches:
            recipe_id = str(uuid.uuid4())[:8]
            output_path = f"static/videos/{recipe_id}.mp4"
            
            # Queue background task to generate the recipe video
            background_tasks.add_task(
                create_recipe_video_sync, 
                title=recipe_match.get('title', 'Delicious Recipe'),
                ingredients=recipe_match.get('ingredients', []),
                instructions=recipe_match.get('instructions', []),
                output_filename=output_path
            )
            
            recipe_match["video_link"] = f"{base_url}/videos/view/{recipe_id}"
            
        return {
            "recipes": matches,
            "success": True,
            "message": "Generated expert recipes."
        }
    
    return {"error": "Could not generate or match a recipe.", "success": False}

