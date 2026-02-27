#!/usr/bin/env bash
set -euo pipefail

WORKDIR="/home/manduong/.openclaw/workspace"
OPENCLAW_BIN="/home/manduong/.nvm/versions/node/v24.13.1/bin/openclaw"
SESSION_KEY="${OPENCLAW_TUI_SESSION:-agent:main:telegram:direct:6542038310}"
BOOT_MESSAGE="${OPENCLAW_TUI_BOOT_MESSAGE:-}"

export PATH="$HOME/.nvm/current/bin:$HOME/.local/bin:$PATH"

cd "$WORKDIR"

# Start gateway + optional local reminder service.
(systemctl --user start openclaw-gateway.service || "$OPENCLAW_BIN" gateway start || true)
systemctl --user start zalo-reminder-manager.service >/dev/null 2>&1 || true

# Wait for gateway RPC to become responsive.
for _ in $(seq 1 20); do
  if "$OPENCLAW_BIN" health >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo "[OpenClaw] Launching TUI (session=$SESSION_KEY, deliver=on)"

if [[ -n "$BOOT_MESSAGE" ]]; then
  exec "$OPENCLAW_BIN" tui --deliver --session "$SESSION_KEY" --message "$BOOT_MESSAGE"
else
  exec "$OPENCLAW_BIN" tui --deliver --session "$SESSION_KEY"
fi
