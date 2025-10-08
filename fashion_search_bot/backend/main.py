import os
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from .services.caption import generate_caption_and_features
from .services.search import search_products

# Initialize FastAPI app
app = FastAPI()
load_dotenv()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="backend/static"), name="static")
templates = Jinja2Templates(directory="backend/templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """
    Render the main HTML page.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload-dress/")
async def upload_dress(file: UploadFile = File(...)):
    """
    Receive an uploaded image, generate caption/features,
    search products, and return them to frontend.
    """
    try:
        # Read uploaded image bytes
        image_bytes = await file.read()
        print(f"Received file: {file.filename}, size: {len(image_bytes)} bytes")

        # Generate caption (optional: you can display it)
        description, _ = generate_caption_and_features(image_bytes)
        print(f"Generated caption: {description}")

        # Search products based on caption
        scraped_products = search_products(description, limit=10)
        print(f"Scraped {len(scraped_products)} products from search.")

        # Return products directly (no vector search)
        return JSONResponse({"description": description, "products": scraped_products})

    except Exception as e:
        print(f"Error in upload_dress: {e}")
        return JSONResponse({"error": str(e)})
