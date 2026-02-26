# Task: Send Facebook message (owner account)

## Goal
Send a Messenger message end-to-end for Boss using profile `AutomatedAccount`.

## Inputs required
- Recipient name
- Message text

## Execution steps
1. Open Facebook in owner profile:
   - `scripts/open_facebook.sh`
2. If browser relay is not attached:
   - Ask Boss to click OpenClaw Browser Relay icon on current Chrome tab (badge ON).
3. Use browser automation to:
   - Open Messenger/search box
   - Search recipient
   - Open exact chat
   - Type message
   - Press Send
4. Confirm delivery result.

## Rules
- Default is execute directly, not tutorial.
- Ask follow-up only when recipient or message content is missing.
- If multiple people share same name, ask Boss to pick the correct one.
