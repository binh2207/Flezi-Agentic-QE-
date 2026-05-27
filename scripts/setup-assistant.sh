#!/usr/bin/env bash
# One-time assistant registration for the AIQE Playwright Harness.
#
# Usage:
#   bash scripts/setup-assistant.sh [claudecode|cursor|copilot|all]
#   npm run setup:claudecode
#   npm run setup:cursor
#   npm run setup:copilot
#   npm run setup:assistants
#
# Runs on Git Bash / WSL / macOS. Windows native: use setup-assistant.ps1 instead.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
target="${1:-all}"

# -- Helpers ------------------------------------------------------------------
print_header() {
  echo ""
  echo "============================================"
  echo "  AIQE Harness -- $1 setup"
  echo "============================================"
}

ok()   { echo "  [OK]  $*"; }
info() { echo "  -->   $*"; }

# -- Core: Playwright + MCP + Harness SDK (shared) ----------------------------
setup_core() {
  echo ""
  echo "-- [1/3] Installing Playwright dependencies..."
  bash "$root/scripts/setup-playwright.sh"
  echo ""
  echo "-- [2/3] Configuring MCP (playwright server)..."
  bash "$root/scripts/setup-mcp.sh"
  echo ""
  echo "-- [3/3] Installing Harness MCP server dependencies..."
  npm install --prefix "$root" --silent
  ok "Harness MCP server dependencies installed."
}

# -- Claude Code --------------------------------------------------------------
setup_claudecode() {
  print_header "Claude Code"

  # Project-level symlink: .claude/skills -> skills/
  if [[ ! -e "$root/.claude/skills" ]]; then
    mkdir -p "$root/.claude"
    ln -sfn "$root/skills" "$root/.claude/skills"
    ok "Created .claude/skills -> skills/"
  else
    ok ".claude/skills already linked."
  fi

  # User-level skills (~/.claude/skills/harness-*)
  if [[ -d "$HOME/.claude" || ! -e "$HOME/.claude" ]]; then
    mkdir -p "$HOME/.claude/skills"
    for dir in "$root"/skills/*/; do
      name=$(basename "$dir")
      ln -sfn "$dir" "$HOME/.claude/skills/harness-$name"
      ok "Linked ~/.claude/skills/harness-$name"
    done
  fi

  echo ""
  echo "  Next steps:"
  info "Open this folder in your terminal:"
  info "  cd $(basename "$root") && claude"
  info "Claude Code reads CLAUDE.md and discovers skills automatically."
  info "Verify: ask 'What harness skills are available?'"
}

# -- Cursor -------------------------------------------------------------------
setup_cursor() {
  print_header "Cursor"

  # Project-level symlink: .cursor/skills -> skills/
  if [[ ! -e "$root/.cursor/skills" ]]; then
    mkdir -p "$root/.cursor"
    ln -sfn "$root/skills" "$root/.cursor/skills"
    ok "Created .cursor/skills -> skills/"
  else
    ok ".cursor/skills already linked."
  fi

  # User-level skills (~/.cursor/skills/harness-*)
  if [[ -d "$HOME/.cursor" || ! -e "$HOME/.cursor" ]]; then
    mkdir -p "$HOME/.cursor/skills"
    for dir in "$root"/skills/*/; do
      name=$(basename "$dir")
      ln -sfn "$dir" "$HOME/.cursor/skills/harness-$name"
      ok "Linked ~/.cursor/skills/harness-$name"
    done
  fi

  echo ""
  echo "  Next steps:"
  info "Open this folder in Cursor."
  info "Restart Cursor (or Reload MCP) to activate the playwright server."
  info "Verify MCP: npm run verify:mcp"
  info "Ask: 'Run pipeline-orchestrator for feature checkout'"
}

# -- GitHub Copilot -----------------------------------------------------------
setup_copilot() {
  print_header "GitHub Copilot"

  # Verify copilot-instructions.md exists
  instructions="$root/.github/copilot-instructions.md"
  if [[ ! -f "$instructions" ]]; then
    echo "ERROR: .github/copilot-instructions.md not found." >&2
    exit 1
  fi
  ok ".github/copilot-instructions.md present."

  # Create or update .vscode/settings.json to enable instruction files
  vscode_dir="$root/.vscode"
  settings="$vscode_dir/settings.json"
  mkdir -p "$vscode_dir"

  if [[ ! -f "$settings" ]]; then
    cat > "$settings" <<'JSON'
{
  "github.copilot.chat.codeGeneration.useInstructionFiles": true,
  "github.copilot.enable": {
    "*": true
  }
}
JSON
    ok "Created .vscode/settings.json (Copilot instruction files enabled)."
  elif grep -q "useInstructionFiles" "$settings"; then
    ok ".vscode/settings.json already enables Copilot instruction files."
  else
    python3 - "$settings" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
data = json.loads(p.read_text())
data["github.copilot.chat.codeGeneration.useInstructionFiles"] = True
p.write_text(json.dumps(data, indent=2) + "\n")
print("  [OK] Updated .vscode/settings.json.")
PY
  fi

  # .vscode/mcp.json provides aiqe-harness + playwright MCP for VS Code Copilot
  if [[ -f "$vscode_dir/mcp.json" ]]; then
    ok ".vscode/mcp.json already present (Harness MCP + Playwright MCP configured)."
  else
    ok ".vscode/mcp.json present."
  fi

  echo ""
  echo "  Next steps:"
  info "Open this folder in VS Code (requires VS Code >= 1.99 for MCP support)."
  info "VS Code will prompt to start MCP servers — click Allow."
  info "In Copilot Chat, MCP tools are available: list_skills, read_skill, read_flow, run_tests."
  info "Ask: 'Run the harness for checkout using inputs/manual-flows/checkout.md'"
}

# -- Dispatch -----------------------------------------------------------------
case "$target" in
  claudecode|claude)
    setup_core
    setup_claudecode
    ;;
  cursor)
    setup_core
    setup_cursor
    ;;
  copilot)
    setup_core
    setup_copilot
    ;;
  all)
    setup_core
    setup_claudecode
    setup_cursor
    setup_copilot
    echo ""
    echo "  All three assistants configured."
    ;;
  *)
    echo "Usage: $0 [claudecode|cursor|copilot|all]"
    echo ""
    echo "  claudecode   Set up for Claude Code"
    echo "  cursor       Set up for Cursor"
    echo "  copilot      Set up for GitHub Copilot (VS Code)"
    echo "  all          Set up for all assistants (default)"
    echo ""
    echo "  Windows native: use scripts/setup-assistant.ps1 instead."
    exit 1
    ;;
esac

echo ""
echo "Setup complete. Full details: docs/register-your-assistant.md"
