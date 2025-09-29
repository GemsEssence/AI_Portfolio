from fastapi import FastAPI
from pydantic import BaseModel
from src.pipeline.orchestrator import SafetyOrchestrator

app = FastAPI(title="AI Safety Models API", version="0.1.0")
orch = SafetyOrchestrator(user_age=16)

class Message(BaseModel):
    text: str
    user_age: int | None = None

@app.post("/infer")
def infer(msg: Message):
    global orch
    if msg.user_age is not None:
        orch.user_age = msg.user_age
    return orch.step(msg.text)
