from fastapi import APIRouter, UploadFile, File
from app.services import voice_transcriber, nlp_model
from app.utils.security import sanitize_text

router = APIRouter(prefix="/api/voice", tags=["voice"])

@router.post("/send")
async def send_voice(file: UploadFile = File(...), lang: str = "en"):
    # transcribe (may use OpenAI Whisper if configured)
    text = await voice_transcriber.transcribe_file_async(file)
    if not text:
        return {"error": "Transcription failed."}
    text = sanitize_text(text)
    reply = nlp_model.chat_response(text)
    return {"transcript": text, "reply": reply}
