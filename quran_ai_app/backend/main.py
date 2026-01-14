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
