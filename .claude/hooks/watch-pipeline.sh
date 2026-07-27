#!/bin/bash
# =============================================================================
# watch-pipeline.sh — PostToolUse hook: detect CI/CD commands
# =============================================================================
# Logs pipeline-related commands for session-end summary.
# =============================================================================

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

if echo "$COMMAND" | grep -qiE '(harness|pipeline|deploy|ci|cd)'; then
  TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  echo "$TIMESTAMP | $COMMAND" >> /tmp/claude-pipeline.log
fi
