import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Simple in-memory session store
conversation_memory = {}

def get_memory(session_id: str) -> str:
    """Retrieve prior memory context for the session."""
    return conversation_memory.get(session_id, "")

def update_memory(session_id: str, user_msg: str, bot_reply: str):
    """Update stored conversation context."""
    prev = conversation_memory.get(session_id, "")
    new_context = f"{prev}\nUser: {user_msg}\nMediBot: {bot_reply}"
    conversation_memory[session_id] = new_context


async def process_text(session_id: str, text: str) -> str:
    """
    Continue chat with memory.
    Detect if user asks for medicine and respond appropriately.
    """
    prev_context = get_memory(session_id)
    text_lower = text.lower()

    # --- Step 1: Detect if user is asking for medicine ---
    medicine_keywords = [
        "medicine", "cream", "ointment", "treatment", "tablet", "drug", "prescription", "remedy"
    ]
    is_medicine_request = any(k in text_lower for k in medicine_keywords)

    model = genai.GenerativeModel("gemini-2.0-flash")

    # --- Step 2: Custom prompt for medicine suggestions ---
    if is_medicine_request:
        prompt = f"""
        You are MediBot, an AI dermatologist with friendly and responsible communication style.

        Context from previous conversation:
        {prev_context}

        The user asked: "{text}"

        Respond by:
        - Suggesting **only mild, over-the-counter (OTC)** medicines or topical creams.
        - Include 2-3 safe, well-known options like benzoyl peroxide gel, salicylic acid cream, hydrocortisone 1%, etc.
        - Mention what each does in simple language.
        - Add home-care or natural remedies if appropriate.
        - Be clear, empathetic, and concise.
        - NEVER recommend strong antibiotics, steroids, or prescription-only drugs.
        """

    else:
        # --- Step 3: General follow-up conversation ---
        prompt = f"""
        You are MediBot, a compassionate AI dermatologist having a follow-up chat.
        Here is the previous context with this user:
        {prev_context}

        The user says: "{text}"

        Respond naturally and kindly.
        - If user follows up about their condition, answer contextually.
        - Avoid repetition. Use prior memory for continuity.
        - If user changes topic, adapt smoothly.
        """

    try:
        response = model.generate_content(prompt)
        reply = response.text.strip()
    except Exception as e:
        print("Error:", e)
        reply = "⚠️ I'm having trouble processing your message right now. Please try again in a moment."

    # --- Step 4: Store new memory ---
    update_memory(session_id, text, reply)

    return reply
