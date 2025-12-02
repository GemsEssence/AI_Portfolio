from fastapi import APIRouter, Form, Request
from app.services import nlp_model
from app.utils.translator import translate_text  # ✅ Add translator utility

router = APIRouter(prefix="/text", tags=["text"])

@router.post("/")
async def chat_with_bot(
    request: Request,
    text: str = Form(None),
    session_id: str = Form(None),
    lang: str = Form("en")  # ✅ Language comes from frontend
):
    """
    🧠 Handles user chat input for MediBot with contextual AI memory and translation.
    - Accepts language code (default English)
    - Translates user input to English before sending to Gemini
    - Translates AI reply back to user's chosen language
    """
    try:
        # ✅ Handle JSON payload (for API or external clients)
        if not text or not session_id:
            try:
                body = await request.json()
                text = body.get("text")
                session_id = body.get("session_id")
                lang = body.get("lang", "en")
            except Exception:
                pass

        # ✅ Validate inputs
        if not text or not session_id:
            return {
                "error": True,
                "message": "Missing required fields: 'text' and 'session_id'.",
                "example": {"text": "What is acne?", "session_id": "abc123", "lang": "en"}
            }

        print(f"[INFO] Chat received — Session: {session_id}, Lang: {lang}, Text: {text}")

        # ✅ Step 1: Translate user input → English
        translated_input = translate_text(text, "en")
        print(f"[DEBUG] Translated input: {translated_input}")

        # ✅ Step 2: Get response from NLP model
        response = await nlp_model.process_text(session_id, translated_input)
        print("[DEBUG] Model response (EN):", response)

        # ✅ Step 3: Translate AI response → selected language
        final_response = translate_text(response, lang)
        print("[DEBUG] Final translated response:", final_response)

        return {"response": final_response}

    except Exception as e:
        print("[ERROR] MediBot failed:", e)
        return {
            "response": f"⚠️ MediBot encountered an issue: {str(e)}"
        }
