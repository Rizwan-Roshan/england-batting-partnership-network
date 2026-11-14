#!/bin/bash
# Stage 9b: print report/report.html to PDF with headless Google Chrome (macOS).
# Page rules (A4, 3 cm margins, 12 pt Times, single spacing) are set in the HTML.
# The PDF name follows the course rule: surnames in alphabetical order joined by "and".
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
NAME="$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['pdf_name'])" "$ROOT/report/authors.json")"
OUT="$ROOT/report/$NAME.pdf"
"$CHROME" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="$OUT" \
  "file://$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$ROOT/report/report.html")" 2>/dev/null
echo "wrote $OUT"
