"""
FastAPI layer exposing SecondSelf backend as a REST API for the frontend.

Run with: uvicorn api:app --reload --port 8000
"""
import os
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from capture import capture_note
from process import process_capture
from graph import build_graph, export_graph, CATEGORY_COLORS
from ask import ask as ask_question

API_KEY = os.getenv("API_KEY")

app = FastAPI(title="SecondSelf API")

# Allow your v0/Vercel frontend + local dev to call this API.
# Replace "*" with your actual frontend domain once deployed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sesecond-self-frontend.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify that the request contains a valid API key."""
    if not API_KEY:
        # If no API key is configured, allow all requests (for local dev)
        return
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


class CaptureRequest(BaseModel):
    content: str
    link_threshold: Optional[float] = 0.75


class AskRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/capture")
def capture(req: CaptureRequest, api_key_verified: None = Depends(verify_api_key)):
    """Capture a note, process it (classify → wiki → link), and rebuild the graph."""
    if not req.content or not req.content.strip():
        raise HTTPException(400, "Content cannot be empty")

    try:
        raw_id = capture_note(req.content.strip())
        wiki_id = process_capture(raw_id, link_threshold=req.link_threshold)
        export_graph()
        return {"raw_id": raw_id, "wiki_id": wiki_id, "status": "processed"}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/graph")
def get_graph(api_key_verified: None = Depends(verify_api_key)):
    """Return the full knowledge graph as nodes + edges."""
    try:
        data = build_graph()
        return {
            "nodes": [n.__dict__ for n in data.nodes],
            "edges": [
                {"from": e.from_, "to": e.to, "weight": e.weight, "title": e.title}
                for e in data.edges
            ],
            "categories": CATEGORY_COLORS,
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/rebuild-graph")
def rebuild_graph(api_key_verified: None = Depends(verify_api_key)):
    try:
        export_graph()
        return {"status": "rebuilt"}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/ask")
def ask_endpoint(req: AskRequest, api_key_verified: None = Depends(verify_api_key)):
    if not req.question or not req.question.strip():
        raise HTTPException(400, "Question cannot be empty")
    try:
        return ask_question(req.question.strip(), req.top_k)
    except Exception as e:
        raise HTTPException(500, str(e))
