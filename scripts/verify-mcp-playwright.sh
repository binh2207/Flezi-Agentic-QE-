#!/usr/bin/env bash
# Checks Playwright MCP package resolves and project .mcp.json registers playwright.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
target="$root/.mcp.json"
ok=1

echo "Checking npx @playwright/mcp…"
if ! npx -y @playwright/mcp@latest --version >/dev/null 2>&1; then
  echo "FAIL: could not run @playwright/mcp (check Node.js and network)" >&2
  ok=0
else
  version="$(npx -y @playwright/mcp@latest --version 2>/dev/null | head -1)"
  echo "OK: @playwright/mcp ($version)"
fi

if [[ ! -f "$target" ]]; then
  echo "WARN: $target missing — run: npm run setup:mcp" >&2
  ok=0
else
  python3 - "$target" <<'PY'
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text())
pw = data.get("mcpServers", {}).get("playwright")
if not pw:
    print("FAIL: .mcp.json has no mcpServers.playwright entry", file=sys.stderr)
    sys.exit(1)
args = pw.get("args") or []
if "@playwright/mcp" not in " ".join(str(a) for a in args) and pw.get("command") != "npx":
    print("WARN: playwright server may not be @playwright/mcp — check .mcp.json", file=sys.stderr)
if not pw.get("autoStart", True):
    print("WARN: playwright autoStart is false — live-execution may need manual MCP start", file=sys.stderr)
print("OK: .mcp.json registers playwright MCP (autoStart)")
PY
  if [[ $? -ne 0 ]]; then ok=0; fi
fi

if [[ $ok -eq 1 ]]; then
  echo ""
  echo "Playwright MCP is configured. In Cursor: Settings → MCP → confirm 'playwright' is green after reload."
  exit 0
fi

echo ""
echo "Fix: npm run setup:mcp && reload Cursor MCP"
exit 1
