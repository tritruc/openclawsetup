#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <phone> [ack_text]"
  exit 1
fi

PHONE="$1"
ACK_TEXT="${2:-ok}"
OUT_WIN='C:\Users\ADMIN\AppData\Local\Temp\zalo_chat_capture.png'
OUT_WSL='/mnt/c/Users/ADMIN/AppData/Local/Temp/zalo_chat_capture.png'

cp /home/manduong/.openclaw/workspace/scripts/windows/zalo_capture_chat.ps1 /mnt/c/Users/ADMIN/AppData/Local/Temp/zalo_capture_chat.ps1
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Users\ADMIN\AppData\Local\Temp\zalo_capture_chat.ps1" -Phone "$PHONE" -OutPath "$OUT_WIN" >/dev/null

node /home/manduong/.openclaw/workspace/scripts/ocr_ack_check.js "$OUT_WSL" "$ACK_TEXT"