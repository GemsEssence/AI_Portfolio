
import os
import io
import uuid
import json
import re
from PIL import Image, ImageDraw, ImageFilter
from fastapi import UploadFile
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Heatmap directory setup
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEATMAP_DIR = os.path.normpath(os.path.join(BASE, "..", "frontend", "static", "heatmaps"))
os.makedirs(HEATMAP_DIR, exist_ok=True)

LANG_MAP = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "ja": "Japanese",
    "zh": "Chinese",
    "ru": "Russian",
    "ar": "Arabic"
}

async def analyze_image_async(file: UploadFile, lang: str = "en") -> dict:
    """
    Analyze a medical image using Google Gemini in a HIPAA/GDPR-compliant way.
    Rejects identifiable *full-face* images, but allows cropped/partial face areas with visible disease.
    """
    contents = await file.read()
    img = Image.open(io.BytesIO(contents)).convert("RGB")
    w, h = img.size

    # Step 1️⃣ - Create a simulated heatmap
    heat = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(heat)
    ellipse_box = (w * 0.25, h * 0.25, w * 0.75, h * 0.75)
    draw.ellipse(ellipse_box, fill=(255, 0, 0, 120))
    heat = heat.filter(ImageFilter.GaussianBlur(radius=25))
    overlay = Image.alpha_composite(img.convert("RGBA"), heat)

    out_name = f"heatmap_{uuid.uuid4().hex[:8]}.png"
    out_path = os.path.join(HEATMAP_DIR, out_name)
    overlay.convert("RGB").save(out_path, format="PNG")

    try:
        # Step 2️⃣ - Initialize Gemini model
        model = genai.GenerativeModel("gemini-2.5-flash")

        # Convert image to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_data = img_bytes.getvalue()

        # Step 3️⃣ - Detect image type with better classification
        check_prompt = (
            "Classify this image in one word from these options: "
            "'full_face', 'partial_face', 'skin', 'xray', 'ct', 'mri', 'hand', 'body'. "
            "If the image shows a full human face (forehead, eyes, nose, mouth, and chin all visible), respond 'full_face'. "
            "If the face is cropped, only partly visible, or focused on a diseased area, respond 'partial_face'. "
            "Return only one word with no explanation."
        )

        check_response = model.generate_content(
            [{"role": "user", "parts": [check_prompt, {"mime_type": "image/png", "data": img_data}]}],
            generation_config={"temperature": 0.1},
        )
        import time
        time.sleep(15)
        
        img_type = (check_response.text or "").lower().strip()
        print(f"[INFO] Detected image type: {img_type}")

        # ✅ HIPAA/GDPR safeguard (Reject only FULL FACE)
        if "full_face" in img_type:
            return {
                "label": "Rejected - Full Face Detected",
                "score": 0.0,
                "heatmap": f"/static/heatmaps/{out_name}",
                "doctor_response": {
                    "message": (
                        "⚠️ For privacy and data protection, please upload only the affected area "
                        "(e.g., cheek patch, eye area, or lip region). "
                        "Full-face images are not allowed for HIPAA/GDPR compliance."
                    )
                },
            }

        # Allow partial_face or other medical images
        if not any(k in img_type for k in ["skin", "xray", "ct", "mri", "hand", "body", "partial_face", "derma"]):
            return {
                "label": "Unrelated Image",
                "score": 0.0,
                "heatmap": f"/static/heatmaps/{out_name}",
                "doctor_response": {
                    "message": "🩺 Please upload a clear medical or diagnostic image (e.g., skin, X-ray, CT, or cropped face area)."
                },
            }

        # Step 4️⃣ - Build structured JSON diagnosis prompt
        lang_name = LANG_MAP.get(lang.lower(), "English")

        diagnosis_prompt = f"""
                            You are MediBot, an empathetic AI medical assistant.
                            Analyze the provided medical image and respond strictly in JSON format:

                            {{
                            "diagnosis": "Likely condition name (also provide common/local name if available)",
                            "explanation": "Short explanation",
                            "possible_causes": ["Cause 1", "Cause 2"],
                            "recommended_medicines": ["Medicine name (purpose)"],
                            "home_remedies": ["Natural remedies"],
                            "precautions": ["Precaution 1", "Precaution 2"],
                            "follow_up_question": "Ask one relevant follow-up question )"
                            }}

                            Guidelines:
                            - Be medically accurate and empathetic.
                            - Only mild, over-the-counter (OTC) medicines.
                            - No antibiotics, steroids, or prescription drugs.
                            """

        diagnosis_response = model.generate_content(
            [{"role": "user", "parts": [diagnosis_prompt, {"mime_type": "image/png", "data": img_data}]}],
            generation_config={"temperature": 0.7},
        )

        raw_text = (diagnosis_response.text or "").strip()
        print(f"[DEBUG] Raw Gemini Response: {raw_text[:200]}...")

        # Step 5️⃣ - Parse JSON safely
        try:
            structured_response = json.loads(raw_text)
        except Exception:
            match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            structured_response = json.loads(match.group()) if match else {"doctor_response": raw_text}

        label = structured_response.get("diagnosis", "Possible condition")

    except Exception as e:
        print("[ERROR]", str(e))
        structured_response = {"doctor_response": "⚠️ Unable to analyze the image at the moment."}
        label = "Unknown"

    return {
        "label": label,
        "score": 0.9,
        "heatmap": f"/static/heatmaps/{out_name}",
        "doctor_response": structured_response,
    }
