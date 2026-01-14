import os
import io
import logging
import google.generativeai as genai
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pdf2image import convert_from_bytes
from pathlib import Path
from dotenv import load_dotenv  # <-- Add this
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quran_ai")
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.error("GEMINI_API_KEY not found in environment variables!")
else:
    genai.configure(api_key=api_key)
# Use your key - recommend moving to environment variable later
# Use gemini-1.5-flash or gemini-2.0-flash-exp for high speed and accuracy
model = genai.GenerativeModel('gemini-2.5-flash')

app = FastAPI(title="Hanuman Chalisa AI")

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def index():
    return (FRONTEND_DIR / "index.html").read_text(encoding="utf-8")

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    try:
        pdf_bytes = await file.read()
        images = convert_from_bytes(pdf_bytes, dpi=300, first_page=1, last_page=1)
        page = images[0]

        # Convert to bytes for Gemini
        img_byte_arr = io.BytesIO()
        page.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()

        # prompt = """
        # Extract the Arabic text from this image.
        # - Correct any OCR spelling errors based on context.
        # - Maintain the original verse structure (Ayaat/Couplets).
        # - Return ONLY the Arabic text without any explanations.
        # """
        prompt = """
            Extract the main Arabic text from this image while following these rules:
            1. EXCLUDE all Headers, Footers, Page Numbers, and Marginalia.
            2. Maintain the original visual structure of the verses (Ayaat/Couplets).
            3. Correct OCR spelling errors based on Arabic context.
            4. Return ONLY the main body text. No explanations, no markdown, and no layout descriptions.
        """
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": img_bytes}
        ])
        
        # Clean text and split into words for the frontend's tracking logic
        text_content = response.text.strip()
        # Remove special characters but keep Hindi script
        words = text_content.split() 

        return {"status": "ok", "words": words, "raw_text": text_content}

    except Exception as e:
        logger.error(f"Error: {e}")
        return {"status": "error", "error": str(e)}