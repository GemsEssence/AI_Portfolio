# Visionary Hub 🚀

**Visionary Hub** is a professional-level **object detection web application** built using **FastAPI** and **YOLOv8**.  
It allows users to detect objects from **uploaded images** or **real-time camera input** and provides structured insights about detected objects.

---

## 📂 Project Structure

```bash
visionary_hub/
├── app/
│   ├── __init__.py
│   ├── orchestrator.py           # FastAPI app with routes & template rendering
│   ├── settings.py               # Configuration and device selection
│   ├── vision/
│   │   ├── __init__.py
│   │   └── visionary.py          # YOLO model handling & inference
│   ├── narratives/
│   │   ├── __init__.py
│   │   ├── request_schemas.py    # Input validation
│   │   └── response_schemas.py   # Response structure & validation
│   ├── insights/
│   │   ├── __init__.py
│   │   └── object_insights.py    # Map objects to descriptions & questions
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── image_reader.py       # Image preprocessing utility
│   │   └── logger.py             # Logging setup
│   ├── static/                   # Frontend assets
│   │   ├── styles.css
│   │   └── scripts.js
│   └── templates/                # HTML templates
│       └── index.html
├── data/
│   ├── artifacts/
│   │   └── yolov8n.pt            # Pre-trained YOLO model
│   └── mappings/
│       └── object_map.json       # Object descriptions & follow-up questions
├── tests/
│   ├── __init__.py
│   └── test_app.py               # Optional unit tests
├── .env                          # Environment variables
├── requirements.txt              # Python dependencies
└── README.md                     # Project overview & setup instructions

🔧 Features

    - Detect objects from uploaded images or real-time camera feed.

    - Retrieve structured information for each detected object:

    - Description

    - Usage

    - Benefits

    - Origin

    - Summary

    - Suggest follow-up questions for each detected object.

    Minimal frontend for interaction with FastAPI backend.

⚙️ Setup Instructions
1. Clone the repository
git clone <your-repo-url>
cd visionary_hub

2. Create and activate a Python virtual environment
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows

3. Install dependencies
pip install -r requirements.txt

4. Setup environment variables

Create a .env file in the root directory:

DEBUG=True

5. Download YOLO model

Place the pre-trained YOLO model yolov8n.pt in:

data/artifacts/

6. Run the application locally
uvicorn app.orchestrator:app --reload

7. Open in browser

    - Visit: http://127.0.0.1:8000

    - Upload Image: Upload any image to detect objects.

   -  Use Camera: Detect objects in real-time using your webcam.

📝 Notes

    - app/ contains all FastAPI modules and business logic.

    - static/ & templates/ manage frontend content.

    - data/ stores models and object mappings.

    - tests/ is optional for unit tests.

    - .env handles configuration such as debug mode.

    - requirements.txt includes all Python dependencies.

✅ Next Steps

    - Add more object mappings in object_map.json for richer insights.

    - Expand frontend features for enhanced interactivity.

    - Write unit tests in tests/ for robust development.

    - Deploy to cloud or local server for production use.

📚 References

    - YOLOv8 Documentation

    - FastAPI Documentation

    - Wikipedia Python Library


---
