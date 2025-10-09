from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse

app = FastAPI(title="AI Project Hub Dashboard")

# Mount the templates folder as static to serve images
app.mount("/static", StaticFiles(directory="templates"), name="static")

# Templates folder
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    apps = [
        {"name": "AI Interview App", "desc": "Smart interview Q&A system", "url": "http://127.0.0.1:8001"},
        {"name": "AI Safe Chat Guard", "desc": "Monitors & filters unsafe chat", "url": "http://127.0.0.1:8502"},
        {"name": "Fashion Search Bot", "desc": "Image-based fashion search", "url": "http://127.0.0.1:8003"},
        {"name": "LegalMind", "desc": "AI-powered legal document summarizer", "url": "http://127.0.0.1:8004"},
        {"name": "Object Detection", "desc": "YOLO-powered object detection", "url": "http://127.0.0.1:8005"},
        {"name": "Personalized Shopping Recommender", "desc": "AI recommendations for products", "url": "http://127.0.0.1:8006"},
        {"name": "Review Analyzer", "desc": "Sentiment and keyword analysis", "url": "http://127.0.0.1:5000"},
    ]
    return templates.TemplateResponse("index.html", {"request": request, "apps": apps})
