#!/bin/sh
set -e

echo "[post-start] configuring Docker socket permissions..."
if [ -S /var/run/docker.sock ]; then
  DOCKER_GID=$(stat -c '%g' /var/run/docker.sock)
  if ! getent group docker >/dev/null 2>&1; then
    sudo addgroup -g "$DOCKER_GID" docker 2>/dev/null || true
  fi
  sudo addgroup devuser docker 2>/dev/null || true
  sudo chmod 666 /var/run/docker.sock 2>/dev/null || true
fi

echo "[post-start] validating devtoolchain..."

for cmd in claude gh; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "WARN: $cmd not found in PATH"
  fi
done

# Harness MCP
[ -n "$HARNESS_API_KEY" ] || echo "WARN: HARNESS_API_KEY is empty"
[ -n "$HARNESS_ORG" ] || echo "WARN: HARNESS_ORG is empty"
[ -n "$HARNESS_PROJECT" ] || echo "WARN: HARNESS_PROJECT is empty"

echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","clientInfo":{"name":"health-check","version":"1.0.0"},"capabilities":{}}}' \
  | harness-mcp-v2 >/dev/null 2>&1 || echo "WARN: harness-mcp-v2 initialize failed"

# GitHub
[ -n "$GITHUB_PERSONAL_ACCESS_TOKEN" ] || echo "WARN: GITHUB_PERSONAL_ACCESS_TOKEN is empty"

# Perplexity
[ -n "$PERPLEXITY_API_KEY" ] || echo "WARN: PERPLEXITY_API_KEY is empty"

echo "[post-start] validating AI environment..."

# Vertex AI
if [ "$CLAUDE_CODE_USE_VERTEX" = "1" ]; then
  gcloud auth print-access-token >/dev/null 2>&1 || echo "WARN: gcloud auth not configured — Vertex AI may fail"
  [ -n "$ANTHROPIC_VERTEX_PROJECT_ID" ] || echo "WARN: ANTHROPIC_VERTEX_PROJECT_ID is empty"
  [ -n "$CLOUD_ML_REGION" ] || echo "WARN: CLOUD_ML_REGION is empty"
fi

# Prompt caching
if [ "$DISABLE_PROMPT_CACHING" = "1" ]; then
  echo "WARN: DISABLE_PROMPT_CACHING=1 — prompt caching is disabled (higher cost/latency)"
fi

# Zscaler TLS certs
if [ -n "${NODE_EXTRA_CA_CERTS}" ] && [ -f "${NODE_EXTRA_CA_CERTS}" ]; then
  CERT_COUNT=$(grep -c 'BEGIN CERTIFICATE' "${NODE_EXTRA_CA_CERTS}" 2>/dev/null || echo 0)
  echo "✓ NODE_EXTRA_CA_CERTS (${CERT_COUNT} certs)"
else
  echo "⚠ NODE_EXTRA_CA_CERTS not set — MCP servers using TLS may fail"
fi

# Obsidian vault (optional)
if [ -d /workspace/obsidian ]; then
  VAULT_FILES=$(find /workspace/obsidian -maxdepth 1 -name "*.md" 2>/dev/null | head -1)
  [ -n "$VAULT_FILES" ] || echo "INFO: /workspace/obsidian mounted but appears empty"
fi

# Chrome DevTools (optional)
CHROME_URL="${CHROME_DEVTOOLS_URL:-http://host.docker.internal:9222}"
curl -s --max-time 3 "$CHROME_URL/json/version" >/dev/null 2>&1 || \
  echo "INFO: Chrome DevTools not reachable at $CHROME_URL (optional)"

# Git config
git config --global user.name "${GIT_USER_NAME:-devuser}" 2>/dev/null || true
git config --global user.email "${GIT_USER_EMAIL:-devuser@localhost}" 2>/dev/null || true

# Install .vsix extensions from local plugins/ (copied during adopt/init)
DEVCONTAINER_DIR="$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")"
LOCAL_PLUGINS="$DEVCONTAINER_DIR/plugins"
HARNESS_VSIX="$LOCAL_PLUGINS/harness-vscode-0.1.9-beta.2.vsix"
if [ -f "$HARNESS_VSIX" ]; then
  EXT_ID="harness-inc.harness-vscode"
  if ! code --list-extensions 2>/dev/null | grep -qi "$EXT_ID"; then
    echo "[post-start] Installing Harness AI Chatbot extension..."
    code --install-extension "$HARNESS_VSIX" --force 2>&1 && \
      echo "✓ Harness AI Chatbot installed" || \
      echo "✗ Harness AI Chatbot installation failed"
  else
    echo "✓ Harness AI Chatbot already installed"
  fi
fi

# MCP config auto-generation (probe sidecars, fallback to stdio)
docker network create mcp-net 2>/dev/null || true

echo "[post-start] generating MCP configs (auto-detect sidecars)..."
if [ -f /workspace/ai-dev-platform/scripts/generate-mcp-configs.sh ]; then
  /workspace/ai-dev-platform/scripts/generate-mcp-configs.sh \
    --mode auto "${PROJECT_PROFILE:-all}" /workspace 2>&1 | sed 's/^/  /'
else
  echo "  WARN: ai-dev-platform not found, using existing MCP configs"
fi

echo "[post-start] done"
