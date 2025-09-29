# Visionary Hub

**Visionary Hub** is a professional-level object detection web application built using **FastAPI** and **YOLO**. It allows users to detect objects in images or real-time camera input and provides structured information about detected objects.

---

## 📂 Project Structure

visionary_hub/
├── app/
│   ├── __init__.py
│   ├── orchestrator.py           # Main FastAPI app with routes and template rendering
│   ├── settings.py              # Configuration and device selection logic
│   ├── vision/
│   │   ├── __init__.py
│   │   └── visionary.py         # YOLO model handling and inference
│   ├── narratives/
│   │   ├── __init__.py
│   │   ├── request_schemas.py   # Input validation for API requests
│   │   └── response_schemas.py  # Response structure and validation
│   ├── insights/
│   │   ├── __init__.py
│   │   └── object_insights.py   # Map objects to descriptions and follow-up questions
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── image_reader.py      # Image preprocessing utility
│   │   └── logger.py            # Logging setup
│   ├── static/                  # Frontend assets like CSS & JavaScript
│   │   ├── styles.css
│   │   └── scripts.js
│   └── templates/               # HTML templates
│       └── index.html
├── data/
│   ├── artifacts/
│   │   └── yolov8n.pt           # Pre-trained YOLO model
│   └── mappings/
│       └── object_map.json      # Object descriptions and follow-up questions
├── tests/
│   ├── __init__.py
│   └── test_app.py              # Unit tests (optional but recommended)
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
└── README.md                    # Project overview and setup instructions

## 🔧 Features
Detect objects from uploaded images or real-time camera feed.

Retrieve structured information for each detected object:

Description

Usage

Benefits

Origin

Summary

Suggest follow-up questions for each detected object.

Minimal frontend for interaction with FastAPI backend.

## ⚙️ Setup Instructions
Clone the repository:


git clone <your-repo-url>
cd visionary_hub
Create a Python virtual environment and activate it:


## Copy code
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

## Install dependencies:
pip install -r requirements.txt

## Setup environment variables:
Create a .env file with:

env
DEBUG=True
Download YOLO model:

Place the pre-trained YOLO model yolov8n.pt in data/artifacts/.

## Run the application locally:

uvicorn app.orchestrator:app --reload
Open in browser:

Visit http://127.0.0.1:8000 to use:

## Upload Image: Upload any image to detect objects.

## Use Camera: Detect objects in real-time using your webcam.

📝 Notes
app/ contains all FastAPI modules and business logic.

static/ & templates/ manage frontend content.

data/ stores models and object mappings.

tests/ is optional for writing unit tests to ensure endpoints and logic work as expected.

.env handles configuration such as debug mode.

requirements.txt includes all Python dependencies.

✅ Next Steps
Add more object mappings in object_map.json for richer insights.

Expand frontend features for enhanced interactivity.

Write unit tests in tests/ for robust development.

Deploy to cloud or local server for production use.

📚 References
YOLOv8 Documentation

FastAPI Documentation

Wikipedia Python Library

yaml
Copy code

---

If you want, I can also **update `object_insights.py` and `orchestrator.py`** so that it integrates perfectly with this README setup, including **camera input, image upload, and Wikipedia-based object descriptions with cleaned output**.  

Do you want me to do that next?