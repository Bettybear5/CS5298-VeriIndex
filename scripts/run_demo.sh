#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python3}"

cd "$ROOT/reference"
$PYTHON -m pip install -e . --quiet
$PYTHON -m veriindex.cli demo
