#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/../apps/zalo-reminder-manager" && pwd)"
PORT="${ZALO_REMINDER_PORT:-8799}"
HOST="${ZALO_REMINDER_HOST:-127.0.0.1}"

cd "$APP_DIR"
exec python3 app.py
