from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers import text_input, voice_input, image_input

app = FastAPI(title="AI MediBot", version="1.0")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static + Templates (fixed paths)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Routers
app.include_router(text_input.router)
app.include_router(voice_input.router)
app.include_router(image_input.router)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
