"""
REST API for the knowledge base: ingest, list documents, and agentic chat.
Run from the project root: `python kb_server/web_app.py`
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from knowledge_base.agent.kb_agent import (
    kb_chat_agentic,
    kb_chat_legacy,
    kb_delete,
    kb_ingest,
    kb_list_docs,
)

app = FastAPI(title="KB Agent API", version="1.0.0")


class ChatBody(BaseModel):
    question: str = Field(..., min_length=1)
    history: list[dict] = Field(default_factory=list)
    model: str | None = None


class IngestBody(BaseModel):
    directory: str
    reset: bool = True


@app.post("/kb/chat")
def kb_chat_post(body: ChatBody, debug: bool = Query(default=False)):
    """Agentic RAG chat; optional debug fields when `debug=true`."""
    out = kb_chat_agentic(
        body.question,
        history=body.history,
        model=body.model,
        debug=debug,
    )
    return JSONResponse(out)


@app.post("/kb/chat/legacy")
def kb_chat_legacy_post(body: ChatBody):
    """One-shot RAG for comparison with agentic mode."""
    return JSONResponse(
        kb_chat_legacy(body.question, history=body.history, model=body.model)
    )


@app.post("/kb/ingest")
def kb_ingest_post(body: IngestBody):
    count = kb_ingest(body.directory, reset=body.reset)
    return {"chunks": count}


@app.get("/kb/docs")
def kb_docs_get():
    return {"sources": kb_list_docs()}


@app.delete("/kb/docs")
def kb_docs_delete(source_substring: str = Query(..., min_length=1)):
    removed = kb_delete(source_substring)
    return {"deleted_chunks": removed}


@app.get("/health")
def health():
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("KB_BIND_HOST", "127.0.0.1")
    port = int(os.environ.get("KB_BIND_PORT", "8765"))
    uvicorn.run("kb_server.web_app:app", host=host, port=port, reload=False)
