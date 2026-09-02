#!/bin/bash
set -euo pipefail

# ---------------------------------------------------------------------------
# DemoBank Demo Reset — Reset app code to STATE 0 (clean, pre-Act-1)
#
# Official branches:
#   secops/ai-agentic-demo       — working branch (fully remediated, Acts 1-7 done)
#   secops/ai-agentic-demo-main  — intermediate state (AI features + AI vulns only)
#   main                         — upstream clean state (basic vulns, no AI)
#
# This script restores app source files from 'main' to STATE 0:
#   - No AI assistant (no ai_assistant.py, no chat widget)
#   - No PII in seed data (no email, no phone)
#   - SQL injection PRESENT (string concat — VULN-001)
#   - Command injection PRESENT (shell=True — VULN-002)
#   - Reflected XSS PRESENT (unescaped param — VULN-006)
#   - CORS wildcard PRESENT (origins="*" — VULN-007)
#   - DB schema uses TEXT ids (original)
#   - requests library NOT in requirements.txt
#   - Only 2 unit tests (test_health + test_dashboard smoke)
#     → Code review agent detects lack of coverage
#     → Worker agent generates missing tests
#
# Files UNTOUCHED (preserved from secops/ai-agentic-demo):
#   docs/         — prompt cards, architecture diagrams
#   deploy/       — k8s manifests, traceable configs
#   .harness/     — pipelines, services, environments, OPA policies
#   scripts/      — attack-chain, traceable-demo-setup (this script is also preserved)
#   services/     — mcp-financial-data
#   policies/     — OPA rego files
#   .claude/      — agents, commands, CLAUDE.md
#
# Demo lifecycle after reset:
#   STATE 0 (this script)
#     → Act 1: coding agent introduces AI feature + vulns (VULN-008/009/010)
#     → Act 2: pipeline governs (build, test, SLSA)
#     → Act 3: security agent finds + remediates ALL vulns
#     → Act 4: deploy (canary + CV)
#     → Act 5: attacker exploits (Traceable detects in Monitor)
#     → Act 6: AI SRE responds
#     → Act 7: Block mode + AI Security
#
# Usage:
#   ./scripts/demo-reset.sh              # Reset app code only (dry view)
#   ./scripts/demo-reset.sh --db         # Also reset database
#   ./scripts/demo-reset.sh --commit     # Reset + auto-commit
#   ./scripts/demo-reset.sh --db --commit # Full reset + commit
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DB_PATH="${DB_PATH:-$PROJECT_DIR/demobank.db}"

# Source branch for clean app files
SOURCE_BRANCH="main"

RESET_DB=false
DO_COMMIT=false

for arg in "$@"; do
    case "$arg" in
        --db)     RESET_DB=true ;;
        --commit) DO_COMMIT=true ;;
        --help|-h)
            echo "Usage: $0 [--db] [--commit]"
            echo "  --db      Also reset the database (delete + re-seed)"
            echo "  --commit  Commit the reset as a new commit"
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

print_ok()   { echo -e "  ${GREEN}[OK]${NC}  $1"; }
print_fail() { echo -e "  ${RED}[!!]${NC}  $1"; }
print_warn() { echo -e "  ${YELLOW}[..]${NC}  $1"; }
print_info() { echo -e "  ${CYAN}[--]${NC}  $1"; }

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   DemoBank Demo Reset — STATE 0          ║${NC}"
echo -e "${CYAN}║   $(date '+%Y-%m-%d %H:%M:%S')                      ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
echo ""

# =========================================================================
# 1. Pre-flight checks
# =========================================================================
echo -e "${CYAN}--- Pre-flight checks ---${NC}"

if ! git -C "$PROJECT_DIR" rev-parse --verify "$SOURCE_BRANCH" >/dev/null 2>&1; then
    print_fail "Branch '$SOURCE_BRANCH' not found — cannot restore clean app files"
    exit 1
fi
print_ok "Source branch: $SOURCE_BRANCH (clean app baseline)"

CURRENT_BRANCH=$(git -C "$PROJECT_DIR" rev-parse --abbrev-ref HEAD)
print_info "Current branch: $CURRENT_BRANCH"

if [[ "$CURRENT_BRANCH" == "$SOURCE_BRANCH" ]]; then
    print_fail "Already on $SOURCE_BRANCH — switch to secops/ai-agentic-demo first"
    exit 1
fi

# Warn about uncommitted changes in app files
DIRTY=$(git -C "$PROJECT_DIR" diff --name-only -- app/ requirements.txt scripts/seed.py tests/ 2>/dev/null | wc -l | tr -d ' ')
if [[ "$DIRTY" -gt 0 ]]; then
    print_warn "$DIRTY uncommitted change(s) in app/test files — will be overwritten"
fi
echo ""

# =========================================================================
# 2. Restore app files from main (STATE 0)
# =========================================================================
echo -e "${CYAN}--- Restoring app code from $SOURCE_BRANCH ---${NC}"

RESTORE_FILES=(
    "app/app.py"
    "app/db.py"
    "app/routes/accounts.py"
    "app/routes/admin.py"
    "app/server.py"
    "app/static/app.js"
    "app/static/styles.css"
    "app/templates/dashboard.html"
    "requirements.txt"
    "scripts/seed.py"
)

RESTORE_OK=0
RESTORE_FAIL=0

for f in "${RESTORE_FILES[@]}"; do
    if git -C "$PROJECT_DIR" show "${SOURCE_BRANCH}:${f}" > "${PROJECT_DIR}/${f}" 2>/dev/null; then
        print_ok "Restored  $f"
        ((RESTORE_OK++)) || true
    else
        print_fail "Failed    $f"
        ((RESTORE_FAIL++)) || true
    fi
done

# Files to REMOVE (added after main, don't exist in STATE 0)
REMOVE_FILES=(
    "app/routes/ai_assistant.py"
)

for f in "${REMOVE_FILES[@]}"; do
    if [[ -f "${PROJECT_DIR}/${f}" ]]; then
        rm "${PROJECT_DIR}/${f}"
        print_ok "Removed   $f"
    else
        print_info "Already absent: $f"
    fi
done

# Clean pycache
find "${PROJECT_DIR}/app" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
print_ok "Cleaned __pycache__"
echo ""

# =========================================================================
# 3. Reset tests to minimal coverage (2 tests only)
# =========================================================================
echo -e "${CYAN}--- Resetting tests to minimal coverage ---${NC}"

# Restore conftest.py from main (same fixture, works for STATE 0)
git -C "$PROJECT_DIR" show "${SOURCE_BRANCH}:tests/conftest.py" > "${PROJECT_DIR}/tests/conftest.py" 2>/dev/null
print_ok "Restored  tests/conftest.py"

# Write minimal test_health.py (1 test — from main)
git -C "$PROJECT_DIR" show "${SOURCE_BRANCH}:tests/test_health.py" > "${PROJECT_DIR}/tests/test_health.py" 2>/dev/null
print_ok "Restored  tests/test_health.py (1 test)"

# Write minimal test_dashboard.py (1 test — smoke only)
cat > "${PROJECT_DIR}/tests/test_dashboard.py" << 'TESTEOF'
def test_dashboard_returns_200(client):
    res = client.get("/")
    assert res.status_code == 200
TESTEOF
print_ok "Wrote     tests/test_dashboard.py (1 test)"

# Remove all other test files (code review agent will flag the gap)
REMOVED_TESTS=0
for f in "${PROJECT_DIR}"/tests/test_*.py; do
    fname=$(basename "$f")
    if [[ "$fname" != "test_health.py" && "$fname" != "test_dashboard.py" ]]; then
        rm "$f"
        print_ok "Removed   tests/$fname"
        ((REMOVED_TESTS++)) || true
    fi
done

# Remove JS test file if present
if [[ -f "${PROJECT_DIR}/tests/dashboard-layout.test.js" ]]; then
    rm "${PROJECT_DIR}/tests/dashboard-layout.test.js"
    print_ok "Removed   tests/dashboard-layout.test.js"
    ((REMOVED_TESTS++)) || true
fi

print_info "Removed $REMOVED_TESTS test files — only 2 tests remain"
echo ""

# =========================================================================
# 4. Verify STATE 0 invariants
# =========================================================================
echo -e "${CYAN}--- Verifying STATE 0 invariants ---${NC}"

CHECKS_PASS=true

check() {
    local label="$1"
    local result="$2"
    if [[ "$result" == "pass" ]]; then
        print_ok "$label"
    else
        print_fail "$label"
        CHECKS_PASS=false
    fi
}

# AI assistant must be gone
[[ ! -f "${PROJECT_DIR}/app/routes/ai_assistant.py" ]] && R="pass" || R="fail"
check "No ai_assistant.py" "$R"

# Chat widget must be gone
grep -q "chat-toggle" "${PROJECT_DIR}/app/templates/dashboard.html" 2>/dev/null && R="fail" || R="pass"
check "No chat widget in dashboard.html" "$R"

grep -q "chat-panel" "${PROJECT_DIR}/app/static/app.js" 2>/dev/null && R="fail" || R="pass"
check "No chat JS in app.js" "$R"

# No AI blueprint
grep -q "ai_assistant" "${PROJECT_DIR}/app/app.py" 2>/dev/null && R="fail" || R="pass"
check "No ai_assistant import in app.py" "$R"

# Vulnerabilities PRESENT (intentional)
grep -q "SELECT \* FROM accounts WHERE id = '" "${PROJECT_DIR}/app/routes/accounts.py" 2>/dev/null && R="pass" || R="fail"
check "VULN-001 present: SQL injection (string concat)" "$R"

grep -q "shell=True" "${PROJECT_DIR}/app/routes/admin.py" 2>/dev/null && R="pass" || R="fail"
check "VULN-002 present: Command injection (shell=True)" "$R"

grep -q 'request.args.get("name", "")' "${PROJECT_DIR}/app/app.py" 2>/dev/null && R="pass" || R="fail"
check "VULN-006 present: Reflected XSS (unescaped)" "$R"

grep -q 'origins="\*"' "${PROJECT_DIR}/app/app.py" 2>/dev/null && R="pass" || R="fail"
check "VULN-007 present: CORS wildcard" "$R"

# No PII in seed data
grep -q "email" "${PROJECT_DIR}/scripts/seed.py" 2>/dev/null && R="fail" || R="pass"
check "No PII (email) in seed.py" "$R"

grep -q "phone" "${PROJECT_DIR}/scripts/seed.py" 2>/dev/null && R="fail" || R="pass"
check "No PII (phone) in seed.py" "$R"

# TEXT ids in DB (original schema)
grep -q "id TEXT PRIMARY KEY" "${PROJECT_DIR}/app/db.py" 2>/dev/null && R="pass" || R="fail"
check "DB schema uses TEXT ids (original)" "$R"

# No requests library
grep -q "requests" "${PROJECT_DIR}/requirements.txt" 2>/dev/null && R="fail" || R="pass"
check "No requests library in requirements.txt" "$R"

# Only 2 test files remain
TEST_COUNT=$(find "${PROJECT_DIR}/tests" -name "test_*.py" | wc -l | tr -d ' ')
[[ "$TEST_COUNT" -eq 2 ]] && R="pass" || R="fail"
check "Only 2 test files (test_health.py + test_dashboard.py)" "$R"

# Count actual test functions
FUNC_COUNT=$(grep -r "^def test_" "${PROJECT_DIR}/tests/" 2>/dev/null | wc -l | tr -d ' ')
[[ "$FUNC_COUNT" -eq 2 ]] && R="pass" || R="fail"
check "Only 2 test functions total" "$R"

# No AI test file
[[ ! -f "${PROJECT_DIR}/tests/test_ai_assistant.py" ]] && R="pass" || R="fail"
check "No test_ai_assistant.py" "$R"

# No accounts test file
[[ ! -f "${PROJECT_DIR}/tests/test_accounts.py" ]] && R="pass" || R="fail"
check "No test_accounts.py (code review agent will flag)" "$R"

echo ""

# =========================================================================
# 5. Database reset (optional)
# =========================================================================
if [[ "$RESET_DB" == true ]]; then
    echo -e "${CYAN}--- Resetting database ---${NC}"

    if [[ -f "$DB_PATH" ]]; then
        rm "$DB_PATH"
        print_ok "Removed $DB_PATH"
    else
        print_info "No existing database"
    fi

    cd "$PROJECT_DIR"
    python3 -c "
from app.db import init_db
from scripts.seed import seed
init_db()
seed()
" 2>&1

    if [[ -f "$DB_PATH" ]]; then
        COUNT=$(python3 -c "
import sqlite3
db = sqlite3.connect('$DB_PATH')
print(db.execute('SELECT COUNT(*) FROM accounts').fetchone()[0])
db.close()
")
        print_ok "Database seeded with $COUNT accounts (TEXT ids, no PII)"
    else
        print_fail "Database not created"
        CHECKS_PASS=false
    fi
    echo ""
fi

# =========================================================================
# 6. Commit (optional)
# =========================================================================
if [[ "$DO_COMMIT" == true ]]; then
    echo -e "${CYAN}--- Committing reset ---${NC}"

    cd "$PROJECT_DIR"

    # Stage restored files
    git add "${RESTORE_FILES[@]}"

    # Stage test files (restored + new minimal)
    git add tests/conftest.py tests/test_health.py tests/test_dashboard.py

    # Stage deletion of removed files
    for f in app/routes/ai_assistant.py \
             tests/test_accounts.py tests/test_admin.py tests/test_ai_assistant.py \
             tests/test_app_factory.py tests/test_config.py tests/test_db.py \
             tests/test_fx.py tests/test_k8s_manifest.py tests/test_seed.py \
             tests/test_statements.py tests/test_transfers.py \
             tests/dashboard-layout.test.js; do
        if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
            git rm --cached "$f" 2>/dev/null || true
        fi
    done

    git commit -m "$(cat <<'EOF'
chore: reset app code + tests to STATE 0 for end-to-end demo

Restore application source files to pre-Act-1 baseline from main.
All intentional vulnerabilities are PRESENT for the demo flow:
  VULN-001: SQL injection (string concatenation)
  VULN-002: Command injection (shell=True)
  VULN-006: Reflected XSS (unescaped user input)
  VULN-007: Insecure CORS (wildcard origin)

Tests reduced to 2 (test_health + test_dashboard smoke).
Code review agent will detect lack of coverage and trigger
worker agent to generate missing unit tests.

Removed: ai_assistant.py, chat widget, PII seed data, 11 test files.
Preserved: docs, deploy, .harness, scripts, policies.
EOF
    )"

    print_ok "Committed reset to STATE 0"
    echo ""
fi

# =========================================================================
# 7. Summary
# =========================================================================
echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║              Summary                     ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
echo ""

if [[ "$CHECKS_PASS" == true ]]; then
    echo -e "  ${GREEN}✓ App code reset to STATE 0 — ready for demo${NC}"
else
    echo -e "  ${RED}✗ Some checks failed — review output above${NC}"
fi

echo ""
echo -e "  ${CYAN}Restored:${NC} ${RESTORE_OK} files from $SOURCE_BRANCH"
if [[ "$RESTORE_FAIL" -gt 0 ]]; then
    echo -e "  ${RED}Failed:${NC}   ${RESTORE_FAIL} files"
fi

echo ""
echo -e "  ${CYAN}App state:${NC}"
echo -e "    AI assistant:  ${RED}absent${NC} (Act 1 will add it)"
echo -e "    Chat widget:   ${RED}absent${NC} (Act 1 will add it)"
echo -e "    SQLi (001):    ${YELLOW}VULNERABLE${NC} (Act 3 will fix)"
echo -e "    CMDi (002):    ${YELLOW}VULNERABLE${NC} (Act 3 will fix)"
echo -e "    XSS  (006):    ${YELLOW}VULNERABLE${NC} (Act 3 will fix)"
echo -e "    CORS (007):    ${YELLOW}VULNERABLE${NC} (Act 3 will fix)"
echo -e "    Unit tests:    ${YELLOW}2 only${NC} (code review agent will flag, worker agent generates)"

echo ""
echo -e "  ${CYAN}Preserved:${NC}"
echo -e "    docs/       prompt cards, architecture diagrams"
echo -e "    deploy/     k8s manifests, traceable configs"
echo -e "    .harness/   pipelines, services, environments"
echo -e "    scripts/    attack-chain, traceable-setup, demo-reset"

echo ""
echo -e "  ${CYAN}Next steps:${NC}"
if [[ "$DO_COMMIT" == false ]]; then
    echo -e "    git diff --stat          # review changes"
    echo -e "    $0 --commit   # commit when ready"
fi
echo -e "    git push origin $CURRENT_BRANCH  # push to remote"
echo ""

echo -e "  ${CYAN}Demo lifecycle:${NC}"
echo -e "    STATE 0 ${GREEN}(current)${NC}"
echo -e "      ↓ Act 1: coding agent adds AI + vulns (008/009/010)"
echo -e "      ↓ Act 2: pipeline governs (build, test, SLSA)"
echo -e "      ↓ Act 3: security agent remediates ALL vulns"
echo -e "      ↓ Act 4: deploy (canary + CV + governance)"
echo -e "      ↓ Act 5: attacker exploits → Traceable detects (Monitor)"
echo -e "      ↓ Act 6: AI SRE responds (12s, 6 actions)"
echo -e "      ↓ Act 7: Block mode + AI Security"
echo ""
