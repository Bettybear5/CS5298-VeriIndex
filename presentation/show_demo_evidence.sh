#!/usr/bin/env bash
# Replay recorded demo evidence from GitHub Actions run 45728324966.
# This is NOT a live devnet run. Say that explicitly in the recording.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
A="$ROOT/demo_assets"

echo "============================================================"
echo " RECORDED EVIDENCE ONLY"
echo " GitHub Actions run 45728324966"
echo " Single-node Lyquor devnet"
echo "============================================================"
echo

echo "== Deployment =="
cat "$A/deploy.json"
echo

echo "== Indexed range =="
cat "$A/range.txt"
echo

echo "== RPC used =="
cat "$A/rpc-used.txt"
echo

echo "== submit_result transaction =="
cat "$A/submit-tx.txt"
echo

echo "== get_result_count =="
cat "$A/result-count.txt"
echo

echo "== has_result =="
cat "$A/has-result.txt"
echo

echo "== get_result JSON =="
python3 - "$A/result.json" <<'PY'
import json, sys
text = open(sys.argv[1], encoding="utf-8").read().strip()
data = json.loads(text)
if isinstance(data, str):
    data = json.loads(data)
print(json.dumps(data, indent=2, ensure_ascii=False))
PY
echo

echo "== submit_result receipt =="
grep -E '^(status|transactionHash|blockNumber)' "$A/submit.log"
