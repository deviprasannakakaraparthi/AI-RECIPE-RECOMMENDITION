from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from app.api import ingredients, recipes, videos
from app.models.ai_manager import process_image_and_get_recipes

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Recipe Recommendation API")

# Allow requests from Web App Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount directory to serve static videos directly
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routers
app.include_router(ingredients.router, prefix="/ingredients", tags=["Ingredients"])
app.include_router(recipes.router, prefix="/recipes", tags=["Recipes"])
app.include_router(videos.router, prefix="/videos", tags=["Videos"])

from fastapi import BackgroundTasks

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
    """Main endpoint for Android app"""
    try:
        image_bytes = await file.read()
        
        # Determine base url
        forwarded_host = request.headers.get("x-forwarded-host")
        if forwarded_host:
            proto = request.headers.get("x-forwarded-proto", "https")
            base_url = f"{proto}://{forwarded_host}"
        else:
            base_url = str(request.base_url).rstrip("/")

        # Use our high-quality detector + 40k dataset retriever
        result = process_image_and_get_recipes(
            image_bytes, 
            meal_type=meal_type, 
            cuisine=cuisine, 
            spice_level=spice_level,
            food_style=food_style,
            bg_tasks=background_tasks,
            base_url=base_url
        )
        
        if "error" in result:
             raise HTTPException(status_code=400, detail=result["error"])

        return {
            "success": True,
            "detected_ingredients": result.get("detected_ingredients", []),
            "recipes": result.get("recipes", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount Flutter Web App build directory (at the very end so other routes match first)
import os
build_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web_build")
if os.path.exists(build_path):
    app.mount("/", StaticFiles(directory=build_path, html=True), name="ui")
else:
    @app.get("/")
    def root():
        return {"message": "AI Recipe API is running! UI directory 'web_build' not found."}
