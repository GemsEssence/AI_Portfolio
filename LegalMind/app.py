from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from backend import utils

app = FastAPI(title="Legal Assistant")

frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

RAW_FOLDER = "rawdata"
os.makedirs(RAW_FOLDER, exist_ok=True)
utils.build_index_from_folder(RAW_FOLDER)

class Query(BaseModel):
    question: str
    top_k: int = 5

@app.post("/ask")
async def ask(q: Query):
    question = q.question.strip()
    answer, retrieved = utils.answer_query(question, top_k=q.top_k)

    if not answer or answer.upper() in ["INSUFFICIENT CONTEXT", "", "DISCLOSED."]:
        return {"answer": "❌ Sorry, I could not find a relevant answer to your query.", "retrieval": []}
        
    if answer == question:
        return {"answer": "❌ Sorry, I could not find a relevant answer to your query.", "retrieval": []}


    retrieval = [
        {
            "source": r.get("source", "unknown"),
            "page": r.get("page", "-"),
            "score": round(r.get("score", 0.0), 3),
            "text": (r.get("text") or "")[:200] + "..."
        }
        for r in retrieved
    ]
    return {"answer": answer, "retrieval": retrieval}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF uploads supported")
    contents = await file.read()
    saved_name = file.filename
    dest = os.path.join(RAW_FOLDER, saved_name)
    with open(dest, "wb") as f:
        f.write(contents)
    added = utils.add_pdf_to_index(contents, filename=saved_name)
    return {"status": "ok", "indexed_chunks": added}
