import os, time, random, json
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

# Load env vars
load_dotenv()

# Initialize Groq LLM
llm = ChatGroq(
    model="deepseek-r1-distill-llama-70b",
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Session storage
session = {
    "messages": [],
    "transcript": [],
    "start_time": None,
    "duration_secs": 0,
    "tech": "",
    "exp": 0,
    "active": False,
}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/start")
async def start_interview(
    tech: str = Form(...),
    exp: float = Form(...),
    duration: int = Form(...)
):
    session.update({
        "messages": [
            SystemMessage(content=f"You are a technical interviewer for a {tech} developer with {exp} years of experience.")
        ],
        "transcript": [],
        "start_time": time.time(),
        "duration_secs": duration * 60,
        "tech": tech,
        "exp": exp,
        "active": True,
    })

    seed = random.randint(1, 9999)
    question_msg = llm.invoke([
        *session["messages"],
        HumanMessage(content=f"You are a friendly human-like technical interviewer. Only ask a **concise technical question** about {tech} for a candidate with {exp} years experience. Do not provide the answer, hints, or explanations. Use the following seed for randomness: {seed}.")
    ])
    question = question_msg.content

    session["messages"].append(HumanMessage(content=question))
    session["transcript"].append({"role": "interviewer", "text": question})

    return JSONResponse({"question": question})

@app.post("/answer")
async def submit_answer(answer: str = Form(...)):
    session["messages"].append(HumanMessage(content=answer))
    session["transcript"].append({"role": "candidate", "text": answer})

    # Ask next follow-up question
    question_msg = llm.invoke([
        *session["messages"],
        HumanMessage(content=f"Ask a follow-up technical question about {session['tech']} based on the last answer.")
    ])
    question = question_msg.content
    session["messages"].append(HumanMessage(content=question))
    session["transcript"].append({"role": "interviewer", "text": question})

    return JSONResponse({"finished": False, "question": question})

@app.post("/finish")
async def finish_interview():
    if not session["active"]:
        return JSONResponse({"finished": True, "feedback": "No active interview.", "transcript": []})

    session["active"] = False

    transcript_text = "\n".join([f"{t['role'].capitalize()}: {t['text']}" for t in session["transcript"]])
    final_feedback_msg = llm.invoke([
        *session["messages"],
        HumanMessage(content=f"""
Evaluate this candidate for a {session['tech']} developer position with {session['exp']} years experience.
Provide JSON output with each question, the candidate's answer, score (0-10), feedback, and a final summary.
Transcript:
{transcript_text}
""")
    ])
    return JSONResponse({
        "finished": True,
        "feedback": final_feedback_msg.content,
        "transcript": session["transcript"]
    })
