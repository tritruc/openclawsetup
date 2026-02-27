@echo off
setlocal

REM Open Ubuntu terminal on Windows login, then start OpenClaw services.
set "DISTRO=Ubuntu"
set "WSL_BOOT_CMD=cd /home/manduong/.openclaw/workspace; export PATH=$HOME/.nvm/current/bin:$HOME/.local/bin:$PATH; (systemctl --user start openclaw-gateway.service || ~/.nvm/versions/node/v24.13.1/bin/openclaw gateway start || true); systemctl --user start zalo-reminder-manager.service >/dev/null 2>&1 || true; echo.; echo [OpenClaw] Startup done. Dashboard: http://127.0.0.1:18789 ; exec bash"

REM Avoid Windows Terminal quote parsing issues by launching wsl.exe directly.
start "OpenClaw Ubuntu" /D C:\Windows\System32 wsl.exe -d %DISTRO% -- bash -lc "%WSL_BOOT_CMD%"

endlocal
