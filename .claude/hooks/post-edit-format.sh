#!/bin/bash
# =============================================================================
# post-edit-format.sh — PostToolUse hook: auto-format edited files
# =============================================================================
# Runs the appropriate formatter based on file extension.
# Customize the formatter commands for your project's stack.
# =============================================================================

INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)

[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0

case "$FILE" in
  *.go)     command -v gofumpt >/dev/null && gofumpt -w "$FILE" ;;
  *.js|*.ts|*.jsx|*.tsx|*.json|*.css|*.html)
            command -v prettier >/dev/null && prettier --write "$FILE" 2>/dev/null ;;
  *.py)     command -v ruff >/dev/null && ruff format "$FILE" 2>/dev/null ;;
esac
