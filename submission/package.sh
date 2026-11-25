#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEMO="${1:-$ROOT/demo/CS5298_VeriIndex_Demo.mp4}"
OUT="$ROOT/submission/CS5298_VeriIndex_Demo.zip"

if [[ ! -f "$DEMO" ]]; then
  echo "Demo recording not found: $DEMO" >&2
  echo "Record the 8-minute demo first and place it there." >&2
  exit 1
fi
if [[ ! -s "$DEMO" ]]; then
  echo "Demo recording is empty: $DEMO" >&2
  exit 1
fi
if grep -q '\[TBD\]' "$ROOT/report/report.md"; then
  echo "report/report.md still contains [TBD] placeholders." >&2
  echo "Fill them before packaging." >&2
  exit 1
fi

rm -f "$OUT"
(
  cd "$(dirname "$DEMO")"
  zip -j "$OUT" "$(basename "$DEMO")"
)
echo "wrote $OUT"
