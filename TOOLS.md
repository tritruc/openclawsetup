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

Implementation uses:
- `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe`
- Command: `Start-Process '<url>'`
