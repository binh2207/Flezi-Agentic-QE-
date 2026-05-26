"""
Agentic KB pipeline: LangGraph controls retrieval, grading, rewrite, and answer checks.
"""
import hashlib
import json
import re
from json import JSONDecodeError
from typing import Literal

from langgraph.graph import END, StateGraph

from kb_server.llm_factory import grader_model, invoke_text
from kb_server.state import AgenticKBState, DEFAULT_GRADER_MODEL, DEFAULT_MODEL
from knowledge_base.vector.query import query

MAX_REWRITE = 2
DOCS_CAP = 12
GRADE_CAP = 15
TOPK = 6

_TICKET = re.compile(r"\b[A-Z][A-Z0-9]{1,9}-\d+\b")


def _fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]


def _parse_json_obj(raw: str) -> dict:
    fragment = raw.strip()
    if fragment.startswith("```"):
        lines = fragment.split("\n")
        fragment = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        fragment = fragment.strip()
    match = re.search(r"\{[\s\S]*\}", fragment)
    if not match:
        return {}
    blob = match.group()
    try:
        parsed = json.loads(blob)
        return parsed if isinstance(parsed, dict) else {}
    except JSONDecodeError:
        return {}


def _resolve_source_from_key(text: str) -> str | None:
    hit = _TICKET.search(text)
    if not hit:
        return None
    return hit.group()


def _history_block(history: list[dict], limit: int = 10) -> str:
    tail = history[-limit:] if history else []
    lines: list[str] = []
    for turn in tail:
        role = turn.get("role", "user")
        content = turn.get("content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines) if lines else "(no prior turns)"


def analyze_query(state: AgenticKBState) -> dict:
    q = state["question"]
    hist = _history_block(state.get("history") or [])
    model = state.get("model") or DEFAULT_MODEL
    prompt = f"""Classify the user question and plan retrieval.

Recent conversation:
{hist}

User question: {q}

Return ONLY valid JSON with this shape:
{{"sub_queries": ["..."], "strategy": "direct|decompose|rag|llm_only"}}

Rules:
- Use "llm_only" for questions that do not need a document KB (e.g. current time, pure math with no org context, chit-chat).
- Use "decompose" for multi-part or compare questions; produce 2-3 focused sub-queries.
- Use "direct" for a single factual question about documentation or product behavior.
- sub_queries must be non-empty unless strategy is llm_only (then use a single trivial placeholder like "(no retrieval)").
"""
    raw = invoke_text(prompt, model=model, max_tokens=512)
    parsed = _parse_json_obj(raw)
    strategy = str(parsed.get("strategy", "rag")).strip()
    subs = parsed.get("sub_queries")
    if not isinstance(subs, list) or not subs:
        subs = [q]
    subs = [str(s).strip() for s in subs if str(s).strip()]
    if not subs:
        subs = [q]
    if strategy == "llm_only":
        subs = ["(no retrieval)"]
    return {"sub_queries": subs, "strategy": strategy}


def route_after_analyze(state: AgenticKBState) -> Literal["retrieve", "generate"]:
    if state.get("strategy") == "llm_only":
        return "generate"
    return "retrieve"


def retrieve(state: AgenticKBState) -> dict:
    key = _resolve_source_from_key(state["question"])
    seen: set[str] = set()
    bucket: list[dict] = []
    rounds = int(state.get("retrieval_rounds") or 0) + 1
    for sub in state.get("sub_queries") or [state["question"]]:
        if sub == "(no retrieval)":
            continue
        text = sub
        if key:
            text = f"{key} {sub}"
        for hit in query(text, n_results=TOPK):
            fp = _fingerprint(hit["text"])
            if fp in seen:
                continue
            seen.add(fp)
            chunk = dict(hit)
            chunk["_fp"] = fp
            bucket.append(chunk)
            if len(bucket) >= DOCS_CAP:
                break
        if len(bucket) >= DOCS_CAP:
            break
    return {"retrieved_docs": bucket, "retrieval_rounds": rounds}


def _grade_one_doc(question: str, doc: dict, grader: str) -> bool:
    body = doc.get("text", "")[:8000]
    prompt = f"""You are assessing relevance. Given a user question and a retrieved document chunk,
output JSON: {{"relevant": true or false, "reason": "one sentence"}}.
Question: {question}
Document: {body}
"""
    raw = invoke_text(prompt, model=grader, max_tokens=256)
    parsed = _parse_json_obj(raw)
    return bool(parsed.get("relevant"))


def grade_documents(state: AgenticKBState) -> dict:
    q = state["question"]
    grader = state.get("grader_model") or grader_model(DEFAULT_GRADER_MODEL)
    docs = (state.get("retrieved_docs") or [])[:GRADE_CAP]
    kept: list[dict] = []
    for doc in docs:
        if _grade_one_doc(q, doc, grader):
            kept.append(doc)
    last_fail = ""
    subs = state.get("sub_queries")
    if subs:
        last_fail = subs[0]
    return {"graded_docs": kept, "last_failed_query": last_fail}


def route_after_grade(state: AgenticKBState) -> Literal["rewrite", "generate"]:
    bucket = state.get("graded_docs") or []
    if len(bucket) >= 2:
        return "generate"
    if int(state.get("rewrite_count") or 0) < MAX_REWRITE:
        return "rewrite"
    return "generate"


def rewrite_query(state: AgenticKBState) -> dict:
    q = state["question"]
    last = state.get("last_failed_query") or q
    irr = state.get("retrieved_docs") or []
    noise = "\n".join((d.get("text") or "")[:400] for d in irr[:3])
    prompt = f"""Rewrite this search query to be more likely to find relevant documents.
Original question: {q}
Previous query that failed: {last}
Examples of irrelevant snippets (ignore if empty):
{noise}
Produce a better search query (just the query text, no explanation).
"""
    model = state.get("model") or DEFAULT_MODEL
    line = invoke_text(prompt, model=model, max_tokens=128).strip().split("\n")[0]
    cleaned = line.strip('"').strip("'")
    count = int(state.get("rewrite_count") or 0) + 1
    return {"sub_queries": [cleaned or q], "rewrite_count": count}


def generate(state: AgenticKBState) -> dict:
    q = state["question"]
    hist = state.get("history") or []
    model = state.get("model") or DEFAULT_MODEL
    strict = bool(state.get("strict_grounding"))
    strategy = state.get("strategy") or "rag"
    docs = state.get("graded_docs") or []
    context = ""
    if strategy == "llm_only":
        context = "(No knowledge-base retrieval for this question.)"
    if strategy != "llm_only" and not docs:
        context = "(No relevant documents were retrieved from the knowledge base.)"
    if strategy != "llm_only" and docs:
        parts: list[str] = []
        for i, doc in enumerate(docs, 1):
            src = doc.get("source", "")
            hdr = doc.get("header", "")
            parts.append(f"[{i}] Source: {src} | {hdr}\n{doc.get('text', '')}")
        context = "\n\n".join(parts)
    system = (
        "You are a precise assistant. Answer using ONLY the provided context when context is present. "
        "If the context does not contain the answer, say the information was not found in the knowledge base "
        "and avoid inventing facts."
    )
    if strict:
        system += " Every sentence must be directly supported by the cited context; if unsure, refuse."
    payload: list[dict] = []
    for turn in hist[-10:]:
        payload.append({"role": turn["role"], "content": turn["content"]})
    user = f"""Context:\n{context}\n\nQuestion:\n{q}\n\n"""
    payload.append({"role": "user", "content": user})
    transcript = "\n".join(f"{m['role']}: {m['content']}" for m in payload)
    answer = invoke_text(transcript, system=system, model=model, max_tokens=2048)
    sources = [
        {
            "text": d.get("text", "")[:400],
            "source": d.get("source", ""),
            "header": d.get("header", ""),
            "score": d.get("score"),
        }
        for d in docs[:8]
    ]
    return {"answer": answer.strip(), "sources": sources}


def grade_answer(state: AgenticKBState) -> dict:
    if state.get("strategy") == "llm_only":
        return {"answer_ok": True, "grounding_score": 1.0}
    docs = state.get("graded_docs") or []
    ctx = "(No relevant documents were retrieved from the knowledge base.)"
    if docs:
        ctx = "\n\n".join((d.get("text") or "")[:6000] for d in docs[:5])
    ans = state.get("answer") or ""
    grader = state.get("grader_model") or grader_model(DEFAULT_GRADER_MODEL)
    prompt = f"""You check answers against evidence.

Retrieved documents:
{ctx}

Generated answer:
{ans}

Return JSON ONLY:
{{"grounded": true|false, "addresses_question": true|false, "ungrounded_claims": ["..."]}}

"grounded" means no substantial factual statements beyond the documents.
"""
    raw = invoke_text(prompt, model=grader, max_tokens=400)
    parsed = _parse_json_obj(raw)
    grounded = bool(parsed.get("grounded", True))
    addresses = bool(parsed.get("addresses_question", True))
    score = 1.0 if grounded else 0.0
    if not grounded:
        score = 0.2
    if not addresses:
        score *= 0.5
    return {
        "answer_ok": grounded and addresses,
        "grounding_score": score,
    }


def route_after_answer(state: AgenticKBState) -> Literal["end", "strict", "caveat"]:
    if state.get("answer_ok"):
        return "end"
    if not state.get("strict_grounding"):
        return "strict"
    return "caveat"


def mark_strict(state: AgenticKBState) -> dict:
    return {"strict_grounding": True}


def apply_caveat(state: AgenticKBState) -> dict:
    base = state.get("answer") or ""
    suffix = (
        "\n\n(Note: This answer could not be fully grounded in retrieved documents; "
        "treat unsupported claims cautiously.)"
    )
    return {"answer": base + suffix}


def build_agentic_kb_graph():
    graph = StateGraph(AgenticKBState)
    graph.add_node("analyze_query", analyze_query)
    graph.add_node("retrieve", retrieve)
    graph.add_node("grade_documents", grade_documents)
    graph.add_node("rewrite_query", rewrite_query)
    graph.add_node("generate", generate)
    graph.add_node("grade_answer", grade_answer)
    graph.add_node("mark_strict", mark_strict)
    graph.add_node("apply_caveat", apply_caveat)

    graph.set_entry_point("analyze_query")
    graph.add_conditional_edges(
        "analyze_query",
        route_after_analyze,
        {"retrieve": "retrieve", "generate": "generate"},
    )
    graph.add_edge("retrieve", "grade_documents")
    graph.add_conditional_edges(
        "grade_documents",
        route_after_grade,
        {"rewrite": "rewrite_query", "generate": "generate"},
    )
    graph.add_edge("rewrite_query", "retrieve")
    graph.add_edge("generate", "grade_answer")
    graph.add_conditional_edges(
        "grade_answer",
        route_after_answer,
        {"end": END, "strict": "mark_strict", "caveat": "apply_caveat"},
    )
    graph.add_edge("mark_strict", "generate")
    graph.add_edge("apply_caveat", END)
    return graph.compile()
