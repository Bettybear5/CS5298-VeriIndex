#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python3}"

echo "== VeriIndex reproducibility check =="
echo "repo:   $ROOT"
echo "python: $($PYTHON --version)"

cd "$ROOT/reference"
$PYTHON -m pip install -e . --quiet
$PYTHON -m pytest -q
$PYTHON -m veriindex.cli demo
$PYTHON -m veriindex.cli evaluate --evidence-dir "$ROOT/report/evidence"

echo
echo "PASS: reference tests, demo, and offline evaluation completed."
