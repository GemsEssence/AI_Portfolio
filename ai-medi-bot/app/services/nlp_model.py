# import google.generativeai as genai
from google import genai
from google.genai import types 
import os
from dotenv import load_dotenv
from google.api_core.exceptions import ResourceExhausted

# Load environment variables and configure API (already done in main app)
load_dotenv()
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

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
    Continue conversation with persistent memory.
    Detect if user asks for medicine and respond appropriately.
    """
    prev_context = get_memory(session_id)
    text_lower = text.lower()

    # --- Step 1: Detect if user is asking for medicine ---
    medicine_keywords = [
        "medicine", "cream", "ointment", "treatment", "tablet", "drug", "prescription", "remedy"
    ]
    is_medicine_request = any(k in text_lower for k in medicine_keywords)

    # 🛑 CRITICAL FIX: Change to the working model
    # model = genai.GenerativeModel("gemini-2.5-flash")

    # --- Step 2: Custom prompt for medicine suggestions ---
    if is_medicine_request:
        prompt = f"""
        You are MediBot, a friendly and professional AI healthcare assistant (general doctor) known for empathetic and responsible communication.

        Context from previous conversation:
        {prev_context}

        The user asked: "{text}"

        Respond by:
        - Suggesting **only mild, over-the-counter (OTC)** medicines or safe topical creams if relevant.  
        - Recommending suitable medicines for the mentioned condition (if identifiable).  
        - Briefly explaining what each medicine does in simple, patient-friendly language.  
        - Including helpful **home-care tips** or **natural remedies** when appropriate.  
        - Keeping your tone **clear, empathetic, concise, and medically accurate**.  
        - Using previous context to maintain continuity and avoid repetition.  
        - Never recommend strong antibiotics, steroids, or prescription-only drugs.  
        - If symptoms are serious or uncertain, politely advise the user to consult a real doctor.  
        """

    else:
        # --- Step 3: General follow-up conversation ---
        prompt = f"""
        You are MediBot, a compassionate AI healthcare assistant (doctor) having a follow-up chat.
        Here is the previous context with this user:
        {prev_context}

        The user says: "{text}"

        Respond naturally and kindly.
        - If user follows up about their condition, answer contextually.
        - Avoid repetition. Use prior memory for continuity, remember previous context.
        - If user changes topic, adapt smoothly.
        """

    try:
        # response = model.generate_content(prompt)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
            config=types.GenerateContentConfig(
                temperature=0.7
            )
        )
        reply = response.text.strip()
        # reply = (response.text or "").strip()
        print(f"[DEBUG] Gemini Response: {reply[:200]}...")

        
    except ResourceExhausted as e:
        # ✅ Handle 429 Quota Exceeded error specifically
        print(f"[ERROR] Quota Exceeded (429): {e}")
        reply = "⚠️ The AI system is temporarily overloaded (Quota Exceeded). Please try again in a moment."
        
    except Exception as e:
        # ✅ Handle all other errors
        print("Error:", e)
        reply = "⚠️ I'm having trouble processing your message right now. Please try again in a moment."

    # --- Step 4: Store new memory ---
    # Only store context if a valid reply was generated, not an error message
    if not reply.startswith("⚠️"):
        update_memory(session_id, text, reply)

    return reply