#!/usr/bin/env bash
# Link harness skills into personal assistant folders (optional).
# Run from repository root.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
target="${1:-all}"

link_cursor() {
  mkdir -p ~/.cursor/skills
  for dir in "$root"/skills/*/; do
    name=$(basename "$dir")
    ln -sfn "$dir" ~/.cursor/skills/harness-$name
    echo "Cursor: ~/.cursor/skills/harness-$name"
  done
}

link_claude() {
  mkdir -p ~/.claude/skills
  for dir in "$root"/skills/*/; do
    name=$(basename "$dir")
    ln -sfn "$dir" ~/.claude/skills/harness-$name
    echo "Claude: ~/.claude/skills/harness-$name"
  done
}

case "$target" in
  cursor) link_cursor ;;
  claude) link_claude ;;
  all) link_cursor; link_claude ;;
  *)
    echo "Usage: $0 [cursor|claude|all]"
    exit 1
    ;;
esac

echo "Done. Copilot: use repo .github/copilot-instructions.md when workspace is this project."
