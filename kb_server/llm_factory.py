"""Thin Anthropic Messages wrapper for prompts (shared by KB nodes)."""
import os

from anthropic import Anthropic


def invoke_text(
    prompt: str,
    *,
    system: str | None = None,
    model: str,
    max_tokens: int = 1024,
) -> str:
    """
    Sends a single user message to Claude; returns concatenated plain text blocks.
    """
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        msg = (
            "ANTHROPIC_API_KEY is missing. Set it in the environment "
            "to run kb_chat_agentic."
        )
        raise RuntimeError(msg)
    kwargs: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system
    reply = Anthropic(api_key=key).messages.create(**kwargs)
    parts = reply.content if reply.content else []
    return "".join(getattr(bit, "text", "") or "" for bit in parts)


def grader_model(explicit_default: str | None = None) -> str:
    """Small/fast model for relevance and grounding checks (override via KB_GRADER_MODEL)."""
    raw = os.environ.get("KB_GRADER_MODEL")
    if raw:
        return raw.strip()
    if explicit_default:
        return explicit_default.strip()
    return "claude-3-5-haiku-20241022"
