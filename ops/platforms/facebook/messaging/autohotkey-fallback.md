# AutoHotkey fallback for Facebook message send

## Purpose
Fallback path when Chrome Relay is unavailable.

## Command
- `scripts/run_facebook_send_ahk.sh "<recipient_name>" "<message>"`

## Notes
- This is UI-level best-effort automation, less reliable than DOM automation.
- Current script attempts to dismiss PIN-recovery modal with `Esc` and then continue search/send flow.
- Might still fail if Facebook layout changes significantly.
- Use only when Relay path cannot be used.
