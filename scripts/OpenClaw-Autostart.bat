@echo off
setlocal

REM Windows startup -> open Ubuntu -> run OpenClaw TUI bound to Telegram session.
set "DISTRO=Ubuntu"
set "WSL_CMD=cd /home/manduong/.openclaw/workspace; /home/manduong/.openclaw/workspace/scripts/autostart_openclaw_tui.sh"

start "OpenClaw TUI (Telegram)" /D C:\Windows\System32 wsl.exe -d %DISTRO% -- bash -lc "%WSL_CMD%"

endlocal
