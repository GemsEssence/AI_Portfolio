# AI-Powered Fashion Search Bot

## Introduction
**AI-Powered Fashion Search Bot** is a simple AI-driven system that allows users to upload images of fashion items and find visually similar products. The system provides similarity scores and returns the top-5 matching items with details.

---

## Objective
- Enable **visual search** for fashion products.  
- Provide **similarity scores** for uploaded images.  
- Return **top 5 visually matching items** with thumbnails.

---

## Solution
- **Backend:** FastAPI  
- **Feature Extraction:** BLIP model for generating image embeddings  
- **Vector Search:** In-memory vector database with cosine similarity  
- **Frontend:** Simple HTML + JavaScript interface for uploads and results display

---

## Challenges
- Handling **JSON serialization** for Numpy arrays and Torch tensors  
- Computing **accurate similarity** in real-time  
- Managing **uploads and thumbnails** efficiently

---

## Technology Stack
- **Python 3.12**  
- **FastAPI** for backend API  
- **PyTorch** & **Transformers (BLIP)** for image feature extraction  
- **NumPy** for vector operations  
- **HTML + JavaScript** for frontend interface  

---

## Results
- Users can upload images of fashion items  
- System returns **top 5 visually similar items**  
- Similarity scores and thumbnails displayed dynamically  
- Simple and extendable for future product integration  

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd fashion_search_bot
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
```

# Activate the environment:
```bash
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
uvicorn backend.main:app --reload
```

### Project Structure
```bash
fashion_search_bot/
│── backend/
│   ├── main.py
│   ├── services/
│   │   ├── caption.py
│   │   ├── vector_search.py
│   │   └── search.py
│   ├── static/
│   │   └── style.css
│   └── templates/
│       └── index.html  
│── .env
│── requirements.txt
```