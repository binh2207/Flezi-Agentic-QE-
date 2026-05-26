#!/usr/bin/env bash
# Ensures project .mcp.json includes Playwright MCP (autoStart) for live-execution.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
example="$root/.mcp.json.example"
target="$root/.mcp.json"

if [[ ! -f "$example" ]]; then
  echo "Missing .mcp.json.example" >&2
  exit 1
fi

python3 - "$example" "$target" <<'PY'
import json
import sys
from pathlib import Path

example_path = Path(sys.argv[1])
target_path = Path(sys.argv[2])
example = json.loads(example_path.read_text())
playwright = example.get("mcpServers", {}).get("playwright")
defaults = example.get("defaults", {})

if not playwright:
    print("No playwright server in .mcp.json.example", file=sys.stderr)
    sys.exit(1)

if not target_path.exists():
    target_path.write_text(json.dumps(example, indent=2) + "\n")
    print(f"Created {target_path.name} from example (playwright + jira).")
    sys.exit(0)

data = json.loads(target_path.read_text())
servers = data.setdefault("mcpServers", {})
changed = False

if "playwright" not in servers:
    servers["playwright"] = playwright
    changed = True
    print("Added playwright MCP server to .mcp.json")

for key, value in defaults.items():
    if key not in data.get("defaults", {}):
        data.setdefault("defaults", {})[key] = value
        changed = True

if changed:
    target_path.write_text(json.dumps(data, indent=2) + "\n")
else:
    print(".mcp.json already includes playwright MCP")
PY

echo ""
echo "Next: restart Cursor (or reload MCP) so the playwright server starts."
echo "Verify: npm run verify:mcp"
