@echo off
cd /d C:\
REM Auto-start OpenClaw Gateway on Windows login via WSL Ubuntu
wsl.exe -d Ubuntu -- bash -lc "systemctl --user start openclaw-gateway.service"
