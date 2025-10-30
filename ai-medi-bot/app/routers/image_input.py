from fastapi import APIRouter, UploadFile, File
from app.services import image_analyzer

router = APIRouter(prefix="/image", tags=["image"])

@router.post("/")
async def analyze_image(file: UploadFile = File(...)):
    result = await image_analyzer.analyze_image_async(file)
    print(result, "============analyze_image_async")
    return {
        "analysis": result,
        "reply": result["doctor_response"]
    }
