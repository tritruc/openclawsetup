# Camoufox evaluation for Facebook task automation

## Objective
Assess whether Camoufox can replace Chrome Relay attachment requirement for end-to-end automation.

## Findings
- Camoufox works and is installable in workspace venv.
- It is Firefox-based (separate browser profile), so it does **not** directly reuse logged-in Chrome profile `AutomatedAccount`.
- Therefore, it cannot immediately continue existing Chrome session without a one-time login/cookie migration.

## Decision
- Keep Chrome + Relay as primary for current account continuity.
- Keep Camoufox as optional secondary engine when owner accepts dedicated automation profile/login.
