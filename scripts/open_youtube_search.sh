#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <search terms>"
  exit 1
fi

QUERY="$*"
ENCODED=$(python3 - "$QUERY" <<'PY'
import sys, urllib.parse
print(urllib.parse.quote_plus(sys.argv[1]))
PY
)
URL="https://www.youtube.com/results?search_query=${ENCODED}"

"$(dirname "$0")/open_url.sh" "$URL"
