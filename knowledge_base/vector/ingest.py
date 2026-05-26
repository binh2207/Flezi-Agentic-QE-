"""
RAG ingestion pipeline: load .md files → chunk → embed → store in ChromaDB
"""
import hashlib
import re
import argparse
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHUNK_SIZE = 1000       # characters per chunk
CHUNK_OVERLAP = 100     # overlap between consecutive chunks
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "rag_docs"
DB_PATH = str(Path(__file__).parent / "chroma_db")


def load_md_files(directory: str) -> list[dict]:
    """Recursively load all .md files from a directory."""
    docs = []
    for path in Path(directory).rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        docs.append({"source": str(path), "content": text})
    return docs


def chunk_markdown(text: str, source: str) -> list[dict]:
    """
    Split markdown into overlapping chunks.
    Splits on headers first to preserve semantic boundaries,
    then further splits large sections by CHUNK_SIZE with CHUNK_OVERLAP.
    """
    header_re = re.compile(r"^#{1,6}\s+.+$", re.MULTILINE)
    sections: list[dict] = []
    last_end = 0
    current_header = ""

    for match in header_re.finditer(text):
        body = text[last_end : match.start()].strip()
        if body:
            sections.append({"header": current_header, "text": body})
        current_header = match.group().strip()
        last_end = match.end()

    tail = text[last_end:].strip()
    if tail:
        sections.append({"header": current_header, "text": tail})

    if not sections:
        sections = [{"header": "", "text": text.strip()}]

    chunks: list[dict] = []
    chunk_idx = 0
    # Use a short hash of the full path so IDs are globally unique even when filenames repeat
    path_hash = hashlib.md5(source.encode()).hexdigest()[:8]
    stem = f"{Path(source).stem}_{path_hash}"

    for section in sections:
        full = f"{section['header']}\n{section['text']}".strip() if section["header"] else section["text"]
        start = 0
        while start < len(full):
            end = start + CHUNK_SIZE
            piece = full[start:end].strip()
            if piece:
                chunks.append({
                    "id": f"{stem}_{chunk_idx}",
                    "text": piece,
                    "source": source,
                    "header": section["header"],
                })
                chunk_idx += 1
            if end >= len(full):
                break
            start = end - CHUNK_OVERLAP

    return chunks


def ingest(directory: str, reset: bool = True) -> int:
    """
    Ingest all .md files from *directory* into ChromaDB.
    Returns the total number of chunks stored.
    """
    print(f"[ingest] Scanning: {directory}")
    docs = load_md_files(directory)
    if not docs:
        print("[ingest] No .md files found.")
        return 0
    print(f"[ingest] Found {len(docs)} file(s)")

    all_chunks: list[dict] = []
    for doc in docs:
        chunks = chunk_markdown(doc["content"], doc["source"])
        all_chunks.extend(chunks)
        print(f"  {Path(doc['source']).name}: {len(chunks)} chunk(s)")

    print(f"\n[ingest] Total chunks: {len(all_chunks)}")
    print("[ingest] Loading embedding model…")
    model = SentenceTransformer(EMBEDDING_MODEL)

    texts = [c["text"] for c in all_chunks]
    print("[ingest] Generating embeddings…")
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    print("[ingest] Storing in ChromaDB…")
    client = chromadb.PersistentClient(path=DB_PATH)

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

    collection = client.get_or_create_collection(COLLECTION_NAME)

    # ChromaDB add() is idempotent on duplicate IDs when using upsert
    collection.upsert(
        ids=[c["id"] for c in all_chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{"source": c["source"], "header": c["header"]} for c in all_chunks],
    )

    print(f"[ingest] Done — {len(all_chunks)} chunk(s) stored at {DB_PATH}\n")
    return len(all_chunks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest .md files into the RAG vector store")
    parser.add_argument("directory", help="Directory containing .md files (searched recursively)")
    parser.add_argument("--no-reset", action="store_true", help="Append to existing collection instead of resetting")
    args = parser.parse_args()
    ingest(args.directory, reset=not args.no_reset)
