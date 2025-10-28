import os
import json
import re
from openai import OpenAI

# === Configuration ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
OBJECT_MAP_PATH = os.path.join(BASE_DIR, "data", "mappings", "object_map.json")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ------------------- Cache Handling -------------------
def load_object_map():
    """Load the cached object info map."""
    if os.path.exists(OBJECT_MAP_PATH):
        with open(OBJECT_MAP_PATH, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_object_map(obj_map):
    """Save updated object map to disk."""
    os.makedirs(os.path.dirname(OBJECT_MAP_PATH), exist_ok=True)
    with open(OBJECT_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(obj_map, f, indent=4, ensure_ascii=False)


# ------------------- OpenAI GPT -------------------
def generate_ai_object_details(cls_name: str):
    """
    Fetch structured object details using OpenAI GPT safely.
    Always returns a JSON object with required fields.
    """
    prompt = f"""
You are an AI assistant for an object detection application.
You MUST ONLY RETURN a valid JSON object, exactly matching this format:

{{
  "name": "<readable name>",
  "description": "<4-5 line description>",
  "usage": "<typical use or context>",
  "benefits": "<why it is useful or important>",
  "origin": "<where it comes from or its history>",
  "summary": "<1-2 line short recap>",
  "question": "Would you like to know more about this <object>?"
}}

Do not include anything outside the JSON.
Describe this object: "{cls_name}"
"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
        temperature=0.6,
    )

    text = response.output_text.strip()

    # Extract JSON block using regex
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        json_text = match.group(0)
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            # Optional: try a tolerant parser
            try:
                import json5
                return json5.loads(json_text)
            except Exception:
                pass

    # Fallback if parsing fails
    return {
        "name": cls_name.title(),
        "description": "Error: AI did not return valid JSON.",
        "usage": "",
        "benefits": "",
        "origin": "",
        "summary": "",
        "question": f"Would you like to know more about this {cls_name}?",
    }


# ------------------- Main Function -------------------
def get_object_details(detected_classes):
    """
    Fetch details for detected classes:
    - Uses cache if available
    - Calls OpenAI API if not cached
    - Returns a list of structured details
    """
    obj_map = load_object_map()
    details = []
    seen_classes = set()

    for cls in detected_classes:
        cls_lower = cls.lower()
        if cls_lower in seen_classes:
            continue
        seen_classes.add(cls_lower)

        # Already cached
        if cls_lower in obj_map:
            details.append(obj_map[cls_lower])
            continue

        # Not cached — call GPT
        try:
            ai_data = generate_ai_object_details(cls)
            obj_map[cls_lower] = ai_data
            details.append(ai_data)
        except Exception as e:
            fallback_data = {
                "name": cls.title(),
                "description": f"Error generating details: {e}",
                "usage": "",
                "benefits": "",
                "origin": "",
                "summary": ""
            }
            details.append(fallback_data)

    # Save updated cache
    save_object_map(obj_map)
    return details


# ------------------- Utility -------------------
def get_cross_question(cls_name: str):
    """Return a conversational question for a detected object."""
    return f"Would you like to know more about this {cls_name}?"
