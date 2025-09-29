# 📄 LegalMind – RAG Pipeline for Document Analysis

A **Retrieval-Augmented Generation (RAG)** pipeline for analyzing legal documents using your own LLM and vector retrieval (FAISS).

---

## 🏗 Pipeline Overview

User Query
|
v
+-----------+
| Classify | --> Casual Chat? --> LLM only
+-----------+
|
v
+-----------+
| Embed | <-- chunks embedded here
+-----------+
|
v
+-----------+
| Retrieve | --> FAISS or other vector DB
+-----------+
|
v
+-----------+
| LLM | <-- context chunks from retrieved embeddings
+-----------+
|
v
+-----------+
| Post-Proc | <-- map answer to source/page
+-----------+
|
v
User Output


---

## 📂 Folder Structure

LegalMind/
├─ backend/ # Backend utilities
│ └─ utils.py
├─ frontend/ # Web interface
│ ├─ index.html
│ ├─ style.css
│ └─ script.js
├─ rawdata/ # PDFs to process
├─ app.py # FastAPI entrypoint
├─ requirements.txt # Python dependencies
├─ venv/ # Virtual environment
├─ Dockerfile
├─ .gitignore
├─ README.md


---

## 🚀 Run Locally

```bash
# Create virtual environment
python -m venv venv

# Activate environment
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Run backend server
uvicorn app:app --reload

---
