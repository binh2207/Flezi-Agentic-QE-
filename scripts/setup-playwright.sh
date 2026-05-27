#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root/playwright-automation-framework"

echo "Installing Playwright framework…"
npm install
npx playwright install chromium

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env — set BASE_URL before running tests."
fi

echo "Playwright harness ready. Run: npm test (from repo root)"
echo "For live QA in Cursor: npm run setup:mcp && npm run verify:mcp"
