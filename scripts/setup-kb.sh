#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

echo "Installing KB / RAG Python dependencies…"
python3 -m pip install -r requirements.txt

echo "KB ready. Set ANTHROPIC_API_KEY and run: npm run kb:serve"
