# AI Interviewer 🎙️

**AI Interviewer** is a **FastAPI-based web application** that conducts technical interviews using **Groq + LangChain**.  
It generates concise technical questions, receives candidate answers, and provides structured feedback with scoring. Users can interact via **text input** or **speech-to-text**.

---

## 📂 Project Structure

```bash
ai_interview_app/
├── app.py                  # FastAPI backend with LLM integration
├── templates/
│   └── index.html          # Frontend UI
├── static/
│   ├── style.css           # Styles for chat interface
│   └── script.js           # JS for chat, TTS, STT interactions
├── .env                    # Environment variables
└── requirements.txt        # Python dependencies


🔧 Features

    Conduct technical interviews for a specified technology and experience level.

    Generate concise technical questions without hints or answers.

    Receive candidate answers and store in a transcript.

    Generate follow-up questions based on previous answers.

    Provide structured final feedback with scoring (0-10) for each answer and overall summary.

    Support text input and speech-to-text input.

    Minimal chat-like frontend for interactive interview experience.


⚙️ Setup Instructions
    1. Clone the repository
    git clone <your-repo-url>
    cd ai_interview

    2. Create and activate a Python virtual environment
    python -m venv venv
    source venv/bin/activate      # Linux / macOS
    venv\Scripts\activate         # Windows

    3. Install dependencies
    pip install -r requirements.txt

    4. Setup environment variables

    Create a .env file with:

    API_KEY=<your-groq-api-key>
    DEBUG=True

    5. Run the FastAPI application
    uvicorn app:app --reload

    6. Open in browser

    Visit: http://127.0.0.1:8000

🖥️ Frontend Interaction

    Start Interview:
    Enter Technology, Experience (years), and Duration (minutes) → Click Start Interview.

    Answer Questions:
    Type your answer or use the microphone button for speech-to-text input.

    Follow-up Questions:
    After each answer, the system generates a follow-up question.

    End Interview:
    When finished, click Finish or wait for session end to receive JSON structured feedback, including:

    Each question

    Candidate answers

    Score (0-10)

    Feedback

    Final summary

📝 Notes

    app.py contains FastAPI routes, session handling, and Groq LLM integration.

    templates/index.html provides the interactive frontend.

    static/ contains CSS and JS for chat bubbles, text-to-speech, and speech-to-text.

    Session is maintained in memory as a Python dictionary (session object).

    .env stores API keys and configuration flags.

    requirements.txt contains all necessary Python packages for FastAPI, LangChain, and Groq integration.