#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <url> [profile_dir_or_profile_name]"
  exit 1
fi

URL="$1"
PROFILE_HINT="${2:-${OPENCLAW_CHROME_PROFILE:-AutomatedAccount}}"

POWERSHELL="/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
CHROME_WIN_PATH='C:\Program Files\Google\Chrome\Application\chrome.exe'
LOCAL_STATE='/mnt/c/Users/ADMIN/AppData/Local/Google/Chrome/User Data/Local State'
CHROME_USER_DATA_DIR='/mnt/c/Users/ADMIN/AppData/Local/Google/Chrome/User Data'

if [[ ! -x "$POWERSHELL" ]]; then
  echo "PowerShell not found at $POWERSHELL" >&2
  exit 2
fi

resolve_profile_dir() {
  local hint="$1"

  # If caller already passed a directory name like "Profile 4", use it directly when present.
  if [[ -d "$CHROME_USER_DATA_DIR/$hint" ]]; then
    echo "$hint"
    return 0
  fi

  # Otherwise try resolving by visible profile name from Local State (e.g. AutomatedAccount -> Profile 4).
  if [[ -f "$LOCAL_STATE" ]]; then
    local resolved
    resolved=$(HINT="$hint" python3 - <<'PY'
import json, os
hint=os.environ.get('HINT','')
path='/mnt/c/Users/ADMIN/AppData/Local/Google/Chrome/User Data/Local State'
try:
    with open(path,'r',encoding='utf-8') as f:
        data=json.load(f)
except Exception:
    print('')
    raise SystemExit
cache=(data.get('profile') or {}).get('info_cache') or {}
for d, info in cache.items():
    if (info.get('name') or '').strip().lower()==hint.strip().lower():
        print(d)
        break
else:
    print('')
PY
)
    if [[ -n "$resolved" && -d "$CHROME_USER_DATA_DIR/$resolved" ]]; then
      echo "$resolved"
      return 0
    fi
  fi

  return 1
}

if PROFILE_DIR=$(resolve_profile_dir "$PROFILE_HINT"); then
  :
else
  PROFILE_DIR='Profile 4'
fi

# Escape single quotes for PowerShell literal strings
PROFILE_ESC=${PROFILE_DIR//\'/\'\'}
URL_ESC=${URL//\'/\'\'}

# IMPORTANT: quote profile value because names like "Profile 4" contain spaces.
# Without this, Chrome may mis-parse and open stray tabs like http://0.0.0.4/
PS_CMD="\$p='$PROFILE_ESC'; \$u='$URL_ESC'; \$c='$CHROME_WIN_PATH'; \$args='--profile-directory=\"' + \$p + '\" --new-tab \"' + \$u + '\"'; Start-Process -FilePath \$c -ArgumentList \$args"
"$POWERSHELL" -NoProfile -Command "$PS_CMD"

echo "Opened in Chrome profile [$PROFILE_DIR] (hint: $PROFILE_HINT): $URL"
