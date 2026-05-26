"""
RAG query: embed a question and retrieve the top-k most relevant chunks from ChromaDB.
"""
import argparse
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "rag_docs"
DB_PATH = str(Path(__file__).parent / "chroma_db")


def query(question: str, n_results: int = 5) -> list[dict]:
    """
    Search the vector store for chunks relevant to *question*.
    Returns a list of dicts with keys: text, source, header, score.
    """
    model = SentenceTransformer(EMBEDDING_MODEL)
    embedding = model.encode([question]).tolist()

    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection(COLLECTION_NAME)

    results = collection.query(
        query_embeddings=embedding,
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for i, doc in enumerate(results["documents"][0]):
        chunks.append({
            "text": doc,
            "source": results["metadatas"][0][i]["source"],
            "header": results["metadatas"][0][i]["header"],
            "score": 1 - results["distances"][0][i],   # cosine similarity (higher = more relevant)
        })

    return chunks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the RAG vector store")
    parser.add_argument("question", help="Question or search phrase")
    parser.add_argument("--n", type=int, default=5, help="Number of results to return (default: 5)")
    args = parser.parse_args()

    results = query(args.question, args.n)

    print(f"\nTop {len(results)} result(s) for: '{args.question}'\n{'─' * 60}")
    for i, r in enumerate(results, 1):
        print(f"[{i}] Score: {r['score']:.4f}  |  {Path(r['source']).name}")
        if r["header"]:
            print(f"     Section: {r['header']}")
        print(f"     {r['text'][:300]}{'…' if len(r['text']) > 300 else ''}")
        print()
