# setup-playwright.ps1
# Install Playwright deps, Chromium, and configure .mcp.json (Windows native).
#
# Usage:
#   npm run setup:playwright:win
#   powershell -ExecutionPolicy Bypass -File scripts/setup-playwright.ps1
#
# Requires: Node.js, npm, Python 3 on PATH.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

function Ok([string]$msg)   { Write-Host "  [OK]  $msg" -ForegroundColor Green }
function Info([string]$msg) { Write-Host "  -->   $msg" -ForegroundColor Yellow }
function Err([string]$msg)  { Write-Host "  [ERR] $msg" -ForegroundColor Red; exit 1 }

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AIQE Harness -- Playwright setup (Win)  " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# -- [1/2] Playwright framework -----------------------------------------------
Write-Host ""
Write-Host "-- [1/2] Installing Playwright dependencies..."
Push-Location "$root\playwright-automation-framework"
npm install
npx playwright install chromium
if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
  Ok "Created .env -- set BASE_URL before running tests."
} else {
  Ok ".env already exists."
}
Pop-Location

# -- [2/2] MCP config ---------------------------------------------------------
Write-Host ""
Write-Host "-- [2/2] Configuring MCP (playwright server)..."
$example   = "$root\.mcp.json.example"
$mcpTarget = "$root\.mcp.json"

if (-not (Test-Path $example)) { Err "Missing .mcp.json.example" }

python3 - $example $mcpTarget @'
import json, sys
from pathlib import Path

example_path = Path(sys.argv[1])
target_path  = Path(sys.argv[2])
example      = json.loads(example_path.read_text())
playwright   = example.get("mcpServers", {}).get("playwright")

if not playwright:
    print("No playwright server in .mcp.json.example", file=sys.stderr); sys.exit(1)

if not target_path.exists():
    target_path.write_text(json.dumps(example, indent=2) + "\n")
    print("  [OK] Created .mcp.json from example."); sys.exit(0)

data    = json.loads(target_path.read_text())
servers = data.setdefault("mcpServers", {})
if "playwright" not in servers:
    servers["playwright"] = playwright
    target_path.write_text(json.dumps(data, indent=2) + "\n")
    print("  [OK] Added playwright MCP server to .mcp.json")
else:
    print("  [OK] .mcp.json already includes playwright MCP")
'@

Write-Host ""
Ok "Playwright harness ready."
Info "Next: set BASE_URL in playwright-automation-framework\.env"
Info "Then run: npm test"
Info "To register your assistant: npm run setup:copilot:win"
Info "To verify MCP:              npm run verify:mcp:win"
