import os, fitz
from pdf2image import convert_from_path
import pytesseract
import faiss
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import re

# ============================
# Config
# ============================
EMB_MODEL = "intfloat/e5-base-v2"
GEN_MODEL = "google/flan-t5-base"
CHUNK_SIZE = 350
CHUNK_OVERLAP = 50  
RELEVANCE_THRESHOLD = 0.35
MAX_TOKENS_CONTEXT = 1000  # maximum cumulative tokens for LLM

# ============================
# Globals
# ============================
emb_model = SentenceTransformer(EMB_MODEL)
index = None
chunks = []
metas = []

clf = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

device = "cuda" if torch.cuda.is_available() else "cpu"
tok = AutoTokenizer.from_pretrained(GEN_MODEL)
llm = AutoModelForSeq2SeqLM.from_pretrained(GEN_MODEL).to(device)

# ============================
# Helpers
# ============================
# def _chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
#     words = text.split()
#     step = size - overlap
#     return [" ".join(words[i:i+size]) for i in range(0, len(words), step)]


def _chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """
    Paragraph-aware chunking with sliding window.
    Keeps paragraphs together and splits only if necessary.
    """
    import re

    paragraphs = [p.strip() for p in re.split(r'\n{1,2}', text) if p.strip()]
    chunks = []
    current_chunk = []
    current_len = 0

    for para in paragraphs:
        para_words = para.split()
        para_len = len(para_words)

        # Split long paragraphs internally
        if para_len > size:
            for i in range(0, para_len, size - overlap):
                subchunk = para_words[i:i+size]
                chunks.append(" ".join(subchunk))
        else:
            if current_len + para_len <= size:
                current_chunk.extend(para_words)
                current_len += para_len
            else:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                # Start new chunk with sliding overlap
                overlap_words = current_chunk[-overlap:] if overlap <= len(current_chunk) else current_chunk
                current_chunk = overlap_words + para_words
                current_len = len(current_chunk)

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    print(chunks,"chunks=================================================================>")
    return chunks


def _extract_text_from_pdf(path):
    doc = fitz.open(path)
    pages_text = []
    for i in range(len(doc)):
        page = doc.load_page(i)
        text = page.get_text().strip()
        if len(text) < 20:
            try:
                images = convert_from_path(path, first_page=i+1, last_page=i+1, dpi=200)
                ocr_text = "".join([pytesseract.image_to_string(img, lang="eng") for img in images])
                text = (text + "\n" + ocr_text).strip()
            except Exception as e:
                print(f"OCR failed on page {i+1}: {e}")
        pages_text.append((i+1, text))
    return pages_text

# ============================
# Index Builders
# ============================
def build_index_from_folder(folder="rawdata/"):
    global index, chunks, metas
    all_chunks, all_meta = [], []
    pdfs = [p for p in os.listdir(folder) if p.lower().endswith(".pdf")]
    for pdf in pdfs:
        path = os.path.join(folder, pdf)
        pages = _extract_text_from_pdf(path)
        for page_num, text in pages:
            if not text.strip():
                continue
            chunk_list = _chunk_text(text)
            for ci, ch in enumerate(chunk_list):
                all_chunks.append(ch)
                all_meta.append({"source": pdf, "page": page_num, "chunk_index": ci})

    if not all_chunks:
        return None, [], []

    emb = emb_model.encode([f"passage: {t}" for t in all_chunks], convert_to_numpy=True, show_progress_bar=True)
    faiss.normalize_L2(emb)
    dim = emb.shape[1]
    idx = faiss.IndexFlatIP(dim)
    idx.add(emb)

    index = idx
    chunks = all_chunks
    metas = all_meta
    print(index,"index======================================================>")
    print(chunks,"chunks======================================================>")

    print(metas,"metas======================================================>")

    return index, metas, chunks

def add_pdf_to_index(file_bytes, filename="uploaded.pdf"):
    global index, chunks, metas
    os.makedirs("rawdata", exist_ok=True)
    tmp_path = os.path.join("rawdata", filename)
    with open(tmp_path, "wb") as f:
        f.write(file_bytes)
    pages = _extract_text_from_pdf(tmp_path)
    new_chunks, new_meta = [], []
    for page_num, text in pages:
        if not text.strip():
            continue
        chunk_list = _chunk_text(text)
        for ci, ch in enumerate(chunk_list):
            new_chunks.append(ch)
            new_meta.append({"source": filename, "page": page_num, "chunk_index": ci})

    if not new_chunks:
        return 0

    emb = emb_model.encode([f"passage: {t}" for t in new_chunks], convert_to_numpy=True)
    faiss.normalize_L2(emb)

    if index is None:
        dim = emb.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(emb)
        chunks = new_chunks.copy()
        metas = new_meta.copy()
    else:
        index.add(emb)
        chunks.extend(new_chunks)
        metas.extend(new_meta)

    return len(new_chunks)

# ============================
# Query & Answer
# ============================
def classify_query(query):
    labels = ["legal document question", "casual chat"]
    res = clf(query, labels)
    return res["labels"][0]

def _generate_answer(prompt):
    inputs = tok(prompt, return_tensors="pt").to(device)
    outputs = llm.generate(**inputs, max_new_tokens=250, temperature=0.7)
    return tok.decode(outputs[0], skip_special_tokens=True).strip()

def is_relevant_query(query, threshold=RELEVANCE_THRESHOLD, top_k=5):
    if index is None:
        return False
    q_emb = emb_model.encode([f"query: {query}"], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)
    D, I = index.search(q_emb, top_k)
    return float(D[0][0]) >= threshold

# def answer_query(query, top_k=5):
#     if index is None:
#         return "❌ No documents indexed yet.", []

#     label = classify_query(query)

#     if label == "casual chat":
#         casual_prompt = f"""You are a friendly assistant.
# The user said: "{query}"
# Reply shortly and naturally. 
# Do NOT mention legal documents."""
#         return _generate_answer(casual_prompt), []

#     # --- Legal Q&A ---
#     q_emb = emb_model.encode([f"query: {query}"], convert_to_numpy=True)
#     faiss.normalize_L2(q_emb)
#     D, I = index.search(q_emb, top_k)

#     retrieved = []
#     token_count = 0
#     for score, idx in sorted(zip(D[0], I[0]), reverse=True):
#         if idx == -1 or score < RELEVANCE_THRESHOLD:
#             continue
#         chunk_text = chunks[idx]
#         # approximate token count
#         token_count += len(chunk_text.split())
#         if token_count > MAX_TOKENS_CONTEXT:
#             break
#         retrieved.append({
#             "text": chunk_text,
#             "source": metas[idx]["source"],
#             "page": metas[idx]["page"],
#             "chunk_index": metas[idx]["chunk_index"],
#             "score": float(score)
#         })

#     if not retrieved:
#         return "❌ No sufficiently relevant context found in documents.", []

#     # structured numbered context
#     context_text = "\n\n".join([f"[{i+1}] {r['text']}" for i, r in enumerate(retrieved)])
#     prompt = f"""You are a precise legal assistant.
# Answer using ONLY the provided context.
# If the answer is not present, reply exactly: INSUFFICIENT CONTEXT.

# Context:
# {context_text}

# Question: {query}
# Answer:"""

#     ans = _generate_answer(prompt)
#     return ans, retrieved


def answer_query(query, top_k=5):
    """
    Retrieve relevant chunks from PDFs and generate an answer.
    Returns: answer (str), sources (list of dict with 'source' and 'page')
    """
    if index is None:
        return "❌ No documents indexed yet.", []

    # Step 1: Classify query type
    label = classify_query(query)

    # --- Casual Chat ---
    if label == "casual chat":
        casual_prompt = f"""You are a friendly assistant.
                The user said: "{query}"
                Reply shortly and naturally. 
                Do NOT mention legal documents."""
        return _generate_answer(casual_prompt), []

    # --- Legal Question ---
    q_emb = emb_model.encode([f"query: {query}"], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)
    D, I = index.search(q_emb, top_k)

    # Collect relevant chunks
    retrieved = []
    token_count = 0
    for score, idx in sorted(zip(D[0], I[0]), reverse=True):
        if idx == -1 or score < RELEVANCE_THRESHOLD:
            continue
        chunk_text = chunks[idx]
        token_count += len(chunk_text.split())
        if token_count > MAX_TOKENS_CONTEXT:
            break
        retrieved.append({
            "text": chunk_text,
            "source": metas[idx]["source"],
            "page": metas[idx]["page"],
            "chunk_index": metas[idx]["chunk_index"],
            "score": float(score)
        })

    if not retrieved:
        return "❌ No sufficiently relevant context found in documents.", []

    # Concatenate chunks for LLM but keep text hidden from frontend
    context_text = "\n\n".join([r["text"] for r in retrieved])
    prompt = f"""You are a precise legal assistant.
                Answer the question using ONLY the provided context.
                If the answer is not present, reply exactly: INSUFFICIENT CONTEXT.

                Context:
                {context_text}

                Question: {query}
                Answer:"""

    ans = _generate_answer(prompt)

    # --- Determine which source/page the answer came from ---
    used_sources = []
    for r in retrieved:
        # simple substring match to check if chunk contributed
        if any(sentence.strip() in r["text"] for sentence in ans.split(".") if sentence.strip()):
            used_sources.append({"source": r["source"], "page": r["page"], "score": r["score"]})

    # fallback: if no match, just use top chunk
    if not used_sources:
        used_sources = [{"source": retrieved[0]["source"], "page": retrieved[0]["page"], "score": retrieved[0]["score"]}]

    return ans, used_sources
