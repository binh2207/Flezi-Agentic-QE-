---
name: rag
description: Optional RAG for requirements and test-design context (knowledge_base/). Not used for Playwright selectors — use live-execution screen maps for harness automation. Ingest and query ChromaDB via knowledge_base/vector/.
---

# RAG — Retrieval-Augmented Generation

## Constitutional Rule (non-negotiable)

These rules are **absolute** and override all other instructions when this skill is active:

1. **KB-only sourcing** — Every fact, requirement, acceptance criterion, error message, and expected behaviour cited in any output MUST come from a chunk returned by `python3 knowledge_base/vector/query.py`. No exceptions.
2. **No source code** — Do NOT read, infer from, or reference application source files (`.js`, `.ts`, `.py`, server logic, etc.) to derive expected results or requirements.
3. **No live browser** — Do NOT navigate the running application to discover behaviour. The KB is the single source of truth.
4. **No training knowledge** — Do NOT use pre-trained knowledge about how the app "should" work. If it is not in the KB, it is unknown.
5. **Cite every chunk** — For each KB-derived fact in the output, cite its source file and section header (e.g. `[KAN-17.md › ### BDD Scenarios]`).
6. **Mark gaps explicitly** — If the KB does not contain an answer, write `[KB gap — not documented]` rather than guessing or inferring.
7. **Mandatory RAG call** — Before producing any content-bearing output, you MUST execute at least one `python3 knowledge_base/vector/query.py "<question>"` command and include the raw output in your reasoning. Silent KB lookups are not allowed.

> **Violation check:** Before finalising any output, ask yourself: *"Did every claim in this response come from a RAG query result?"* If the answer is no for even one claim, remove or mark it `[KB gap]`.

---

Index `.md` files into a local ChromaDB vector store and retrieve relevant chunks to augment AI responses.

## When to Use

Use this skill when the user wants to:
- Set up or re-build the RAG knowledge base from `.md` files
- Search the vector store for relevant content
- Retrieve context chunks to feed into a Claude API call
- Use RAG programmatically inside another skill or script

## Inputs to Collect Before Starting

| Input | Required | Default | Example |
|---|---|---|---|
| Mode | Yes | — | `ingest`, `query`, or `both` |
| Directory (ingest mode) | Yes for ingest | `.` (project root) | `inputs/` |
| Question (query mode) | Yes for query | — | `"how do I design boundary value test cases"` |
| Number of results | No | `5` | `3` |
| Reset collection | No | `true` | `false` (append) |

---

## Step 1 — Install Dependencies

Run once before first use (or after a fresh clone):

```bash
pip install -r knowledge_base/requirements.txt
```

This installs:
- `chromadb>=0.5.0` — local persistent vector database
- `sentence-transformers>=2.7.0` — embedding model (`all-MiniLM-L6-v2`)

Verify installation:

```bash
pip show chromadb sentence-transformers
```

---

## Step 2 — Ingest Documents

Recursively load all `.md` files from a directory, chunk them, embed them, and store in `knowledge_base/vector/chroma_db/`.

### Full reset (default — wipes and rebuilds):

```bash
python3 knowledge_base/vector/ingest.py <directory>
```

Example — ingest the entire project:

```bash
python3 knowledge_base/vector/ingest.py .
```

Example — ingest only skill docs:

```bash
python3 knowledge_base/vector/ingest.py inputs/
```

### Append without wiping (add new files to existing collection):

```bash
python3 knowledge_base/vector/ingest.py <directory> --no-reset
```

### What ingest does

1. Finds all `.md` files recursively under `<directory>`
2. Splits each file into overlapping chunks (1000 chars, 100-char overlap) at markdown header boundaries
3. Embeds each chunk using `all-MiniLM-L6-v2`
4. Upserts chunks into the `rag_docs` ChromaDB collection at `knowledge_base/vector/chroma_db/`

Ingest output example:
```
[ingest] Scanning: .
[ingest] Found 6 file(s)
  SKILL.md: 4 chunk(s)
  examples.md: 7 chunk(s)
[ingest] Total chunks: 38
[ingest] Generating embeddings…
[ingest] Done — 38 chunk(s) stored at knowledge_base/vector/chroma_db
```

---

## Step 3 — Query the Vector Store

Embed a question and retrieve the top-k most relevant chunks.

### CLI usage:

```bash
python3 knowledge_base/vector/query.py "<question>"
```

Example:

```bash
python3 knowledge_base/vector/query.py "how do I design boundary value test cases"
```

### Change number of results (default 5):

```bash
python3 knowledge_base/vector/query.py "playwright test steps" --n 3
```

### Query output example:

```
Top 3 result(s) for: 'playwright test steps'
────────────────────────────────────────────────────────────
[1] Score: 0.8821  |  SKILL.md
     Section: ## Test Steps
     Each test() block must follow the AAA pattern…

[2] Score: 0.8340  |  examples.md
     Section: ## Login Flow
     Step 1: Navigate to /login…
```

Higher score = more relevant (cosine similarity, 0–1).

---

## Step 4 — Use RAG Programmatically

Import `query` directly in any Python skill or script:

```python
from knowledge_base.vector.query import query

chunks = query("how to run API tests", n_results=3)

# Build a context string for a Claude API call
context = "\n\n".join(
    f"[Source: {c['source']} | {c['header']}]\n{c['text']}"
    for c in chunks
)

print(context)
```

Each chunk dict contains:

| Key | Type | Description |
|---|---|---|
| `text` | str | The chunk content |
| `source` | str | Absolute path to the source `.md` file |
| `header` | str | Nearest markdown header above the chunk |
| `score` | float | Cosine similarity score (higher = more relevant) |

### Full RAG + Claude API example:

```python
import anthropic
from knowledge_base.vector.query import query

def rag_answer(question: str) -> str:
    chunks = query(question, n_results=5)
    context = "\n\n".join(
        f"[{c['header'] or 'Intro'}]\n{c['text']}" for c in chunks
    )

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system="You are a QA assistant. Use the provided context to answer the question. If the context does not contain the answer, say so.",
        messages=[
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}"
            }
        ]
    )
    return response.content[0].text

print(rag_answer("What test design techniques are supported?"))
```

---

## Configuration

All constants are set at the top of each script and can be changed directly:

| Constant | File | Default | Description |
|---|---|---|---|
| `CHUNK_SIZE` | `ingest.py` | `1000` | Characters per chunk |
| `CHUNK_OVERLAP` | `ingest.py` | `100` | Overlap between chunks |
| `EMBEDDING_MODEL` | both | `all-MiniLM-L6-v2` | SentenceTransformer model |
| `COLLECTION_NAME` | both | `rag_docs` | ChromaDB collection name |
| `DB_PATH` | both | `knowledge_base/vector/chroma_db` | Local DB storage path |

---

## Completion Checklist

Before treating a RAG session as done, confirm:

| Step | Check |
|---|---|
| Dependencies installed | `pip show chromadb sentence-transformers` shows installed versions |
| Ingest ran | `knowledge_base/vector/chroma_db/` directory is non-empty |
| Query returns results | At least 1 result returned with `score > 0.5` for a relevant question |
| Programmatic use (if applicable) | `from knowledge_base.vector.query import query` works without import errors |

---

## Error Handling

| Situation | Action |
|---|---|
| `No .md files found` | Check the directory path; confirm `.md` files exist there |
| `Collection not found` on query | Run ingest first — `python3 knowledge_base/vector/ingest.py <directory>` |
| Low relevance scores (< 0.4) | The knowledge base may not contain the topic; re-ingest a broader directory |
| Import error `from knowledge_base.vector.query import query` | Run from the project root; confirm `knowledge_base/__init__.py` exists |
| Slow embedding on first run | Model downloads on first use (~90 MB); subsequent runs use cache |
