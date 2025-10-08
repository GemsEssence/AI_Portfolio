import torch
import numpy as np

# Simple in-memory vector DB
VECTOR_DB = []

def add_to_index(title: str, data: dict):
    """
    Add item to vector DB.
    data should contain:
        - "features": numpy array or torch tensor
        - "title": str
    """
    if isinstance(data.get("features"), torch.Tensor):
        data["features"] = data["features"].cpu().numpy()
    VECTOR_DB.append({"title": title, **data})

def search_similar(query_features: torch.Tensor, top_k: int = 3):
    """
    Return top_k similar items from VECTOR_DB based on cosine similarity
    """
    if query_features.ndim == 1:
        query_features = query_features.unsqueeze(0)

    query_np = query_features.cpu().numpy()
    results = []

    for item in VECTOR_DB:
        if "features" not in item:
            continue
        vec = item["features"]
        sim = np.dot(query_np, vec.T) / (np.linalg.norm(query_np) * np.linalg.norm(vec) + 1e-10)
        results.append({"title": item["title"], "similarity": float(sim)})

    results = sorted(results, key=lambda x: x["similarity"], reverse=True)[:top_k]
    print(f"Search found {len(results)} similar items.")
    return results
