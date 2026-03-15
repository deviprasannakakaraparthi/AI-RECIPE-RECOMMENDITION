from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from app.api import ingredients, recipes, videos
from app.models.ai_manager import process_image_and_get_recipes

app = FastAPI(title="AI Recipe Recommendation API")

# Include API routers
app.include_router(ingredients.router, prefix="/ingredients", tags=["Ingredients"])
app.include_router(recipes.router, prefix="/recipes", tags=["Recipes"])
app.include_router(videos.router, prefix="/videos", tags=["Videos"])

@app.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    meal_type: str = Form("Lunch"),
    cuisine: str = Form("Indian"),
    spice_level: str = Form("Medium"),
    food_style: str = Form("Curry")
):
    """Main endpoint for Android app"""
    try:
        image_bytes = await file.read()
        # Use our high-quality detector + 40k dataset retriever
        result = process_image_and_get_recipes(
            image_bytes, 
            meal_type=meal_type, 
            cuisine=cuisine, 
            spice_level=spice_level,
            food_style=food_style
        )
        
        if "error" in result:
             raise HTTPException(status_code=400, detail=result["error"])

        # Map to the structure expected by the Android app
        # The Android app expects: matched_recipe.Category for title and generated_steps for instructions
        return {
            "success": True,
            "detected_ingredients": result["detected_ingredients"],
            "matched_recipe": {
                "Category": result["recipe"]["title"], # Android uses this for Title
                "Title": result["recipe"]["title"],
                "Ingredients": result["recipe"]["ingredients"],
                "Cuisine": cuisine
            },
            "generated_steps": result["recipe"]["instructions"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "AI Recipe Recommendation API is running!"}
