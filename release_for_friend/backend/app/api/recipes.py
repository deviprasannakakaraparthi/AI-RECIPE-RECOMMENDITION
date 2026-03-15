from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from app.models.ai_manager import generate_recipe_steps
from app.utils.similarity import recommend_recipes_full

router = APIRouter()

class RecipeRequest(BaseModel):
    ingredients: List[str]
    recipe_name: Optional[str] = None
    meal_type: Optional[str] = "Lunch"
    cuisine: Optional[str] = "Indian"
    spice_level: Optional[str] = "Medium"
    food_style: Optional[str] = "Curry"

from app.models.ai_manager import recipe_engine

@router.post("/generate")
def recipe(request: RecipeRequest):
    """
    Expert Recipe Generation.
    Uses the high-accuracy RecipeIntelligence engine.
    """
    # Use the robust engine for all requests
    # We pass target_name as food_style if it's provided to guide the search
    match = recipe_engine.recommend_recipe(
        request.ingredients, 
        cuisine=request.cuisine, 
        spice_level=request.spice_level, 
        meal_type=request.meal_type, 
        food_style=request.recipe_name if request.recipe_name else request.food_style
    )
    
    if match:
        return {
            "title": match["title"],
            "ingredients": match["ingredients"],
            "instructions": match["instructions"],
            "suggestion": "Expertly matched and generated." if match.get("is_ai_generated") else "Matched from our authentic database.",
            "success": True
        }
    
    return {"error": "Could not generate or match a recipe.", "success": False}

