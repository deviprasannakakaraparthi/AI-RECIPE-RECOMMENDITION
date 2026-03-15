from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.models.ai_manager import process_image_and_get_recipes

router = APIRouter()

@router.post("/detect")
async def detect(
    file: UploadFile = File(...),
    meal_type: Optional[str] = Form("Lunch"),
    cuisine: Optional[str] = Form("Indian"),
    spice_level: Optional[str] = Form("Medium")
):
    try:
        image_bytes = await file.read()
        # The smarter handler that returns real recipe metadata
        result = process_image_and_get_recipes(
            image_bytes, 
            meal_type=meal_type, 
            cuisine=cuisine, 
            spice_level=spice_level
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
