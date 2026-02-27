#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: $0 <phone> <message>"
  exit 1
fi

PHONE="$1"
MESSAGE="$2"
cp /home/manduong/.openclaw/workspace/scripts/windows/zalo_send_message.ps1 /mnt/c/Users/ADMIN/AppData/Local/Temp/zalo_send_message.ps1

/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Users\ADMIN\AppData\Local\Temp\zalo_send_message.ps1" -Phone "$PHONE" -Message "$MESSAGE"

echo "Screenshots:"
echo "- /mnt/c/Users/ADMIN/AppData/Local/Temp/zalo_after_search.png"
echo "- /mnt/c/Users/ADMIN/AppData/Local/Temp/zalo_before_send.png"
echo "- /mnt/c/Users/ADMIN/AppData/Local/Temp/zalo_after_send.png"
