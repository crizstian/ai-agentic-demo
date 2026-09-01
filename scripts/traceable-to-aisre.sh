#!/bin/bash
# traceable-to-aisre.sh
# Simulates Traceable WAAP sending a webhook to Harness AI SRE
# Usage: ./scripts/traceable-to-aisre.sh [optional-dedup-suffix]
#
# Demo flow:
#   Act 5: Run real attacks → show Traceable detecting them in dashboard
#   Act 6: Run this script → AI SRE creates incident → runbook → Slack

WEBHOOK_URL="https://app.harness.io/gateway/ir/tp/account/EeRjnXTnS4GrLG5VNNJZUw/api/v1/mc/webhook/5ce8a8bb-686e-4fce-9015-18af740d22f1/n7hqsfr8f47l3g1q748cqv2951"

DEDUP_SUFFIX="${1:-$(date +%s)}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "Sending Traceable attack alert to Harness AI SRE..."

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Attack Chain Detected: DemoBank API\",
    \"description\": \"Traceable WAAP detected coordinated 3-stage API attack chain against DemoBank production: Stage 1 — Zombie API recon via /api/ai/status exposed AI model config and internal MCP service URL. Stage 2 — Prompt Injection on /api/ai/chat bypassed AI guardrails, leaked 5 customer accounts via East-West MCP call. Stage 3 — BOLA enumeration on /api/accounts/{id}/details exfiltrated PII and financial data without authorization. WAF detected 0/4 steps. WAAP detected 4/4 steps. Protection Policies in Monitor mode.\",
    \"priority\": \"P1\",
    \"service\": \"demobank\",
    \"source\": \"traceable-waap\",
    \"attack_type\": \"multi-step-chain\",
    \"environment\": \"production\",
    \"dedup_id\": \"traceable-attack-${DEDUP_SUFFIX}\",
    \"link\": \"https://app.us9.traceable.ai/threat-activity\",
    \"detection_time\": \"${TIMESTAMP}\"
  }")

if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "201" ]; then
  echo "Alert sent successfully (HTTP $HTTP_STATUS)"
  echo ""
  echo "Verify in Harness AI SRE:"
  echo "  1. Alerts  → new alert with P1: Critical"
  echo "  2. Incidents → auto-created Security Incident"
  echo "  3. Slack   → #security-incidents notification"
else
  echo "ERROR: HTTP $HTTP_STATUS"
fi
