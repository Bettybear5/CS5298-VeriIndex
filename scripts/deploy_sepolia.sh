#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/contracts"

: "${SEPOLIA_RPC_URL:?set SEPOLIA_RPC_URL in the environment}"
: "${PRIVATE_KEY:?set PRIVATE_KEY in the environment}"

# Requires Foundry and forge-std:
#   forge install foundry-rs/forge-std
forge script script/Deploy.s.sol \
  --rpc-url "$SEPOLIA_RPC_URL" \
  --broadcast \
  -vvv
