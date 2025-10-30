``` bash 
ai_medibot/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app entry point
│   │
│   ├── routers/                    # Routes for modular API endpoints
│   │   ├── __init__.py
│   │   ├── text_input.py           # Handles chat/text interactions
│   │   ├── voice_input.py          # Handles voice-to-text input
│   │   └── image_input.py          # Handles image uploads and analysis
│   │
│   ├── services/                   # Core AI logic & external model integrations
│   │   ├── __init__.py
│   │   ├── nlp_model.py            # Chat and text understanding (Gemini)
│   │   ├── voice_transcriber.py    # Speech-to-text processing
│   │   └── image_analyzer.py       # Image diagnosis + heatmap generator
│   │
│   └── utils/                      # Helper modules for translation and security
│       ├── __init__.py
│       ├── translator.py
│       └── security.py
│
├── frontend/
│   ├── templates/
│   │   └── index.html              # Frontend UI with chat and upload interface
│   └── static/
│       ├── style.css               # Custom styling
│       └── script.js               # Chat & image upload logic
│
├── .env                            # Store your Gemini / API keys here
├── requirements.txt
└── README.md

```

### 🧩 Installation & Setup

### 1️⃣ Clone the repository
 ``` bash
git clone https://github.com/your-username/ai_medibot.git
cd ai_medibot
```
### Create and activate a virtual environment
``` bash
python -m venv venv
source venv/bin/activate        # (On Windows: venv\Scripts\activate)
```

### Install dependencies
``` bash
pip install -r requirements.txt
```

### Create a .env file and add your API key
``` bash
GOOGLE_API_KEY=your_gemini_api_key_here
```


### Running the App

Start the FastAPI development server:
``` bash
uvicorn app.main:app --reload

```

### Now open your browser and visit:
👉 http://127.0.0.1:8000
