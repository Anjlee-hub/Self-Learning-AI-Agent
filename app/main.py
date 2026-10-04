import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.agent_loop import is_calculation_request, is_time_request, is_word_count_request, run_agent
from agent.ollama_client import get_llm_provider, is_llm_available


def get_allowed_origins():
    raw = os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def get_activity_for_request(message):
    text = (message or "").lower().strip()

    if not text:
        return []

    if is_calculation_request(text):
        activity = [
            "Detected calculation request",
            "Retrieved relevant learning",
            "Selected calculator tool",
            "Executed calculator",
            "Verified result",
            "Evaluated response",
        ]
        return activity

    if is_time_request(text):
        return [
            "Detected time request",
            "Selected time tool",
            "Executed time lookup",
            "Evaluated response",
        ]

    if is_word_count_request(text):
        return [
            "Detected word-count request",
            "Selected word-count tool",
            "Executed count",
            "Evaluated response",
        ]

    return [
        "Received user request",
        "Evaluated whether a deterministic tool was needed",
        "Used language model response",
    ]


app = FastAPI(
    title="Self-Learning AI Agent",
    description="API for the self-learning AI agent.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    activity: list[str]


@app.get("/")
def root():
    return {
        "name": "Self-Learning AI Agent",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    provider = get_llm_provider()
    llm_available = is_llm_available()

    return {
        "status": "healthy",
        "agent": "online",
        "llm_provider": provider,
        "llm_available": llm_available,
        "ollama_available": llm_available if provider == "ollama" else None,
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    message = (request.message or "").strip()

    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        result, activity = run_agent(message, return_activity=True)
        return ChatResponse(response=str(result), activity=activity)
    except Exception as error:
        raise HTTPException(status_code=500, detail="Agent execution failed. Please try again.")
