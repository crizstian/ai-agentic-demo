#!/bin/bash
# =============================================================================
# validate-push.sh — PreToolUse hook: warn before git push
# =============================================================================
# Intercepts Bash commands containing "git push" and warns the user.
# =============================================================================

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

if echo "$COMMAND" | grep -qE 'git\s+push'; then
  BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
  if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
    echo "WARN: Pushing to protected branch '$BRANCH'. Confirm with user."
  fi
fi
