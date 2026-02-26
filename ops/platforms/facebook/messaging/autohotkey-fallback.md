# AutoHotkey fallback for Facebook message send

## Purpose
Fallback path when Chrome Relay is unavailable.

## Command
- `scripts/run_facebook_send_ahk.sh "<recipient_name>" "<message>"`

## Notes
- This is UI-level best-effort automation (keyboard-driven), less reliable than DOM automation.
- Might fail if Facebook layout changes or popup captures focus.
- Use only when Relay path cannot be used.
