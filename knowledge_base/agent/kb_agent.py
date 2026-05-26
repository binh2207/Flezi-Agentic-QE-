"""Knowledge-base agent API: ingest, list, delete, legacy RAG chat, agentic LangGraph chat."""
from __future__ import annotations

import chromadb

from kb_server.llm_factory import grader_model, invoke_text
from kb_server.state import DEFAULT_GRADER_MODEL, DEFAULT_MODEL
from knowledge_base.agent.agentic_kb_graph import build_agentic_kb_graph
from knowledge_base.vector.ingest import ingest as run_ingest
from knowledge_base.vector.query import COLLECTION_NAME, DB_PATH, query as vector_query

_GRAPH_HOLDER: list = []


def kb_ingest(directory: str, reset: bool = True) -> int:
    """Ingest Markdown into Chroma via the shared vector ingest pipeline."""
    return run_ingest(directory, reset=reset)


def kb_delete(source_substring: str) -> int:
    """Delete chunks whose metadata source path contains *source_substring*."""
    client = chromadb.PersistentClient(path=DB_PATH)
    col = client.get_collection(COLLECTION_NAME)
    data = col.get(include=["metadatas"])
    targets: list[str] = []
    for chunk_id, meta in zip(data["ids"], data["metadatas"] or []):
        src = ""
        if meta:
            raw = meta.get("source")
            if raw:
                src = str(raw)
        if source_substring in src:
            targets.append(chunk_id)
    if targets:
        col.delete(ids=targets)
    return len(targets)


def kb_list_docs() -> list[dict]:
    """Return unique source paths present in the vector collection."""
    client = chromadb.PersistentClient(path=DB_PATH)
    col = client.get_collection(COLLECTION_NAME)
    data = col.get(include=["metadatas"])
    seen: set[str] = set()
    rows: list[dict] = []
    for meta in data["metadatas"] or []:
        if not meta:
            continue
        src = meta.get("source")
        if not src or src in seen:
            continue
        seen.add(str(src))
        rows.append({"source": str(src)})
    rows.sort(key=lambda item: item["source"])
    return rows


def kb_chat_legacy(
    question: str,
    history: list[dict] | None = None,
    model: str | None = None,
) -> dict:
    """One-shot vector search then a single LLM answer (original pipeline)."""
    chosen = model or DEFAULT_MODEL
    hits = vector_query(question, n_results=8)
    if not hits:
        context = "(No documents retrieved from the knowledge base.)"
    if hits:
        blocks: list[str] = []
        for i, row in enumerate(hits, 1):
            hdr = row.get("header", "")
            src = row.get("source", "")
            blocks.append(f"[{i}] {src} | {hdr}\n{row.get('text', '')}")
        context = "\n\n".join(blocks)
    system = (
        "You are a precise assistant. Use only the provided context when answering. "
        "If the context lacks the answer, say it was not found in the knowledge base."
    )
    hist = history or []
    lines: list[str] = []
    for turn in hist[-10:]:
        lines.append(f"{turn.get('role', 'user')}: {turn.get('content', '')}")
    lines.append(f"user: Context:\n{context}\n\nQuestion:\n{question}")
    answer = invoke_text("\n".join(lines), system=system, model=chosen, max_tokens=2048)
    sources = [
        {
            "text": (h.get("text") or "")[:400],
            "source": h.get("source", ""),
            "header": h.get("header", ""),
            "score": h.get("score"),
        }
        for h in hits[:8]
    ]
    return {"answer": answer.strip(), "sources": sources}


def kb_chat_agentic(
    question: str,
    history: list[dict] | None = None,
    model: str | None = None,
    *,
    debug: bool = False,
) -> dict:
    """LangGraph agentic RAG chat with graded retrieval and optional answer check."""
    if not _GRAPH_HOLDER:
        _GRAPH_HOLDER.append(build_agentic_kb_graph())
    runner = _GRAPH_HOLDER[0]

    chosen = model or DEFAULT_MODEL
    grader = grader_model(DEFAULT_GRADER_MODEL)
    init: dict = {
        "question": question,
        "history": history or [],
        "model": chosen,
        "grader_model": grader,
        "rewrite_count": 0,
        "retrieval_rounds": 0,
        "strict_grounding": False,
        "strategy": "rag",
        "sub_queries": [],
        "retrieved_docs": [],
        "graded_docs": [],
    }
    out = runner.invoke(init)
    payload: dict = {
        "answer": out.get("answer", ""),
        "sources": out.get("sources") or [],
    }
    if debug:
        payload["retrieval_rounds"] = int(out.get("retrieval_rounds") or 0)
        payload["grounding_score"] = float(out.get("grounding_score") or 0.0)
        payload["strategy"] = out.get("strategy", "")
        payload["rewrite_count"] = int(out.get("rewrite_count") or 0)
    return payload
