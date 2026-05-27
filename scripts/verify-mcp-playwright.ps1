# verify-mcp-playwright.ps1
# Checks @playwright/mcp resolves and .mcp.json registers the playwright server.
#
# Usage:
#   npm run verify:mcp:win
#   powershell -ExecutionPolicy Bypass -File scripts/verify-mcp-playwright.ps1

$ErrorActionPreference = "SilentlyContinue"
$root = Split-Path -Parent $PSScriptRoot
$mcpTarget = "$root\.mcp.json"
$ok = $true

Write-Host ""
Write-Host "Checking npx @playwright/mcp..."
$version = npx -y "@playwright/mcp@latest" --version 2>$null
if ($LASTEXITCODE -ne 0 -or -not $version) {
  Write-Host "  FAIL: could not run @playwright/mcp (check Node.js and network)" -ForegroundColor Red
  $ok = $false
} else {
  Write-Host "  OK: @playwright/mcp ($($version.Trim()))" -ForegroundColor Green
}

if (-not (Test-Path $mcpTarget)) {
  Write-Host "  WARN: .mcp.json missing -- run: npm run setup:playwright:win" -ForegroundColor Yellow
  $ok = $false
} else {
  python3 - $mcpTarget @'
import json, sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text())
pw = data.get("mcpServers", {}).get("playwright")
if not pw:
    print("  FAIL: .mcp.json has no mcpServers.playwright entry", file=sys.stderr); sys.exit(1)
args = pw.get("args") or []
if "@playwright/mcp" not in " ".join(str(a) for a in args) and pw.get("command") != "npx":
    print("  WARN: playwright server may not be @playwright/mcp -- check .mcp.json", file=sys.stderr)
if not pw.get("autoStart", True):
    print("  WARN: playwright autoStart is false -- live-execution may need manual MCP start", file=sys.stderr)
print("  OK: .mcp.json registers playwright MCP (autoStart)")
'@
  if ($LASTEXITCODE -ne 0) { $ok = $false }
}

Write-Host ""
if ($ok) {
  Write-Host "Playwright MCP is configured." -ForegroundColor Green
  Write-Host "In VS Code / Cursor: confirm 'playwright' MCP server is active after reload." -ForegroundColor Yellow
  exit 0
}

Write-Host "Fix: npm run setup:playwright:win  then reload your editor's MCP." -ForegroundColor Red
exit 1
