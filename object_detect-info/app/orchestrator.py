from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from app.vision.visionary import Visionary
from app.insights.object_insights import get_object_details, get_cross_question
from app.utils.image_reader import read_image
from app.utils.logger import logger
from app.narratives.response_schemas import DetectionResponse

# app = FastAPI()
# visionary = Visionary()

# app.mount("/static", StaticFiles(directory="app/static"), name="static")
# templates = Jinja2Templates(directory="app/templates")

# @app.post("/camera-feed")
# async def camera_feed(frame: UploadFile = File(...)):
#     """
#     Detect objects in camera frame for live streaming
#     """
#     logger.info(f"Received camera frame: {frame.filename}")
#     image_bytes = await frame.read()
#     image = read_image(image_bytes)

#     detections = visionary.detect_with_coordinates(image)
#     logger.info(f"Live detections: {detections}")

#     return JSONResponse(content={"objects": detections})

# # @app.post("/camera-feed", response_model=DetectionResponse)
# # async def camera_feed(frame: UploadFile = File(...)):
# #     logger.info(f"Received camera frame: {frame.filename}")
# #     image_bytes = await frame.read()
# #     image = read_image(image_bytes)
# #     detected_classes = visionary.detect(image)
# #     logger.info(f"Detected classes from camera: {detected_classes}")

# #     details = get_object_details(detected_classes)
# #     print(details,"details----------------------------------------------------------------->")
# #     question = details[0]["question"] if detected_classes else "No objects detected."
    
# #     return DetectionResponse(objects=details, question=question)

# @app.post("/camera-feed")
# async def camera_feed(frame: UploadFile = File(...)):
#     """
#     For real-time detection: returns coordinates and labels only
#     """
#     logger.info(f"Received camera frame: {frame.filename}")
#     image_bytes = await frame.read()
#     image = read_image(image_bytes)

#     detections = visionary.detect_with_coordinates(image)
#     logger.info(f"Detected objects: {detections}")

#     return JSONResponse(content={"objects": detections})  


# @app.get("/", response_class=HTMLResponse)
# def index(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

# from fastapi import FastAPI, UploadFile, File
# from fastapi.responses import HTMLResponse, JSONResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from fastapi.requests import Request
# from app.vision.visionary import Visionary
# from app.utils.image_reader import read_image
# from app.utils.logger import logger

app = FastAPI()
visionary = Visionary()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    logger.info(f"Received image upload: {file.filename}")
    image_bytes = await file.read()
    image = read_image(image_bytes)
    detections = visionary.detect_with_coordinates(image)
    detected_classes = [obj["name"] for obj in detections]
    details = get_object_details(detected_classes)  # <-- your GPT logic
    # Merge description into detections
    for obj, detail in zip(detections, details):
        obj["description"] = detail.get("description", "")

    return JSONResponse(content={"objects": details})


@app.post("/camera-feed")
async def camera_feed(frame: UploadFile = File(...)):
    logger.info(f"Received camera frame: {frame.filename}")
    image_bytes = await frame.read()
    image = read_image(image_bytes)
    detections = visionary.detect_with_coordinates(image)
    logger.info(f"Live detections: {detections}")
    return JSONResponse(content={"objects": detections})


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

