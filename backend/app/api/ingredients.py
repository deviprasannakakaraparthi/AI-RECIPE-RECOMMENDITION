from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from typing import Optional
from app.models.ai_manager import process_image_and_get_recipes

router = APIRouter()

from fastapi import BackgroundTasks

@router.post("/detect")
async def detect(
    background_tasks: BackgroundTasks,
    request: Request,
    file: UploadFile = File(...),
    meal_type: Optional[str] = Form("Lunch"),
    cuisine: Optional[str] = Form("Indian"),
    spice_level: Optional[str] = Form("Medium")
):
    try:
        image_bytes = await file.read()
        
        # Determine base url
        forwarded_host = request.headers.get("x-forwarded-host")
        if forwarded_host:
            proto = request.headers.get("x-forwarded-proto", "https")
            base_url = f"{proto}://{forwarded_host}"
        else:
            base_url = str(request.base_url).rstrip("/")
            
        # The smarter handler that returns real recipe metadata
        result = process_image_and_get_recipes(
            image_bytes, 
            meal_type=meal_type, 
            cuisine=cuisine, 
            spice_level=spice_level,
            bg_tasks=background_tasks,
            base_url=base_url
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
