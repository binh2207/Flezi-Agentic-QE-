# Knowledge base (KB) guidelines

Optional RAG layer for **requirements and test-design context**. It does **not** replace the Playwright harness or live screen maps.

## Use KB for

- Product requirements, acceptance criteria, BDD scenarios in markdown
- Test-case design before automation ([test-case-design](../skills/test-case-design/SKILL.md))
- Domain rules, naming conventions, prior QA decisions documented in `.md`
- Answering “what should the app do?” when docs exist in the repo

## Do not use KB for

- Playwright **selectors** or locators → use [live-execution](../skills/live-execution/SKILL.md) screen maps
- Discovering current UI layout → use MCP browser, not the vector store
- Proving a test passed/failed → use `npx playwright test`
- Inventing behaviour not present in ingested documents → mark `[KB gap — not documented]`

## Components

| Path | Role |
|------|------|
| `knowledge_base/vector/` | Ingest + query (ChromaDB) |
| `knowledge_base/agent/` | Agentic RAG graph (retrieve, grade, answer) |
| `kb_server/` | FastAPI wrapper (`web_app.py`) |

## Setup

```bash
npm run setup:kb
# or: pip install -r requirements.txt

export ANTHROPIC_API_KEY=...   # required for agentic chat API
```

## Ingest documents

Ingest `.md` files into `knowledge_base/vector/chroma_db/`:

```bash
# Full rebuild (default)
python3 knowledge_base/vector/ingest.py inputs/

# Append without wiping
python3 knowledge_base/vector/ingest.py inputs/ --no-reset

# Broader corpus (requirements + skills + flows)
python3 knowledge_base/vector/ingest.py .
```

Good sources to ingest: user stories, Confluence exports, `inputs/test-cases/`, feature specs, API docs in markdown.

## Query from CLI

```bash
python3 knowledge_base/vector/query.py "checkout payment rules" --n 5
```

Use output to inform test-case design. Cite source paths from the query results.

## HTTP API

```bash
npm run kb:serve
# http://127.0.0.1:8765
```

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness |
| POST | `/kb/ingest` | Body: `{ "directory": "inputs/", "reset": true }` |
| GET | `/kb/docs` | List ingested sources |
| DELETE | `/kb/docs?source_substring=...` | Remove chunks by source path |
| POST | `/kb/chat` | Agentic RAG Q&A |
| POST | `/kb/chat/legacy` | One-shot RAG (comparison) |

Optional env: `KB_BIND_HOST`, `KB_BIND_PORT` (default `127.0.0.1:8765`), `KB_GRADER_MODEL`.

## Workflow with harness

```text
(Optional) KB query / test-case-design  →  inputs/test-cases/*.md
                                              ↓
        Harness (required for automation)  →  live-execution → screen maps → POM
```

KB and harness are **parallel inputs** to quality; only the harness path produces runnable Playwright tests.

## Agent skill

Follow [skills/rag/SKILL.md](../skills/rag/SKILL.md) when the RAG skill is active (strict KB-only answers).

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Collection not found` on query | Run ingest first |
| Empty or irrelevant results | Ingest a broader directory; rephrase query |
| `ANTHROPIC_API_KEY is missing` | Export key before `kb:serve` or agentic chat |
| Slow first ingest | Model download (~90 MB); later runs use cache |
| Conflicting with harness | Remember: selectors always from screen maps, not KB |
