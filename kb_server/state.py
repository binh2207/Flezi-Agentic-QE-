"""Shared LangGraph state for the KB agent."""
from typing import TypedDict


class AgenticKBState(TypedDict, total=False):
    question: str
    history: list[dict]
    model: str
    grader_model: str
    sub_queries: list[str]
    strategy: str
    retrieved_docs: list[dict]
    graded_docs: list[dict]
    rewrite_count: int
    retrieval_rounds: int
    last_failed_query: str
    strict_grounding: bool
    answer: str
    answer_ok: bool
    sources: list[dict]
    grounding_score: float
    caveat: str


DEFAULT_MODEL = "claude-sonnet-4-20250514"
DEFAULT_GRADER_MODEL = "claude-3-5-haiku-20241022"
