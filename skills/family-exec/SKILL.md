---
name: family-exec
description: Execute owner-requested local machine tasks end-to-end on Windows/WSL (open URLs, YouTube search, Gmail/Facebook actions, and Facebook messaging). Use when user asks the assistant to DO the action directly instead of giving instructions.
---

# Family Exec

Execute tasks directly whenever safely possible.

## Priority behavior

1. Prefer **execution-first** (do the task), not tutorial answers.
2. Ask follow-up only when required:
   - missing target person
   - missing message content
   - OTP/CAPTCHA/2FA
   - browser relay tab not attached
3. Confirm completion clearly.

## Local machine actions

- Open URL: `scripts/open_url.sh "<url>"`
- YouTube search: `scripts/open_youtube_search.sh "<query>"`
- Gmail: `scripts/open_gmail.sh`
- Facebook: `scripts/open_facebook.sh`

## Account binding

- Default account profile: `AutomatedAccount` (Chrome dir `Profile 4`)
- Gmail/Facebook actions must use this profile unless user overrides.

## Facebook messaging flow

1. Open Facebook: `scripts/open_facebook.sh`
2. If Chrome Relay is not attached, request one-time attach:
   - User clicks OpenClaw Browser Relay icon on current Chrome tab until badge ON.
3. Use browser snapshot + act to:
   - find Messenger/search
   - open correct chat
   - type message
   - send
4. Return final status.

## References

- See `references/facebook-messaging-playbook.md` for deterministic click flow.
