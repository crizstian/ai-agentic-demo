#!/bin/bash
# =============================================================================
# audit-mcp.sh — PostToolUse hook: log MCP server invocations
# =============================================================================
# Security Level 1: hook-based audit trail for MCP tool calls.
# Appends to /workspace/.mcp-audit.log (JSONL format).
# =============================================================================

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)

if [[ "$TOOL" == mcp__* ]]; then
  SERVER=$(echo "$TOOL" | cut -d'_' -f3)
  TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  echo "{\"ts\":\"$TIMESTAMP\",\"server\":\"$SERVER\",\"tool\":\"$TOOL\"}" >> /workspace/.mcp-audit.log
fi
