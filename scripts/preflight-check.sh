#!/bin/bash
set -uo pipefail

# ---------------------------------------------------------------------------
# DemoBank Pre-flight Check — Validate demo readiness before going live
#
# Checks: app health, Split API, MCP service, feature flags, GitHub auth,
#          Harness pipeline status, STATE 0 invariants (optional).
#
# Usage:
#   ./scripts/preflight-check.sh                # Quick connectivity + flags
#   ./scripts/preflight-check.sh --full         # + STATE 0 invariant checks
#   ./scripts/preflight-check.sh --act1         # Expect flags ON (post Act 1)
#   ./scripts/preflight-check.sh --json         # Machine-readable output
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

FULL_CHECK=false
EXPECT_FLAGS_ON=false
JSON_OUTPUT=false

for arg in "$@"; do
    case "$arg" in
        --full)  FULL_CHECK=true ;;
        --act1)  EXPECT_FLAGS_ON=true ;;
        --json)  JSON_OUTPUT=true ;;
        --help|-h)
            echo "Usage: $0 [--full] [--act1] [--json]"
            echo "  --full   Include STATE 0 invariant checks"
            echo "  --act1   Expect feature flags ON (post Act 1)"
            echo "  --json   Machine-readable JSON output"
            exit 0
            ;;
        *) echo "Unknown option: $arg"; exit 1 ;;
    esac
done

# -- Colors ----------------------------------------------------------------
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0
RESULTS=()

check_pass() {
    ((PASS_COUNT++)) || true
    RESULTS+=("{\"name\":\"$1\",\"status\":\"PASS\",\"detail\":\"$2\"}")
    if [[ "$JSON_OUTPUT" == false ]]; then
        echo -e "  ${GREEN}[PASS]${NC} $1: $2"
    fi
}

check_fail() {
    ((FAIL_COUNT++)) || true
    RESULTS+=("{\"name\":\"$1\",\"status\":\"FAIL\",\"detail\":\"$2\"}")
    if [[ "$JSON_OUTPUT" == false ]]; then
        echo -e "  ${RED}[FAIL]${NC} $1: $2"
    fi
}

check_warn() {
    ((WARN_COUNT++)) || true
    RESULTS+=("{\"name\":\"$1\",\"status\":\"WARN\",\"detail\":\"$2\"}")
    if [[ "$JSON_OUTPUT" == false ]]; then
        echo -e "  ${YELLOW}[WARN]${NC} $1: $2"
    fi
}

APP_URL="${DEMOBANK_URL:-http://demobank-e2e.selatam.harness-demo.site}"
SPLIT_SDK_KEY="${SPLIT_SDK_KEY:-v4kvjbb2cuupu0ihed20iceumvv1m9po07bn}"
MCP_URL="${MCP_SERVER_URL:-http://mcp-financial-data:5001}"

if [[ "$JSON_OUTPUT" == false ]]; then
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   DemoBank Pre-flight Check              ║${NC}"
    echo -e "${CYAN}║   $(date '+%Y-%m-%d %H:%M:%S')                      ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
    echo ""
fi

# =========================================================================
# 1. Connectivity checks
# =========================================================================
if [[ "$JSON_OUTPUT" == false ]]; then
    echo -e "${CYAN}--- Connectivity ---${NC}"
fi

# App health
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 --max-time 10 "${APP_URL}/health" 2>/dev/null || echo "000")
if [[ "$HTTP_CODE" == "200" ]]; then
    check_pass "App health" "$HTTP_CODE"
elif [[ "$HTTP_CODE" == "000" ]]; then
    check_fail "App health" "unreachable (timeout)"
else
    check_fail "App health" "HTTP $HTTP_CODE"
fi

# Split API
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 --max-time 10 \
    "https://sdk.split.io/api/splitChanges?since=-1" \
    -H "Authorization: Bearer ${SPLIT_SDK_KEY}" 2>/dev/null || echo "000")
if [[ "$HTTP_CODE" == "200" ]]; then
    check_pass "Split API" "$HTTP_CODE"
elif [[ "$HTTP_CODE" == "000" ]]; then
    check_fail "Split API" "unreachable (timeout)"
else
    check_fail "Split API" "HTTP $HTTP_CODE (check SDK key)"
fi

# MCP Financial Data
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 --max-time 10 \
    "${MCP_URL}/health" 2>/dev/null || echo "000")
if [[ "$HTTP_CODE" == "200" ]]; then
    check_pass "MCP Financial Data" "$HTTP_CODE"
elif [[ "$HTTP_CODE" == "000" ]] || [[ "$HTTP_CODE" == "000000" ]]; then
    check_warn "MCP Financial Data" "unreachable (in-cluster only)"
else
    check_fail "MCP Financial Data" "HTTP $HTTP_CODE"
fi

if [[ "$JSON_OUTPUT" == false ]]; then echo ""; fi

# =========================================================================
# 2. Feature flags
# =========================================================================
if [[ "$JSON_OUTPUT" == false ]]; then
    echo -e "${CYAN}--- Feature Flags ---${NC}"
fi

SPLIT_RESPONSE=$(curl -s --connect-timeout 5 --max-time 10 \
    "https://sdk.split.io/api/splitChanges?since=-1" \
    -H "Authorization: Bearer ${SPLIT_SDK_KEY}" 2>/dev/null || echo "{}")

check_flag() {
    local flag_name="$1"
    local default_treatment
    local active_100

    default_treatment=$(echo "$SPLIT_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for s in data.get('splits', []):
        if s.get('name') == '$flag_name':
            print(s.get('defaultTreatment', 'unknown'))
            break
    else:
        print('not_found')
except: print('error')
" 2>/dev/null || echo "error")

    active_100=$(echo "$SPLIT_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for s in data.get('splits', []):
        if s.get('name') == '$flag_name':
            for c in s.get('conditions', []):
                for p in c.get('partitions', []):
                    if p.get('treatment') == 'on' and p.get('size', 0) == 100:
                        print('on')
                        break
            break
    print('off')
except: print('error')
" 2>/dev/null | head -1 || echo "error")

    local effective="off"
    if [[ "$active_100" == "on" ]] || [[ "$default_treatment" == "on" ]]; then
        effective="on"
    fi

    if [[ "$EXPECT_FLAGS_ON" == true ]]; then
        if [[ "$effective" == "on" ]]; then
            check_pass "$flag_name" "ON (correct for post-Act 1)"
        else
            check_fail "$flag_name" "OFF (expected ON for --act1)"
        fi
    else
        if [[ "$effective" == "off" ]] || [[ "$default_treatment" == "off" ]]; then
            check_pass "$flag_name" "OFF (correct for Act 0)"
        elif [[ "$effective" == "on" ]]; then
            check_fail "$flag_name" "ON (expected OFF for Act 0)"
        else
            check_warn "$flag_name" "could not determine ($default_treatment)"
        fi
    fi
}

check_flag "ai_chat_enabled"
check_flag "ai_chat_backend"

if [[ "$JSON_OUTPUT" == false ]]; then echo ""; fi

# =========================================================================
# 3. Auth & secrets
# =========================================================================
if [[ "$JSON_OUTPUT" == false ]]; then
    echo -e "${CYAN}--- Auth & Secrets ---${NC}"
fi

# GitHub auth
if gh auth status >/dev/null 2>&1; then
    GH_USER=$(gh api user --jq '.login' 2>/dev/null || echo "unknown")
    check_pass "GitHub auth" "authenticated as $GH_USER"
else
    check_fail "GitHub auth" "not authenticated (run gh auth login)"
fi

# Harness API key
if [[ -n "${HARNESS_API_KEY:-}" ]]; then
    check_pass "HARNESS_API_KEY" "set (${#HARNESS_API_KEY} chars)"
else
    check_warn "HARNESS_API_KEY" "not set (flag reset will skip)"
fi

# OPENAI_API_KEY
if [[ -n "${OPENAI_API_KEY:-}" ]]; then
    check_pass "OPENAI_API_KEY" "set"
else
    check_warn "OPENAI_API_KEY" "not set (AI chat will use fallback/fail)"
fi

if [[ "$JSON_OUTPUT" == false ]]; then echo ""; fi

# =========================================================================
# 4. Pipeline status
# =========================================================================
if [[ "$JSON_OUTPUT" == false ]]; then
    echo -e "${CYAN}--- Pipeline ---${NC}"
fi

PIPELINE_STATUS=$(curl -s --connect-timeout 5 --max-time 10 \
    "https://app.harness.io/gateway/pipeline/api/pipelines/summary/AI_SDLC_DemoBank?accountIdentifier=EeRjnXTnS4GrLG5VNNJZUw&orgIdentifier=sandbox&projectIdentifier=CristianRamirez" \
    -H "x-api-key: ${HARNESS_API_KEY:-none}" 2>/dev/null || echo "{}")

if echo "$PIPELINE_STATUS" | grep -q '"name"'; then
    LAST_STATUS=$(echo "$PIPELINE_STATUS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    ei = data.get('data', {}).get('executionSummaryInfo', {})
    deploys = ei.get('lastExecutionStatus', 'unknown')
    print(deploys)
except: print('unknown')
" 2>/dev/null || echo "unknown")
    if [[ "$LAST_STATUS" == "Success" ]] || [[ "$LAST_STATUS" == "unknown" ]]; then
        check_pass "Pipeline AI_SDLC_DemoBank" "exists (last: $LAST_STATUS)"
    elif [[ "$LAST_STATUS" == "Running" ]]; then
        check_warn "Pipeline AI_SDLC_DemoBank" "currently running"
    else
        check_warn "Pipeline AI_SDLC_DemoBank" "last run: $LAST_STATUS"
    fi
else
    check_warn "Pipeline AI_SDLC_DemoBank" "could not check (no API key or network)"
fi

if [[ "$JSON_OUTPUT" == false ]]; then echo ""; fi

# =========================================================================
# 5. STATE 0 invariants (--full only)
# =========================================================================
if [[ "$FULL_CHECK" == true ]]; then
    if [[ "$JSON_OUTPUT" == false ]]; then
        echo -e "${CYAN}--- STATE 0 Invariants ---${NC}"
    fi

    # AI assistant absent
    if [[ ! -f "${PROJECT_DIR}/app/routes/ai_assistant.py" ]]; then
        check_pass "No ai_assistant.py" "absent"
    else
        check_fail "No ai_assistant.py" "file exists (not STATE 0)"
    fi

    # Chat widget absent
    if ! grep -q "chat-toggle" "${PROJECT_DIR}/app/templates/dashboard.html" 2>/dev/null; then
        check_pass "No chat widget" "absent from dashboard.html"
    else
        check_fail "No chat widget" "found in dashboard.html"
    fi

    # Vulnerabilities present
    if grep -q "SELECT \* FROM accounts WHERE id = '" "${PROJECT_DIR}/app/routes/accounts.py" 2>/dev/null; then
        check_pass "VULN-001 SQLi" "present (intentional)"
    else
        check_fail "VULN-001 SQLi" "missing (should be present in STATE 0)"
    fi

    if grep -q "shell=True" "${PROJECT_DIR}/app/routes/admin.py" 2>/dev/null; then
        check_pass "VULN-002 CMDi" "present (intentional)"
    else
        check_fail "VULN-002 CMDi" "missing (should be present in STATE 0)"
    fi

    # CSS bugs present
    if grep -q "rotate(3deg)" "${PROJECT_DIR}/app/static/styles.css" 2>/dev/null; then
        check_pass "CSS bug: rotated cards" "present (intentional)"
    else
        check_fail "CSS bug: rotated cards" "missing"
    fi

    # Test count
    TEST_COUNT=$(find "${PROJECT_DIR}/tests" -maxdepth 1 -name "test_*.py" 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$TEST_COUNT" -eq 2 ]]; then
        check_pass "Test files" "2 (correct for STATE 0)"
    else
        check_fail "Test files" "$TEST_COUNT (expected 2)"
    fi

    # No requests in requirements.txt
    if ! grep -q "requests" "${PROJECT_DIR}/requirements.txt" 2>/dev/null; then
        check_pass "No requests lib" "absent from requirements.txt"
    else
        check_fail "No requests lib" "found in requirements.txt"
    fi

    if [[ "$JSON_OUTPUT" == false ]]; then echo ""; fi
fi

# =========================================================================
# 6. Summary
# =========================================================================
TOTAL=$((PASS_COUNT + FAIL_COUNT + WARN_COUNT))

if [[ "$JSON_OUTPUT" == true ]]; then
    echo "{"
    echo "  \"timestamp\": \"$(date -u '+%Y-%m-%dT%H:%M:%SZ')\","
    echo "  \"mode\": \"$(if [[ "$EXPECT_FLAGS_ON" == true ]]; then echo 'act1'; else echo 'act0'; fi)\","
    echo "  \"full_check\": $FULL_CHECK,"
    echo "  \"passed\": $PASS_COUNT,"
    echo "  \"failed\": $FAIL_COUNT,"
    echo "  \"warnings\": $WARN_COUNT,"
    echo "  \"result\": \"$(if [[ "$FAIL_COUNT" -eq 0 ]]; then echo 'READY'; else echo 'NOT_READY'; fi)\","
    echo "  \"checks\": [$(IFS=,; echo "${RESULTS[*]}")]"
    echo "}"
else
    echo -e "${CYAN}═══════════════════════════════════════════${NC}"
    if [[ "$FAIL_COUNT" -eq 0 ]]; then
        echo -e "  ${GREEN}Result: READY${NC} ($PASS_COUNT/$TOTAL passed, $WARN_COUNT warnings)"
    else
        echo -e "  ${RED}Result: NOT READY${NC} ($PASS_COUNT/$TOTAL passed, $FAIL_COUNT failed, $WARN_COUNT warnings)"
    fi
    echo -e "${CYAN}═══════════════════════════════════════════${NC}"
    echo ""
fi

exit "$FAIL_COUNT"
