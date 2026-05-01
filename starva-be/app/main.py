from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .rag_engine import SimpleRAGEngine
from .modules.cfobuddy_be import router as cfobuddy_router


class BriefCreate(BaseModel):
    text: str


class Brief(BaseModel):
    id: int
    text: str


class SuggestionRequest(BaseModel):
    briefId: int


class SuggestionResponse(BaseModel):
    symbols: List[str]
    colorPalette: List[str]
    notes: str


app = FastAPI(title="Design RAG Backend")

# Simple in-memory store for briefs.
BRIEFS: List[Brief] = []
rag_engine = SimpleRAGEngine()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cfobuddy_router, prefix="/api")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/briefs", response_model=Brief)
async def create_brief(payload: BriefCreate) -> Brief:
    new_id = len(BRIEFS) + 1
    brief = Brief(id=new_id, text=payload.text)
    BRIEFS.append(brief)
    return brief


@app.get("/briefs", response_model=List[Brief])
async def list_briefs() -> List[Brief]:
    return BRIEFS


@app.post("/suggest", response_model=SuggestionResponse)
async def suggest_design(payload: SuggestionRequest) -> SuggestionResponse:
    brief = next((b for b in BRIEFS if b.id == payload.briefId), None)
    if not brief:
        # In a more complete app, raise HTTPException(404)
        return SuggestionResponse(symbols=[], colorPalette=[], notes="Brief not found.")

    suggestion = rag_engine.suggest(brief.text)
    return SuggestionResponse(**suggestion.to_dict())


# For local dev, run: uvicorn app.main:app --reload --port 8000
