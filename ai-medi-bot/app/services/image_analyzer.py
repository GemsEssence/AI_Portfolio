# import os
# import io
# import uuid
# import base64
# from PIL import Image, ImageDraw, ImageFilter
# from fastapi import UploadFile
# from openai import OpenAI
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# HEATMAP_DIR = os.path.normpath(os.path.join(BASE, "..", "frontend", "static", "heatmaps"))
# os.makedirs(HEATMAP_DIR, exist_ok=True)


# async def analyze_image_async(file: UploadFile) -> dict:
#     """
#     Analyze uploaded image using AI for skin condition prediction and
#     generate structured doctor-style feedback (diagnosis, medicine, advice).
#     """
#     contents = await file.read()
#     img = Image.open(io.BytesIO(contents)).convert("RGB")
#     w, h = img.size

#     # --- Step 1: Create simulated heatmap overlay ---
#     heat = Image.new("RGBA", img.size, (0, 0, 0, 0))
#     draw = ImageDraw.Draw(heat)
#     ellipse_box = (w * 0.25, h * 0.25, w * 0.75, h * 0.75)
#     draw.ellipse(ellipse_box, fill=(255, 0, 0, 120))
#     heat = heat.filter(ImageFilter.GaussianBlur(radius=25))

#     overlay = Image.alpha_composite(img.convert("RGBA"), heat)
#     out_name = f"heatmap_{uuid.uuid4().hex[:8]}.png"
#     out_path = os.path.join(HEATMAP_DIR, out_name)
#     overlay.convert("RGB").save(out_path, format="PNG")

#     # --- Step 2: Use GPT-4o for structured analysis ---
#     try:
#         buffered = io.BytesIO()
#         img.save(buffered, format="PNG")
#         img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

#         prompt = """
#         You are an experienced, friendly online dermatologist named MediBot.
#         Analyze the given skin image realistically and respond in a structured JSON format as below:

#         {
#           "diagnosis": "Name of likely skin condition",
#           "explanation": "Brief layman-friendly description of what this condition looks like and feels like.",
#           "possible_causes": ["Cause 1", "Cause 2", "Cause 3"],
#           "recommended_medicines": ["Medicine name (purpose)", "Cream or tablet suggestions (optional)"],
#           "home_remedies": ["Natural or gentle remedies", "Lifestyle tips"],
#           "precautions": ["Precaution 1", "Precaution 2"],
#           "follow_up_question": "Ask a relevant follow-up question to the user"
#         }

#         Rules:
#         - Always act confident and helpful.
#         - Don’t say “consult a dermatologist” unless it looks severe.
#         - Suggest both mild OTC medicines and daily care.
#         - Use warm, human, friendly language.
#         """

#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are a kind and confident AI dermatologist."},
#                 {
#                     "role": "user",
#                     "content": [
#                         {"type": "text", "text": prompt},
#                         {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
#                     ]
#                 }
#             ],
#             temperature=0.85,
#         )

#         raw = response.choices[0].message.content.strip()

#         # Try parsing JSON output (if valid)
#         import json
#         try:
#             structured_response = json.loads(raw)
#         except json.JSONDecodeError:
#             structured_response = {"doctor_response": raw}

#         label = structured_response.get("diagnosis", "Possible skin condition")
#         confidence = 0.85

#     except Exception as e:
#         structured_response = {
#             "error": str(e),
#             "doctor_response": "⚠️ Unable to analyze image or generate medical feedback right now."
#         }
#         label = "Unknown"
#         confidence = 0.0

#     # --- Step 3: Return result ---
#     return {
#         "label": label,
#         "score": confidence,
#         "heatmap": f"/static/heatmaps/{out_name}",
#         "doctor_response": structured_response
#     }
import os
import io
import uuid
import json
from PIL import Image, ImageDraw, ImageFilter
from fastapi import UploadFile
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEATMAP_DIR = os.path.normpath(os.path.join(BASE, "..", "frontend", "static", "heatmaps"))
os.makedirs(HEATMAP_DIR, exist_ok=True)


async def analyze_image_async(file: UploadFile) -> dict:
    """
    Analyze uploaded image using Google Gemini.
    If image is not a human skin photo, gracefully reject it.
    Otherwise, return structured doctor-style feedback.
    """
    contents = await file.read()
    img = Image.open(io.BytesIO(contents)).convert("RGB")
    w, h = img.size

    # --- Step 1: Create simulated heatmap overlay ---
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
        # ✅ Use Gemini model
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Convert image to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # --- Step 2: Check if image is skin or unrelated ---
        check_prompt = (
            "Look at this image and identify what it mainly shows. "
            "Respond in one word like 'skin', 'face', 'fruit', 'object', 'animal', or 'other'."
        )

        check_response = model.generate_content(
            [
                {"role": "user", "parts": [check_prompt, {"mime_type": "image/png", "data": img_bytes.getvalue()}]}
            ],
            generation_config={"temperature": 0.2},
        )

        img_type = check_response.text.lower().strip()
        print(f"[INFO] Detected image type: {img_type}")

        # --- Step 3: If not a skin/face/body image, return rejection message ---
        if not any(keyword in img_type for keyword in ["skin", "face", "hand", "body", "derma"]):
            return {
                "label": "Unrelated Image",
                "score": 0.0,
                "heatmap": f"/static/heatmaps/{out_name}",
                "doctor_response": {
                    "message": "🩺 I'm not trained to analyze this type of image. Please upload a clear photo of human skin for medical evaluation."
                }
            }

        # --- Step 4: Proceed with medical-style analysis ---
        diagnosis_prompt = """
        You are an experienced, friendly online dermatologist named MediBot.
        Analyze the given skin image and respond in the following JSON format:

        {
          "diagnosis": "Name of likely skin condition",
          "explanation": "Brief layman-friendly description.",
          "possible_causes": ["Cause 1", "Cause 2"],
          "recommended_medicines": ["Medicine name (purpose)"],
          "home_remedies": ["Natural remedies"],
          "precautions": ["Precaution 1", "Precaution 2"],
          "follow_up_question": "Ask a relevant follow-up question"
        }

        Rules:
        - Always be confident and empathetic.
        - Suggest mild OTC medicines and daily skincare.
        - Avoid saying “consult a dermatologist” unless absolutely necessary.
        - Keep tone human and natural.
        """

        diagnosis_response = model.generate_content(
            [
                {"role": "user", "parts": [diagnosis_prompt, {"mime_type": "image/png", "data": img_bytes.getvalue()}]}
            ],
            generation_config={"temperature": 0.8},
        )

        raw_text = diagnosis_response.text.strip()

        try:
            structured_response = json.loads(raw_text)
        except json.JSONDecodeError:
            structured_response = {"doctor_response": raw_text}

        label = structured_response.get("diagnosis", "Possible skin condition")
        confidence = 0.85

    except Exception as e:
        structured_response = {
            "error": str(e),
            "doctor_response": "⚠️ Unable to analyze image or generate medical feedback right now."
        }
        label = "Unknown"
        confidence = 0.0

    return {
        "label": label,
        "score": confidence,
        "heatmap": f"/static/heatmaps/{out_name}",
        "doctor_response": structured_response
    }
