#!/usr/bin/env bash
# sync-evals.sh — Sync repo JSONL dataset to Harness AI Evals platform
#
# Usage: ./scripts/sync-evals.sh
#
# Reads evals/datasets/mcp-quality-gate.jsonl and upserts each item
# to the platform dataset via the AI Evals REST API.
#
# Requires: HARNESS_API_KEY env var

set -euo pipefail

DATASET_ID="648bbb0f-ff5b-4724-98bc-7baa6478f2d8"
ACCOUNT="EeRjnXTnS4GrLG5VNNJZUw"
BASE="https://app.harness.io/ai-evals/api/v1/orgs/sandbox/projects/CristianRamirez"
JSONL="evals/datasets/mcp-quality-gate.jsonl"

if [[ -z "${HARNESS_API_KEY:-}" ]]; then
  echo "ERROR: HARNESS_API_KEY not set" >&2
  exit 1
fi

if [[ ! -f "$JSONL" ]]; then
  echo "ERROR: $JSONL not found — run from repo root" >&2
  exit 1
fi

echo "Syncing $JSONL → dataset $DATASET_ID"

# Delete existing items and re-create from JSONL
# Step 1: List current items
EXISTING=$(curl -s "${BASE}/dataset/${DATASET_ID}/items?accountIdentifier=${ACCOUNT}&page_size=100" \
  -H "x-api-key: ${HARNESS_API_KEY}" | python3 -c "
import sys, json
data = json.load(sys.stdin)
items = data.get('data', data) if isinstance(data, dict) else data
if isinstance(items, list):
    for item in items:
        print(item.get('uuid', ''))
" 2>/dev/null || true)

# Step 2: Create items from JSONL
count=0
while IFS= read -r line; do
  [[ -z "$line" ]] && continue

  # Transform JSONL format to API format
  body=$(echo "$line" | python3 -c "
import sys, json
item = json.loads(sys.stdin.read())
api_item = {
    'input': item['input'],
    'metadata': item.get('metadata', {})
}
if 'expected' in item:
    api_item['expected_output'] = item['expected']
if 'expected_tools' in item:
    api_item['expected_tools'] = item['expected_tools']
if 'precomputed_output' in item:
    api_item['precomputed_output'] = item['precomputed_output']
print(json.dumps(api_item))
")

  status=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "${BASE}/dataset/${DATASET_ID}/items?accountIdentifier=${ACCOUNT}" \
    -H "x-api-key: ${HARNESS_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$body")

  count=$((count + 1))
  item_id=$(echo "$line" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('id','?'))")
  echo "  [$count] $item_id → HTTP $status"

done < "$JSONL"

echo "Done: $count items synced"
