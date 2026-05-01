"""
server.py — drop this at the root of Project-Starva (next to agentbackend.py)
Run: uvicorn server:app --reload --port 8000
"""
from dotenv import load_dotenv
try:
    load_dotenv()
except:
    pass  # .env file not found, continue without it

import datetime
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List

from agentbackend import build_agent
from signals.dashboard import render_signal_board
from langchain_core.messages import HumanMessage, AIMessage

app = FastAPI(title="CFO Buddy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Build agent once at startup
agent = build_agent()
conversation_history: List = []


class ChatRequest(BaseModel):
    message: str
    reset: bool = False


@app.post("/chat")
async def chat(req: ChatRequest):
    global conversation_history

    if req.reset:
        conversation_history = []
        return {"response": "Conversation reset.", "reset": True}

    conversation_history.append(HumanMessage(content=req.message))

    # cap history to last 40 messages
    if len(conversation_history) > 40:
        conversation_history = conversation_history[-40:]

    try:
        result = agent.invoke({"messages": conversation_history})
        msgs = result["messages"]

        # get last non-empty content
        response = ""
        for m in reversed(msgs):
            content = getattr(m, "content", "")
            if content and content.strip():
                response = content.strip()
                break

        if not response:
            response = "I couldn't generate a response. Please try again."

        conversation_history.append(AIMessage(content=response))

        # log to file
        try:
            with open("conversation.log", "a") as f:
                f.write(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] You: {req.message}\n")
                f.write(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] CFOBuddy: {response}\n\n")
                f.flush()
        except Exception as log_err:
            print(f"Warning: Logging error: {log_err}")

        return {"response": response, "status": "success"}

    except Exception as e:
        import traceback
        print(f"Chat error: {traceback.format_exc()}")
        error_msg = f"Backend error processing your request. Please try again. Details: {str(e)}"
        return {"response": error_msg, "error": True, "status": "error"}


@app.get("/signals")
async def signals():
    try:
        board = render_signal_board()
        return board
    except Exception as e:
        return {"error": str(e)}


@app.get("/health")
async def health():
    return {"status": "ok", "model": "llama3.2:3b", "ollama": "http://localhost:11434"}


# serve frontend
app.mount("/", StaticFiles(directory="ui", html=True), name="ui")