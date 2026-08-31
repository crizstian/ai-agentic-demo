#!/bin/bash
set -euo pipefail

# ---------------------------------------------------------------------------
# DemoBank Demo Reset
# Tears down running processes, re-seeds the database, runs smoke tests,
# and reports readiness. Idempotent — safe to run repeatedly.
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

DB_PATH="${DB_PATH:-$PROJECT_DIR/demobank.db}"
APP_PORT="${PORT:-3000}"
MCP_PORT=5001
BASE_URL="http://localhost:${APP_PORT}"

# Track background PIDs for cleanup
BG_PIDS=()

# -- Colors ----------------------------------------------------------------
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# -- Helpers ---------------------------------------------------------------
print_success() { echo -e "  ${GREEN}[PASS]${NC}  $1"; }
print_error()   { echo -e "  ${RED}[FAIL]${NC}  $1"; }
print_warn()    { echo -e "  ${YELLOW}[WARN]${NC}  $1"; }
print_info()    { echo -e "  ${CYAN}[INFO]${NC}  $1"; }

# -- Cleanup trap ----------------------------------------------------------
cleanup() {
    for pid in "${BG_PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            wait "$pid" 2>/dev/null || true
        fi
    done
}
trap cleanup EXIT

# -- Checklist tracking ----------------------------------------------------
CHECKS=()
record() {
    # record "label" pass|fail
    CHECKS+=("$1|$2")
}

# =========================================================================
# 1. Banner
# =========================================================================
echo ""
echo -e "${CYAN}=== DemoBank Demo Reset ===${NC}"
echo -e "${CYAN}    $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo ""

# =========================================================================
# 2. Stop running processes
# =========================================================================
echo -e "${CYAN}--- Stopping running processes ---${NC}"

kill_port() {
    local port=$1
    local label=$2
    local pids

    pids=$(lsof -ti :"$port" 2>/dev/null || true)
    if [[ -n "$pids" ]]; then
        echo "$pids" | xargs kill -9 2>/dev/null || true
        print_success "Killed $label on port $port (PID $pids)"
    else
        print_info "No process on port $port ($label)"
    fi
}

kill_port "$APP_PORT" "DemoBank"
kill_port "$MCP_PORT" "MCP Financial Data"
record "Processes stopped" "pass"
echo ""

# =========================================================================
# 3. Clean and re-seed database
# =========================================================================
echo -e "${CYAN}--- Resetting database ---${NC}"

if [[ -f "$DB_PATH" ]]; then
    rm "$DB_PATH"
    print_success "Removed $DB_PATH"
else
    print_info "No existing database at $DB_PATH"
fi

cd "$PROJECT_DIR"

python3 -c "
from app.db import init_db
from scripts.seed import seed
init_db()
seed()
" 2>&1

if [[ -f "$DB_PATH" ]]; then
    print_success "Database created and seeded"
    record "Database seeded" "pass"
else
    print_error "Database file not found after seeding"
    record "Database seeded" "fail"
fi
echo ""

# =========================================================================
# 4. Verify seed data
# =========================================================================
echo -e "${CYAN}--- Verifying seed data ---${NC}"

ACCOUNT_COUNT=$(python3 -c "
import sqlite3, sys
db = sqlite3.connect('$DB_PATH')
db.row_factory = sqlite3.Row
rows = db.execute('SELECT id, owner, balance FROM accounts ORDER BY id').fetchall()
for r in rows:
    print(f'  Account {r[\"id\"]:>3}  {r[\"owner\"]:<20}  \${r[\"balance\"]:>12,.2f}')
print(f'---')
print(len(rows))
db.close()
" 2>&1)

# Last line is the count
COUNT=$(echo "$ACCOUNT_COUNT" | tail -1)
# Print the account rows (everything except the last two lines: separator and count)
echo "$ACCOUNT_COUNT" | head -n -2

if [[ "$COUNT" -eq 5 ]]; then
    print_success "Verified $COUNT accounts in database"
    record "Seed verification" "pass"
else
    print_error "Expected 5 accounts, found $COUNT"
    record "Seed verification" "fail"
fi
echo ""

# =========================================================================
# 5. Smoke tests
# =========================================================================
echo -e "${CYAN}--- Running smoke tests ---${NC}"

# Start app in background
python3 -m app.server &
APP_PID=$!
BG_PIDS+=("$APP_PID")

print_info "Started DemoBank (PID $APP_PID), waiting for startup..."
sleep 3

SMOKE_PASS=true

smoke_test() {
    local label="$1"
    local path="$2"
    local url="${BASE_URL}${path}"
    local status

    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null || echo "000")

    if [[ "$status" == "200" ]]; then
        print_success "$label  (HTTP $status)"
    else
        print_error "$label  (HTTP $status)"
        SMOKE_PASS=false
    fi
}

smoke_test "/health"          "/health"
smoke_test "/api/accounts"    "/api/accounts"
smoke_test "/api/ai/status"   "/api/ai/status"
smoke_test "/api/fx/"         "/api/fx/"

# Kill background app
if kill -0 "$APP_PID" 2>/dev/null; then
    kill "$APP_PID" 2>/dev/null || true
    wait "$APP_PID" 2>/dev/null || true
    print_info "Stopped background DemoBank (PID $APP_PID)"
fi

if [[ "$SMOKE_PASS" == true ]]; then
    record "Smoke tests" "pass"
else
    record "Smoke tests" "fail"
fi
echo ""

# =========================================================================
# 6. Git status
# =========================================================================
echo -e "${CYAN}--- Git status ---${NC}"

BRANCH=$(git -C "$PROJECT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
print_info "Branch: $BRANCH"

CHANGES=$(git -C "$PROJECT_DIR" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
if [[ "$CHANGES" -gt 0 ]]; then
    print_warn "$CHANGES uncommitted change(s)"
else
    print_success "Working tree clean"
fi

if git -C "$PROJECT_DIR" rev-parse --verify demo/base >/dev/null 2>&1; then
    print_info "Branch demo/base exists. To reset to demo baseline run:"
    echo -e "         git checkout demo/base"
fi

record "Git status" "pass"
echo ""

# =========================================================================
# 7. Summary
# =========================================================================
echo -e "${CYAN}=== Summary ===${NC}"

ALL_PASS=true
for entry in "${CHECKS[@]}"; do
    label="${entry%%|*}"
    status="${entry##*|}"
    if [[ "$status" == "pass" ]]; then
        echo -e "  ${GREEN}[OK]${NC}  $label"
    else
        echo -e "  ${RED}[!!]${NC}  $label"
        ALL_PASS=false
    fi
done

echo ""
if [[ "$ALL_PASS" == true ]]; then
    echo -e "${GREEN}Demo environment ready!${NC}"
else
    echo -e "${RED}Issues found — review output above.${NC}"
fi
echo ""
