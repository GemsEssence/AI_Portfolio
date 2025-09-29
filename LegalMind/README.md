# 📄 LegalMind – RAG Pipeline for Document Analysis

A **Retrieval-Augmented Generation (RAG)** pipeline for analyzing legal documents using your own LLM and vector retrieval (FAISS).

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
