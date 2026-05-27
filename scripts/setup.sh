#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
bash "$root/scripts/setup-playwright.sh"
bash "$root/scripts/setup-mcp.sh"
bash "$root/scripts/setup-kb.sh"
echo "Full setup complete (Playwright + optional KB)."
