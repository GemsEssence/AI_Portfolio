from backend.services.caption import caption_processor, caption_model, device, crop_dress
import requests
from PIL import Image
import io
import torch

def filter_similar_products(upload_features: torch.Tensor, products: list, threshold: float = 0.65):
    """
    Filters products based on a minimum similarity score instead of a fixed count.
    """
    import requests
    import io
    from PIL import Image
    from backend.services.caption import caption_processor, caption_model, device, crop_dress

    results = []

    for prod in products:
        try:
            url = prod.get("thumbnail")
            if not url or url.startswith("/static"):
                continue

            response = requests.get(url, timeout=5)
            prod_image = Image.open(io.BytesIO(response.content)).convert("RGB")
            
            # Use the same cropper for consistency
            cropped_image = crop_dress(prod_image)

            inputs = caption_processor(images=cropped_image, return_tensors="pt").to(device)
            with torch.no_grad():
                vision_outputs = caption_model.vision_model(pixel_values=inputs["pixel_values"])
                pooled_output = vision_outputs.last_hidden_state.mean(dim=1)
                prod_features = torch.nn.functional.normalize(pooled_output, p=2, dim=1)

            # Cosine similarity calculation
            sim = (upload_features @ prod_features.T).item()
            print(f"[DEBUG] Similarity for product '{prod.get('title','')}': {sim:.4f}")

            # --- ONLY ADD IF SIMILARITY IS ABOVE THRESHOLD ---
            if sim >= threshold:
                results.append((sim, prod))

        except Exception as e:
            print(f"[WARN] Failed product image {prod.get('title','')}: {e}")

    # Sort so the most similar is first
    results.sort(key=lambda x: x[0], reverse=True)

    # Return only the products that passed the threshold
    return [p for sim, p in results]