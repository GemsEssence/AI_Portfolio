import os
import tempfile
from typing import Optional
from fastapi import UploadFile

# This module is a switch: local mock or OpenAI Whisper (if API key provided)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

async def transcribe_file_async(file: UploadFile) -> Optional[str]:
    """
    Save the incoming UploadFile to temp and return transcription text.
    Replace the mock with Whisper/OpenAI when ready.
    """
    try:
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
        # If OPENAI_API_KEY is set, integrate whisper here (example placeholders)
        if OPENAI_API_KEY:
            # TODO: call OpenAI/whisper API using openai package
            # e.g., openai.Audio.transcriptions.create(...)
            return "Simulated transcription (Whisper integration pending)."
        # fallback mock:
        return "Simulated transcription: i have fever and headache"
    except Exception:
        return None
