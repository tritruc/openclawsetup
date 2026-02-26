#!/usr/bin/env bash
set -euo pipefail

# Defaults to profile name AutomatedAccount (resolved to profile dir internally)
"$(dirname "$0")/open_chrome_profile_url.sh" "https://mail.google.com/" "${OPENCLAW_CHROME_PROFILE:-AutomatedAccount}"
