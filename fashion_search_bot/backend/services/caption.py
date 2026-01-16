import io
from PIL import Image
import torch
import numpy as np
from transformers import BlipProcessor, BlipForConditionalGeneration, AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from ultralytics import YOLO

# Device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[INFO] Device: {device}")

# YOLO segmentation model (dress detection)
yolo_model = YOLO("yolov8l-seg.pt")  # lightweight

# BLIP for base captioning
caption_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
caption_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to(device)

# Instruction-following LLM (small)
llm_model_name = "google/flan-t5-large"
tokenizer = AutoTokenizer.from_pretrained(llm_model_name)
llm_model = AutoModelForSeq2SeqLM.from_pretrained(llm_model_name).to(device)
llm_pipeline = pipeline(
    "text2text-generation",
    model=llm_model,
    tokenizer=tokenizer,
    device=0 if device=="cuda" else -1
)

# # --- Crop dress using YOLO ---
def crop_dress(image: Image.Image):
    results = yolo_model.predict(np.array(image), verbose=False)
    # print(results,"results------------------------------->")
    for r in results:
        if r.masks is not None and len(r.masks.data) > 0:
            mask = r.masks.data[0].cpu().numpy()
            ys, xs = np.where(mask > 0)
            if len(xs) == 0 or len(ys) == 0:
                continue
            x1, x2 = xs.min(), xs.max()
            y1, y2 = ys.min(), ys.max()
            return image.crop((x1, y1, x2, y2))
    return image  # fallback if no mask found

# --- Main pipeline ---
def generate_caption_and_features(image_bytes: bytes):
    try:
        # Load image
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Crop dress only
        dress_image = crop_dress(image)
        
        print(dress_image,"dressImage------------------------------->")

        # BLIP caption on cropped dress
        inputs = caption_processor(images=dress_image, return_tensors="pt").to(device)
        out = caption_model.generate(**inputs, max_length=50)
        base_caption = caption_processor.decode(out[0], skip_special_tokens=True)
        print(f"[DEBUG] BLIP base caption (cropped): {base_caption}")

        # Refine with instruction-following LLM
        # prompt = (
        #     "You are a professional fashion product describer for an online store. "
        #     "Example:Describe ONLY the clothing item — not the person, gender, or background. "
        #     "Example:Focus purely on garment type, fabric, pattern, design, embroidery, style, and occasion. "
        #     "Example:Avoid words like 'person', 'man', 'woman', 'girl', 'animal, 'bird', 'boy', 'model', 'wearing', 'standing', etc. "
        #     "Example:Describe it as if it is displayed alone on a plain background.\n\n"
        #     f"Caption: \"{base_caption}\""
        # )
        # prompt = (
        #     "Task: Extract only 2-3 essential clothing keywords (fabric, color, style).\n"
        #     "Example:Focus purely on garment type, fabric, pattern, design, embroidery, style, and occasion.\n"
        #     "Strictly remove all non-clothing words.\n"
        #     f"Input: '{base_caption}'\n"
        #     "Output:"
        # )
       # Use clear Input/Output pairs to guide the model
        prompt = (
            "Task: Convert an image description into a specific clothing search query. "
            "Include only color, fabric, pattern, and garment type. "
            "Strictly remove people, actions, and background objects.\n\n"
            "Example 1: 'a woman in a blue dress holding an umbrella' -> 'blue floral tiered dress'\n"
            "Example 2: 'a man riding a skateboard in a red shirt' -> 'red button-down shirt'\n"
            "Example 3: 'close up of a dress with a polka dot pattern' -> 'polka dot pattern dress'\n"
            f"Input: '{base_caption}'\n"
            "Output:"
        )
        refined_caption = llm_pipeline(prompt, max_new_tokens=120, do_sample=False)[0]["generated_text"].strip()
        if not refined_caption:
            refined_caption = base_caption
        print(f"[DEBUG] Refined dress caption: {refined_caption}")

        # Features for similarity search
        with torch.no_grad():
            vision_outputs = caption_model.vision_model(pixel_values=inputs["pixel_values"])
            pooled_output = vision_outputs.last_hidden_state.mean(dim=1)
            image_features = torch.nn.functional.normalize(pooled_output, p=2, dim=1)
        # print(f"[DEBUG] Image features shape: {image_features.shape}")

        return refined_caption, image_features

    except Exception as e:
        print(f"[ERROR] Processing failed: {e}")
        return None, None
