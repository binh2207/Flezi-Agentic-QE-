"""RAG answer: query ChromaDB then call Claude with retrieved context."""
from __future__ import annotations

import argparse

import anthropic

from knowledge_base.vector.query import query as vector_query

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_N_RESULTS = 5
DEFAULT_SYSTEM = (
    "You are a QA assistant. Use the provided context to answer the question. "
    "If the context does not contain the answer, say so."
)


class RAGAnswer:
    """Query the vector store and answer using Claude.

    Usage:
        from scripts.rag_answer import RAGAnswer

        result = RAGAnswer().answer("What test design techniques are supported?")
        print(result["answer"])
        for s in result["sources"]:
            print(s["source"], s["score"])
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        n_results: int = DEFAULT_N_RESULTS,
        system: str = DEFAULT_SYSTEM,
    ) -> None:
        self.model = model
        self.n_results = n_results
        self.system = system

    def retrieve(self, question: str) -> tuple[str, list[dict]]:
        """Return (context_string, raw_chunks) for *question*."""
        chunks = vector_query(question, n_results=self.n_results)
        context = "\n\n".join(
            f"[Source: {c['source']} | {c.get('header') or 'Intro'}]\n{c['text']}"
            for c in chunks
        )
        return context, chunks

    def answer(self, question: str) -> dict:
        """Return dict with keys: answer, sources (list of {source, header, score})."""
        context, chunks = self.retrieve(question)
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=self.system,
            messages=[
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}",
                }
            ],
        )
        return {
            "answer": response.content[0].text,
            "sources": [
                {
                    "source": c["source"],
                    "header": c.get("header", ""),
                    "score": c.get("score"),
                }
                for c in chunks
            ],
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RAG answer using Claude")
    parser.add_argument("question", help="Question to answer from the knowledge base")
    parser.add_argument("--n", type=int, default=DEFAULT_N_RESULTS, help="Number of chunks to retrieve")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Claude model ID")
    args = parser.parse_args()

    result = RAGAnswer(model=args.model, n_results=args.n).answer(args.question)
    print(result["answer"])
    print(f"\nSources ({len(result['sources'])}):")
    for s in result["sources"]:
        print(f"  [{s['score']:.4f}] {s['source']} | {s['header']}")
