#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 4 ]]; then
  echo "Usage: $0 <gmail_email> <gmail_password> <facebook_user> <facebook_password>"
  exit 1
fi

AHK_EXE="/mnt/c/Users/ADMIN/AppData/Local/Programs/AutoHotkey/v2/AutoHotkey64.exe"
AHK_SCRIPT="$(dirname "$0")/windows/login_google_facebook.ahk"

if [[ ! -x "$AHK_EXE" ]]; then
  echo "AutoHotkey not found: $AHK_EXE" >&2
  exit 2
fi

"$AHK_EXE" "$AHK_SCRIPT" "$1" "$2" "$3" "$4"
