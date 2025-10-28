from backend.services.caption import caption_processor, caption_model, device, crop_dress
import requests
from PIL import Image
import io
import torch


def filter_similar_products(upload_features: torch.Tensor, products: list, top_k: int = 20):
    import requests
    import io
    from PIL import Image
    from backend.services.caption import caption_processor, caption_model, device
    from backend.services.caption import crop_dress  # ✅ Use the same cropper

    results = []

    for prod in products:
        try:
            url = prod.get("thumbnail")
            if not url or url.startswith("/static"):
                continue

            # --- Download image ---
            response = requests.get(url, timeout=5)
            prod_image = Image.open(io.BytesIO(response.content)).convert("RGB")

            # --- Crop the dress region (for more accurate similarity) ---
            cropped_image = crop_dress(prod_image)

            # --- Extract vision embeddings ---
            inputs = caption_processor(images=cropped_image, return_tensors="pt").to(device)
            with torch.no_grad():
                vision_outputs = caption_model.vision_model(pixel_values=inputs["pixel_values"])
                pooled_output = vision_outputs.last_hidden_state.mean(dim=1)
                prod_features = torch.nn.functional.normalize(pooled_output, p=2, dim=1)

            # --- Cosine similarity ---
            sim = (upload_features @ prod_features.T).item()

            results.append((sim, prod))

        except Exception as e:
            print(f"[WARN] Failed product image {prod.get('title','')}: {e}")

    # --- Sort by similarity descending (top match first) ---
    results.sort(key=lambda x: x[0], reverse=True)

    # --- Extract top products ---
    top_products = [p for sim, p in results[:top_k]]

    # --- Optional: Print best match ---
    if results:
        best_sim, best_product = results[0]
        print(f"[INFO] Top match: '{best_product['title']}' (similarity={best_sim:.4f})")

    return top_products


# def filter_similar_products(upload_features: torch.Tensor, products: list, top_k: int = 10):
#     results = []

#     for prod in products:
#         try:
#             url = prod.get("thumbnail")
#             if not url or url.startswith("/static"):
#                 continue
#             response = requests.get(url, timeout=5)
#             prod_image = Image.open(io.BytesIO(response.content)).convert("RGB")

#             # --- Crop the dress in the scraped product image ---
#             prod_dress_image = crop_dress(prod_image)

#             # Compute features
#             inputs = caption_processor(images=prod_dress_image, return_tensors="pt").to(device)
#             with torch.no_grad():
#                 vision_outputs = caption_model.vision_model(pixel_values=inputs["pixel_values"])
#                 pooled_output = vision_outputs.last_hidden_state.mean(dim=1)
#                 prod_features = torch.nn.functional.normalize(pooled_output, p=2, dim=1)

#             # Cosine similarity
#             sim = (upload_features @ prod_features.T).item()
#             results.append((sim, prod))

#         except Exception as e:
#             print(f"[WARN] Failed product image {prod.get('title','')}: {e}")

#     # Sort by similarity
#     results.sort(key=lambda x: x[0], reverse=True)
#     return [p for sim, p in results[:top_k]]
