#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <url>"
  exit 1
fi

URL="$1"

# Preferred on this host (WSL -> open on Windows desktop)
POWERSHELL="/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
if [[ -x "$POWERSHELL" ]]; then
  "$POWERSHELL" -NoProfile -Command "Start-Process '$URL'" >/dev/null 2>&1 || true
  echo "Opened on Windows host: $URL"
  exit 0
fi

# Linux desktop fallback
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$URL" >/dev/null 2>&1 || true
  echo "Opened via xdg-open: $URL"
  exit 0
fi

echo "No URL opener available on this host." >&2
exit 2
