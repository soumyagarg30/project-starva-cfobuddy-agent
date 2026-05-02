from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import ollama
import json
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_NAME = "llama3.2:3b"

conversation_history = []

# frontend folder
app.mount("/ui", StaticFiles(directory="ui"), name="ui")


class ChatRequest(BaseModel):
    message: str
    reset: bool = False


@app.get("/")
async def root():
    return FileResponse("ui/index.html")


@app.get("/health")
async def health():
    return {
        "status": "online",
        "model": MODEL_NAME
    }


@app.get("/signals")
async def signals():
    return {
        "margin": {
            "status": "GREEN",
            "label": "Healthy"
        },
        "ltv": {
            "status": "GREEN",
            "label": "Growing"
        },
        "cac": {
            "status": "YELLOW",
            "label": "Monitor"
        },
        "burn": {
            "status": "RED",
            "label": "High"
        },
        "runway": {
            "status": "GREEN",
            "label": "14 months"
        }
    }


@app.post("/chat")
async def chat(req: ChatRequest):
    global conversation_history

    if req.reset:
        conversation_history = []
        return {"response": "Conversation reset."}

    if not req.message.strip():
        return {"response": "Please enter a message."}

    try:
        conversation_history.append({
            "role": "user",
            "content": req.message
        })

        response = ollama.chat(
            model=MODEL_NAME,
            messages=conversation_history
        )

        bot_response = response["message"]["content"]

        conversation_history.append({
            "role": "assistant",
            "content": bot_response
        })

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": req.message,
            "assistant": bot_response
        }

        with open("conversation.log", "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        return {
            "response": bot_response
        }

    except Exception as e:
        return {
            "response": f"Backend error: {str(e)}"
        }