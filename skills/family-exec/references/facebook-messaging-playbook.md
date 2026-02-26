# Facebook Messaging Playbook (Relay)

Use this when user asks to send a Messenger message.

## Inputs
- recipient name
- message body

## Deterministic flow
1. Ensure Facebook is open via `scripts/open_facebook.sh`.
2. Use browser profile `chrome`.
3. If no tab attached: stop and ask user to attach relay icon (badge ON).
4. Snapshot (prefer refs=aria when needed), then:
   - click Search/Messenger search box
   - type recipient name
   - select matching conversation
   - click message input
   - type full message
   - press Enter or click Send
5. Validate message bubble appears.
6. Report success.

## Failure handling
- Multiple people with same name: ask user to confirm exact profile.
- Input box not visible: reopen conversation and retry once.
- Relay detached mid-flow: ask user to reattach, then continue.
