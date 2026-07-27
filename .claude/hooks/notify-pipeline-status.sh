#!/bin/bash
# =============================================================================
# notify-pipeline-status.sh — Stop hook: session-end pipeline summary
# =============================================================================
# On session end, reports pipeline-related activity from the session.
# =============================================================================

LOG="/tmp/claude-pipeline.log"

if [ -f "$LOG" ]; then
  COUNT=$(wc -l < "$LOG" | tr -d ' ')
  echo "Pipeline activity this session: $COUNT commands logged"
  rm -f "$LOG"
fi
