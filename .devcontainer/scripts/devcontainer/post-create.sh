#!/bin/sh
set -e

echo "[post-create] bootstrap inicial..."

git config --global user.name "${GIT_USER_NAME:-devuser}" || true
git config --global user.email "${GIT_USER_EMAIL:-devuser@localhost}" || true

# VS Code devcontainer creates an overlay on /usr/local that shadows image binaries.
CONTAINER_NAME="${CONTAINER_NAME:-$(hostname)}"
for bin in helm; do
  if ! command -v "$bin" > /dev/null 2>&1; then
    echo "[post-create] Recovering $bin from image layer..."
    docker exec "$CONTAINER_NAME" cat "/usr/local/bin/$bin" > "/tmp/$bin" 2>/dev/null && \
      chmod +x "/tmp/$bin" && \
      sudo mv "/tmp/$bin" "/usr/local/bin/$bin" && \
      echo "[post-create] ✓ $bin recovered" || \
      echo "[post-create] ✗ $bin recovery failed"
  fi
done

# Go SDK is a full directory tree — recover from image layer if overlay hid it
if [ ! -d /usr/local/go ] || ! command -v go > /dev/null 2>&1; then
  echo "[post-create] Recovering Go SDK from image layer..."
  docker exec "$CONTAINER_NAME" tar cf - -C /usr/local go 2>/dev/null | sudo tar xf - -C /usr/local && \
    echo "[post-create] ✓ Go SDK recovered" || \
    echo "[post-create] ✗ Go SDK recovery failed"
fi

# Install ShiftLeft CLI (sl) if token is configured
if [ -n "$SHIFTLEFT_ACCESS_TOKEN" ]; then
  if ! command -v sl > /dev/null 2>&1; then
    echo "[post-create] Installing ShiftLeft CLI..."
    curl -fsSL https://cdn.shiftleft.io/download/sl > /tmp/sl
    chmod +x /tmp/sl
    sudo mv /tmp/sl /usr/local/bin/sl
  fi
  sl auth --token "$SHIFTLEFT_ACCESS_TOKEN" --org "${SHIFTLEFT_ORG_ID:-}" || true
fi

# Zscaler Root CA — install if present but missing from trust store
PLATFORM_CERTS="/workspace/ai-dev-platform/images/certs"
if [ -f "$PLATFORM_CERTS/zscaler-root-ca.crt" ] && ! grep -q 'CN=Zscaler Root CA,' /etc/ssl/certs/ca-certificates.crt 2>/dev/null; then
  echo "[post-create] Installing Zscaler Root CA..."
  sudo cp "$PLATFORM_CERTS/zscaler-root-ca.crt" /usr/local/share/ca-certificates/zscaler-root-ca.crt && \
    sudo update-ca-certificates && \
    sudo cp /etc/ssl/certs/ca-certificates.crt /etc/ssl/cert.pem && \
    echo "[post-create] ✓ Zscaler Root CA installed" || \
    echo "[post-create] ✗ Zscaler Root CA installation failed"
fi

# NOTE: VS Code extension installs are in post-start.sh
# (code CLI is not available until VS Code server is fully up)

echo "[post-create] done"
