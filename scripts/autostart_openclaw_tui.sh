#!/usr/bin/env bash
set -euo pipefail

WORKDIR="/home/manduong/.openclaw/workspace"
SESSION_KEY="${OPENCLAW_TUI_SESSION:-agent:main:telegram:direct:6542038310}"
BOOT_MESSAGE="${OPENCLAW_TUI_BOOT_MESSAGE:-}"
HISTORY_LIMIT="${OPENCLAW_TUI_HISTORY_LIMIT:-80}"

export PATH="$HOME/.linuxbrew/bin:$HOME/.nvm/current/bin:$HOME/.local/bin:$PATH"

OPENCLAW_BIN="${OPENCLAW_BIN:-$(command -v openclaw || true)}"
if [[ -z "$OPENCLAW_BIN" && -x "$HOME/.nvm/versions/node/v24.13.1/bin/openclaw" ]]; then
  OPENCLAW_BIN="$HOME/.nvm/versions/node/v24.13.1/bin/openclaw"
fi
if [[ -z "$OPENCLAW_BIN" ]]; then
  echo "[OpenClaw] ERROR: openclaw binary not found in PATH" >&2
  exit 1
fi

cd "$WORKDIR"

# Prevent duplicate TUI instances fighting for focus/input.
LOCKFILE="/tmp/openclaw-tui-autostart.lock"
exec 9>"$LOCKFILE"
if ! flock -n 9; then
  echo "[OpenClaw] TUI is already running (lock: $LOCKFILE). Skip duplicate launch."
  exit 0
fi

# Start gateway + optional local reminder service.
systemctl --user start openclaw-gateway.service || "$OPENCLAW_BIN" gateway start || true
systemctl --user start zalo-reminder-manager.service >/dev/null 2>&1 || true

# Wait for gateway RPC to become responsive; restart once if still unhealthy.
healthy=0
for _ in $(seq 1 25); do
  if "$OPENCLAW_BIN" health >/dev/null 2>&1; then
    healthy=1
    break
  fi
  sleep 1
done

if [[ "$healthy" -ne 1 ]]; then
  echo "[OpenClaw] Gateway health check timeout, restarting service once..."
  systemctl --user restart openclaw-gateway.service || true
  for _ in $(seq 1 20); do
    if "$OPENCLAW_BIN" health >/dev/null 2>&1; then
      healthy=1
      break
    fi
    sleep 1
  done
fi

echo "[OpenClaw] Launching TUI (session=$SESSION_KEY, deliver=on, history-limit=$HISTORY_LIMIT)"

if [[ -n "$BOOT_MESSAGE" ]]; then
  exec "$OPENCLAW_BIN" tui --deliver --session "$SESSION_KEY" --history-limit "$HISTORY_LIMIT" --message "$BOOT_MESSAGE"
else
  exec "$OPENCLAW_BIN" tui --deliver --session "$SESSION_KEY" --history-limit "$HISTORY_LIMIT"
fi
