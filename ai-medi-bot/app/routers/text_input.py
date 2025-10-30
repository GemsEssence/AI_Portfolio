from fastapi import APIRouter, Form, Request
from app.services import nlp_model

router = APIRouter(prefix="/text", tags=["text"])

@router.post("/")
async def chat_with_bot(
    request: Request,
    text: str = Form(None),
    session_id: str = Form(None)
):
    """
    🧠 Handles user chat input for MediBot with contextual AI memory.
    Supports both FormData (from frontend) and JSON (API clients).
    """
    try:
        # ✅ Handle case where frontend sends JSON instead of FormData
        if not text or not session_id:
            try:
                body = await request.json()
                text = body.get("text")
                session_id = body.get("session_id")
            except Exception:
                pass

        # ✅ Validate inputs
        if not text or not session_id:
            return {
                "error": True,
                "message": "Missing required fields: 'text' and 'session_id'.",
                "example": {"text": "What is acne?", "session_id": "abc123"}
            }

        print(f"[INFO] Chat received — Session: {session_id}, Text: {text}")

        # ✅ Call NLP model
        response = await nlp_model.process_text(session_id, text)
        print("[DEBUG] Model response:", response)

        return {"response": response}

    except Exception as e:
        print("[ERROR] MediBot failed:", e)
        return {
            "response": f"⚠️ MediBot encountered an issue: {str(e)}"
        }
