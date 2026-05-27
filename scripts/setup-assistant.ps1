# setup-assistant.ps1
# One-time assistant registration for the AIQE Playwright Harness (Windows native).
#
# Usage:
#   .\scripts\setup-assistant.ps1 [claudecode|cursor|copilot|all]
#   npm run setup:claudecode:win
#   npm run setup:cursor:win
#   npm run setup:copilot:win
#   npm run setup:assistants:win
#
# Requires: Node.js, npm, Python 3 on PATH.
# Symlinks need Developer Mode ON (Windows Settings -> For Developers) or run as Admin.
param(
  [ValidateSet("claudecode","claude","cursor","copilot","all","")]
  [string]$Target = "all"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

# -- Helpers ------------------------------------------------------------------
function Print-Header([string]$title) {
  Write-Host ""
  Write-Host "============================================" -ForegroundColor Cyan
  Write-Host ("  AIQE Harness -- {0} setup" -f $title) -ForegroundColor Cyan
  Write-Host "============================================" -ForegroundColor Cyan
}

function Ok([string]$msg)   { Write-Host "  [OK]  $msg" -ForegroundColor Green }
function Info([string]$msg) { Write-Host "  -->   $msg" -ForegroundColor Yellow }
function Err([string]$msg)  { Write-Host "  [ERR] $msg" -ForegroundColor Red }

function New-Symlink([string]$link, [string]$target) {
  if (Test-Path $link) {
    Ok "'$link' already exists."
    return
  }
  try {
    New-Item -ItemType SymbolicLink -Path $link -Target $target | Out-Null
    Ok "Created symlink: $link -> $target"
  } catch {
    # Fallback: directory junction (no elevation needed)
    try {
      cmd /c mklink /J "$link" "$target" | Out-Null
      Ok "Created junction: $link -> $target"
    } catch {
      Err "Could not create link '$link'. Enable Developer Mode or run as Admin."
    }
  }
}

# -- Core: Playwright + MCP + Harness SDK (shared) ----------------------------
function Setup-Core {
  Write-Host ""
  Write-Host "-- [1/3] Installing Playwright dependencies..."
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

  Write-Host ""
  Write-Host "-- [2/3] Configuring MCP (playwright server)..."
  $example = "$root\.mcp.json.example"
  $mcpTarget = "$root\.mcp.json"

  if (-not (Test-Path $example)) {
    Err "Missing .mcp.json.example"; exit 1
  }

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
  Write-Host "-- [3/3] Installing Harness MCP server dependencies..."
  Push-Location $root
  npm install --silent
  Pop-Location
  Ok "Harness MCP server dependencies installed."
}

# -- Claude Code --------------------------------------------------------------
function Setup-ClaudeCode {
  Print-Header "Claude Code"

  # Project-level: .claude\skills -> skills\
  $projectLink = "$root\.claude\skills"
  if (-not (Test-Path "$root\.claude")) { New-Item -ItemType Directory "$root\.claude" | Out-Null }
  New-Symlink $projectLink "$root\skills"

  # User-level: ~\.claude\skills\harness-*
  $userClaudeSkills = "$env:USERPROFILE\.claude\skills"
  if (-not (Test-Path $userClaudeSkills)) { New-Item -ItemType Directory -Force $userClaudeSkills | Out-Null }
  Get-ChildItem "$root\skills" -Directory | ForEach-Object {
    New-Symlink "$userClaudeSkills\harness-$($_.Name)" $_.FullName
  }

  Write-Host ""
  Write-Host "  Next steps:"
  Info "Open a terminal in this folder and run: claude"
  Info "Claude Code reads CLAUDE.md and discovers skills automatically."
  Info "Verify: ask 'What harness skills are available?'"
}

# -- Cursor -------------------------------------------------------------------
function Setup-Cursor {
  Print-Header "Cursor"

  # Project-level: .cursor\skills -> skills\
  $projectLink = "$root\.cursor\skills"
  if (-not (Test-Path "$root\.cursor")) { New-Item -ItemType Directory "$root\.cursor" | Out-Null }
  New-Symlink $projectLink "$root\skills"

  # User-level: ~\.cursor\skills\harness-*
  $userCursorSkills = "$env:USERPROFILE\.cursor\skills"
  if (-not (Test-Path $userCursorSkills)) { New-Item -ItemType Directory -Force $userCursorSkills | Out-Null }
  Get-ChildItem "$root\skills" -Directory | ForEach-Object {
    New-Symlink "$userCursorSkills\harness-$($_.Name)" $_.FullName
  }

  Write-Host ""
  Write-Host "  Next steps:"
  Info "Open this folder in Cursor."
  Info "Restart Cursor (or Reload MCP) to activate the playwright server."
  Info "Verify MCP: npm run verify:mcp"
  Info "Ask: 'Run pipeline-orchestrator for feature checkout'"
}

# -- GitHub Copilot -----------------------------------------------------------
function Setup-Copilot {
  Print-Header "GitHub Copilot"

  $instructions = "$root\.github\copilot-instructions.md"
  if (-not (Test-Path $instructions)) {
    Err ".github\copilot-instructions.md not found."; exit 1
  }
  Ok ".github\copilot-instructions.md present."

  # Create or update .vscode\settings.json
  $vscodeDir = "$root\.vscode"
  $settings  = "$vscodeDir\settings.json"
  if (-not (Test-Path $vscodeDir)) { New-Item -ItemType Directory $vscodeDir | Out-Null }

  if (-not (Test-Path $settings)) {
    @'
{
  "github.copilot.chat.codeGeneration.useInstructionFiles": true,
  "github.copilot.enable": {
    "*": true
  }
}
'@ | Out-File -Encoding utf8 $settings
    Ok "Created .vscode\settings.json (Copilot instruction files enabled)."
  } else {
    $content = Get-Content $settings -Raw
    if ($content -match "useInstructionFiles") {
      Ok ".vscode\settings.json already enables Copilot instruction files."
    } else {
      python3 - $settings @'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
data = json.loads(p.read_text())
data["github.copilot.chat.codeGeneration.useInstructionFiles"] = True
p.write_text(json.dumps(data, indent=2) + "\n")
print("  [OK] Updated .vscode/settings.json.")
'@
    }
  }

  # .vscode/mcp.json provides aiqe-harness + playwright MCP for VS Code Copilot
  $vscodeMcp = "$root\.vscode\mcp.json"
  if (Test-Path $vscodeMcp) {
    Ok ".vscode\mcp.json already present (Harness MCP + Playwright MCP configured)."
  } else {
    Ok ".vscode\mcp.json present."
  }

  Write-Host ""
  Write-Host "  Next steps:"
  Info "Open this folder in VS Code (requires VS Code >= 1.99 for MCP support)."
  Info "VS Code will prompt to start MCP servers -- click Allow."
  Info "In Copilot Chat, MCP tools are available: list_skills, read_skill, read_flow, run_tests."
  Info "Ask: 'Run the harness for checkout using inputs/manual-flows/checkout.md'"
}

# -- Dispatch -----------------------------------------------------------------
switch ($Target) {
  { $_ -in "claudecode","claude" } {
    Setup-Core; Setup-ClaudeCode
  }
  "cursor" {
    Setup-Core; Setup-Cursor
  }
  "copilot" {
    Setup-Core; Setup-Copilot
  }
  default {
    # "all" or ""
    Setup-Core
    Setup-ClaudeCode
    Setup-Cursor
    Setup-Copilot
    Write-Host ""
    Ok "All three assistants configured."
  }
}

Write-Host ""
Write-Host "Setup complete. Full details: docs/register-your-assistant.md" -ForegroundColor Cyan
