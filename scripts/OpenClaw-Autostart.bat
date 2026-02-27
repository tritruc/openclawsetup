@echo off
setlocal

REM Open Ubuntu terminal on Windows login, then start OpenClaw services.
set "DISTRO=Ubuntu"
set "WSL_BOOT_CMD=export PATH=\"$HOME/.nvm/current/bin:$HOME/.local/bin:$PATH\"; cd /home/manduong/.openclaw/workspace; (systemctl --user start openclaw-gateway.service || ~/.nvm/versions/node/v24.13.1/bin/openclaw gateway start || true); systemctl --user start zalo-reminder-manager.service >/dev/null 2>&1 || true; echo.; echo [OpenClaw] Startup done. Dashboard: http://127.0.0.1:18789 ; exec bash"

if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe" (
  start "OpenClaw Ubuntu" "%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe" -w 0 new-tab --title "OpenClaw Ubuntu" wsl.exe -d %DISTRO% -- bash -lc "%WSL_BOOT_CMD%"
) else (
  start "OpenClaw Ubuntu" wsl.exe -d %DISTRO% -- bash -lc "%WSL_BOOT_CMD%"
)

endlocal
