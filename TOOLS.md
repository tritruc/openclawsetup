# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

### Desktop control (WSL host)

- Open any URL on Windows desktop from WSL:
  - `scripts/open_url.sh "https://example.com"`
- Open YouTube search directly on Windows desktop:
  - `scripts/open_youtube_search.sh "karaoke con bướm xinh"`
- Open URL in a specific Chrome profile (name or directory):
  - `scripts/open_chrome_profile_url.sh "https://example.com" "AutomatedAccount"`
- Open Gmail in owner profile:
  - `scripts/open_gmail.sh`
- Open Facebook in owner profile:
  - `scripts/open_facebook.sh`

Implementation uses:
- `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe`
- Command: `Start-Process '<url>'`

### Web accounts (owner preference)

- Primary Chrome profile for account actions: `AutomatedAccount` (directory: `Profile 4`)
- Gmail account in this profile: `manduongne3@gmail.com`
- Rule: all Gmail/Facebook actions should run inside this profile unless owner says otherwise.
- Facebook send-message automation primary mode: Chrome Relay (extension badge ON on attached tab).
- Fallback mode: AutoHotkey UI automation via `scripts/run_facebook_send_ahk.sh`.

### Automation engines (installed)

- Camoufox environment (workspace-local): `.venv-camoufox`
  - Smoke test: `source .venv-camoufox/bin/activate && python scripts/camoufox_smoke_test.py`
- AutoHotkey (Windows user install):
  - `/mnt/c/Users/ADMIN/AppData/Local/Programs/AutoHotkey/v2/AutoHotkey64.exe`
