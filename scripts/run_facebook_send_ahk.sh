#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <recipient_name> <message>"
  exit 1
fi

RECIPIENT="$1"
shift
MESSAGE="$*"

AHK_EXE="/mnt/c/Users/ADMIN/AppData/Local/Programs/AutoHotkey/v2/AutoHotkey64.exe"
AHK_SCRIPT="$(dirname "$0")/windows/facebook_send_message.ahk"

if [[ ! -x "$AHK_EXE" ]]; then
  echo "AutoHotkey not found: $AHK_EXE" >&2
  exit 2
fi

"$AHK_EXE" "$AHK_SCRIPT" "$RECIPIENT" "$MESSAGE"
