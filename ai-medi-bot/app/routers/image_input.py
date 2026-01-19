from fastapi import APIRouter, UploadFile, File, Query
from app.services import image_analyzer
from app.utils.translator import translate_text

router = APIRouter(prefix="/image", tags=["image"])

@router.post("/")
async def analyze_image(
    file: UploadFile = File(...),
    lang: str = Query("en", description="Language for translation (e.g., en, hi, fr, ja)")
):
    """
    🩺 Analyze an uploaded medical image and return doctor-style diagnostic details.
    Optionally translate the AI response to the selected language.
    """
    # Step 1️⃣ — Run the image analyzer model
    result = await image_analyzer.analyze_image_async(file, lang=lang)

    # Step 2️⃣ — Extract AI doctor response
    doctor_reply = result.get("doctor_response", {})

    # Step 3️⃣ — Translate all text fields if needed
    if lang and lang.lower() != "en" and isinstance(doctor_reply, dict):
        for key, value in doctor_reply.items():
            if isinstance(value, str):
                doctor_reply[key] = await translate_text(value, lang)

            elif isinstance(value, list):
                translated_list = []
                for v in value:
                    translated_list.append(await translate_text(v, lang))
                doctor_reply[key] = translated_list


    # Step 4️⃣ — Return translated + original data
    result["doctor_response"] = doctor_reply
    print(f"[DEBUG] Image analysis result (lang={lang}):", result)

    return {
        "analysis": result,
        "reply": doctor_reply
    }